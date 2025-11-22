import math
from typing import List, Dict, Any, Tuple

def poisson_pmf(k: int, lam: float) -> float:
    """Poisson probability P(N = k) for integer k >= 0 and rate lam > 0 (uses log-space for stability)."""
    if k < 0:
        return 0.0
    if lam == 0:
        return 1.0 if k == 0 else 0.0

    # log pmf to avoid overflow: log p = -lam + k*log(lam) - log(k!)
    log_p = -lam + k * math.log(lam) - math.lgamma(k + 1)
    return math.exp(log_p)

def poisson_cdf(k: int, lam: float) -> float:
    """Poisson cumulative probability P(N <= k)."""
    if k < 0:
        return 0.0
    total = 0.0
    for i in range(0, k + 1):
        total += poisson_pmf(i, lam)
    return total

def forecast_server_load_one_step(
    forecasted_users: float,
    avg_requests_per_user: float,
    coverage_prob: float = 0.99
) -> Tuple[float, Dict[str, Any]]:
    """
    Forecast server load for a single time step, using a Poisson model.

    Returns:
        expected_load: scalar load for this step (objective-friendly)
        diagnostics: full metadata (lambda, pmf table, capacity, coverage)
    """
    U = float(forecasted_users)
    r = float(avg_requests_per_user)

    if U < 0:
        raise ValueError("forecasted_users cannot be negative.")
    if r < 0:
        raise ValueError("avg_requests_per_user cannot be negative.")

    lam = U * r  # Poisson rate parameter

    # Range around lambda for PMF inspection
    std = math.sqrt(lam) if lam > 0 else 0.0
    k_min = max(0, int(math.floor(lam - 4 * std)))
    k_max = max(0, int(math.floor(lam + 4 * std)))

    pmf_table = []
    for k in range(k_min, k_max + 1):
        p = poisson_pmf(k, lam)
        pmf_table.append((k, p))

    # Find capacity C such that P(N <= C) >= coverage_prob
    C = 0
    cdf_val = 0.0
    upper_bound = int(lam * 10 + 1000) if lam > 0 else 1000
    while C <= upper_bound:
        cdf_val = poisson_cdf(C, lam)
        if cdf_val >= coverage_prob:
            break
        C += 1

    diagnostics = {
        "lambda": lam,
        "expected_load": lam,  # this is the expected usage for this time step
        "pmf_table": pmf_table,
        "capacity_for_coverage": C,
        "coverage_probability": coverage_prob
    }

    return lam, diagnostics

def forecast_total_usage_over_horizon(
    forecasted_users_list: List[float],
    avg_requests_per_user: float,
    coverage_prob: float = 0.99
) -> Tuple[float, Dict[str, Any]]:
    """
    Takes a list of forecasted user counts over multiple time steps, and:
      - computes Poisson parameters per step
      - computes expected load per step
      - sums expected loads to get TOTAL USAGE (area under the curve).

    Returns:
      - total_expected_usage: scalar, can feed profit optimization
      - diagnostics: per-step details and configuration
    """
    per_step_results = []
    total_expected_usage = 0.0

    for t, U_t in enumerate(forecasted_users_list):
        expected_load, step_res = forecast_server_load_one_step(
            forecasted_users=U_t,
            avg_requests_per_user=avg_requests_per_user,
            coverage_prob=coverage_prob
        )
        step_res["time_index"] = t  # optional: label the step
        per_step_results.append(step_res)
        total_expected_usage += expected_load

    diagnostics = {
        "per_step": per_step_results,
        "coverage_probability": coverage_prob,
        "avg_requests_per_user": avg_requests_per_user,
    }

    # Tuple so optimizers can use the scalar directly while retaining detail
    return total_expected_usage, diagnostics

# Example usage (connecting to your user forecast output):
if __name__ == "__main__":
    # Suppose your user-forecast model (binomial + Taylor + elasticity)
    # gave you the following expected users for the next 5 time steps:
    forecasted_users_horizon = [150, 160, 155, 170, 165]

    # Assume each user makes on average 3 requests per time window
    avg_requests_per_user = 3.0

    total_usage, debug = forecast_total_usage_over_horizon(
        forecasted_users_list=forecasted_users_horizon,
        avg_requests_per_user=avg_requests_per_user,
        coverage_prob=0.99
    )

def compute_expected_cost(total_expected_requests, cost_per_request):
    """
    Compute expected infrastructure cost.

    total_expected_requests : float
        Total expected number of requests (e.g. from Poisson forecast).

    cost_per_request : float
        Cost of serving a single request.

    Returns:
        float: expected total cost.
    """
    if total_expected_requests < 0:
        raise ValueError("total_expected_requests cannot be negative.")
    if cost_per_request < 0:
        raise ValueError("cost_per_request cannot be negative.")

    return total_expected_requests * cost_per_request

   
