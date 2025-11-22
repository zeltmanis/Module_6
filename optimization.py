"""
Price optimization utilities for user growth and profit objectives.

Strategy:
- Use the user forecaster to get the trend-based expected next users.
- Use price elasticity to adjust that forecast when trying new prices.
- Use the cost forecaster to estimate infra load and cost.
- Score each candidate price for different objectives.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

from forecaster_user import forecast_next_active_users, PriceElasticityModel
from forecaster_cost import (
    forecast_total_usage_over_horizon,
    compute_expected_cost,
)


Objective = Literal["user_growth", "profit", "hybrid"]


@dataclass
class PriceOptionResult:
    price: float
    predicted_users: float
    user_growth: float
    revenue: float
    expected_usage: float
    expected_cost: float
    profit: float
    score: float
    diagnostics: Dict[str, object]


def _combine_trend_and_price_effect(
    trend_next_users: float,
    current_users: float,
    elasticity_predicted_users: float,
) -> float:
    """
    Scale the trend forecast by the elasticity implied user ratio.
    Keeps the trend signal while incorporating price sensitivity.
    """
    if current_users <= 0:
        return max(trend_next_users, 0.0)

    ratio = elasticity_predicted_users / current_users
    return max(trend_next_users * ratio, 0.0)


def evaluate_price_option(
    new_price: float,
    *,
    current_price: float,
    historical_users: List[float],
    elasticity_model: PriceElasticityModel,
    avg_requests_per_user: float,
    cost_per_request: float,
    coverage_prob: float = 0.99,
) -> PriceOptionResult:
    """
    Evaluate a single price point and return detailed metrics.
    """
    if len(historical_users) < 1:
        raise ValueError("historical_users must contain at least one value.")

    current_users = historical_users[-1]

    trend_next_users, trend_diag = forecast_next_active_users(historical_users)
    elasticity_res = elasticity_model.predict_users(
        current_price=current_price,
        new_price=new_price,
        current_users=current_users,
    )

    # Blend baseline trend with price-driven elasticity adjustment
    predicted_users = _combine_trend_and_price_effect(
        trend_next_users=trend_next_users,
        current_users=current_users,
        elasticity_predicted_users=elasticity_res["predicted_users"],
    )

    user_growth = predicted_users - current_users
    revenue = new_price * predicted_users

    expected_usage, usage_diag = forecast_total_usage_over_horizon(
        forecasted_users_list=[predicted_users],
        avg_requests_per_user=avg_requests_per_user,
        coverage_prob=coverage_prob,
    )
    expected_cost = compute_expected_cost(
        total_expected_requests=expected_usage,
        cost_per_request=cost_per_request,
    )
    profit = revenue - expected_cost

    diagnostics = {
        "trend": trend_diag,
        "elasticity": elasticity_res,
        "usage": usage_diag,
    }

    # Score is filled by optimize_price once objective is chosen
    return PriceOptionResult(
        price=new_price,
        predicted_users=predicted_users,
        user_growth=user_growth,
        revenue=revenue,
        expected_usage=expected_usage,
        expected_cost=expected_cost,
        profit=profit,
        score=0.0,
        diagnostics=diagnostics,
    )


def optimize_price(
    price_grid: List[float],
    *,
    current_price: float,
    historical_users: List[float],
    elasticity_model: PriceElasticityModel,
    avg_requests_per_user: float,
    cost_per_request: float,
    objective: Objective = "profit",
    hybrid_weight_growth: float = 0.5,
    coverage_prob: float = 0.99,
) -> Tuple[PriceOptionResult, List[PriceOptionResult]]:
    """
    Evaluate a grid of prices and return the best option plus all evaluations.

    objective:
        - "user_growth": maximize predicted users
        - "profit": maximize profit
        - "hybrid": weighted sum of normalized growth and profit

    hybrid_weight_growth:
        Weight for growth in the hybrid score (0..1). Profit gets (1 - weight).
    """
    if not 0 <= hybrid_weight_growth <= 1:
        raise ValueError("hybrid_weight_growth must be between 0 and 1.")

    evaluated: List[PriceOptionResult] = []
    for p in price_grid:
        res = evaluate_price_option(
            new_price=p,
            current_price=current_price,
            historical_users=historical_users,
            elasticity_model=elasticity_model,
            avg_requests_per_user=avg_requests_per_user,
            cost_per_request=cost_per_request,
            coverage_prob=coverage_prob,
        )
        evaluated.append(res)

    max_users = max(r.predicted_users for r in evaluated) or 1.0
    profits = [r.profit for r in evaluated]
    max_profit = max(profits) if profits else 1.0
    min_profit = min(profits) if profits else 0.0
    profit_range = max(max_profit - min_profit, 1e-9)

    def score_fn(res: PriceOptionResult) -> float:
        if objective == "user_growth":
            return res.predicted_users
        if objective == "profit":
            return res.profit
        if objective == "hybrid":
            growth_score = res.predicted_users / max_users
            profit_score = (res.profit - min_profit) / profit_range
            return hybrid_weight_growth * growth_score + (1 - hybrid_weight_growth) * profit_score
        raise ValueError(f"Unsupported objective '{objective}'.")

    for res in evaluated:
        res.score = score_fn(res)

    best = max(evaluated, key=lambda r: r.score)
    return best, evaluated


def optimize_profit(
    price_grid: List[float],
    *,
    current_price: float,
    historical_users: List[float],
    elasticity_model: PriceElasticityModel,
    avg_requests_per_user: float,
    cost_per_request: float,
    coverage_prob: float = 0.99,
) -> Tuple[PriceOptionResult, List[PriceOptionResult]]:
    """
    Convenience wrapper to optimize purely for profit.
    """
    return optimize_price(
        price_grid=price_grid,
        current_price=current_price,
        historical_users=historical_users,
        elasticity_model=elasticity_model,
        avg_requests_per_user=avg_requests_per_user,
        cost_per_request=cost_per_request,
        objective="profit",
        coverage_prob=coverage_prob,
    )


def optimize_user_growth(
    price_grid: List[float],
    *,
    current_price: float,
    historical_users: List[float],
    elasticity_model: PriceElasticityModel,
    avg_requests_per_user: float,
    cost_per_request: float,
    coverage_prob: float = 0.99,
) -> Tuple[PriceOptionResult, List[PriceOptionResult]]:
    """
    Convenience wrapper to optimize purely for user growth (predicted users).
    """
    return optimize_price(
        price_grid=price_grid,
        current_price=current_price,
        historical_users=historical_users,
        elasticity_model=elasticity_model,
        avg_requests_per_user=avg_requests_per_user,
        cost_per_request=cost_per_request,
        objective="user_growth",
        coverage_prob=coverage_prob,
    )


def summarize_objectives(results: Dict[str, PriceOptionResult]) -> None:
    """
    Print a quick comparison of best options for each objective.
    """
    print("\n--- Objective Comparison ---")
    for label, res in results.items():
        print(
            f"{label:20s} | price={res.price:6.2f} | users={res.predicted_users:8.1f} | profit={res.profit:10.2f}"
        )


if __name__ == "__main__":
    # Example usage with dummy data; replace with real histories.
    historical_users = [1000, 1100, 1200, 1350, 1500]
    current_price = 10.0
    price_candidates = [8, 9, 10, 11, 12, 14]

    # Fit a simple elasticity model from synthetic pairs
    elasticity_model = PriceElasticityModel()
    elasticity_model.fit(
        prices=[9, 10, 11, 10, 12, 9],
        users=[1200, 1100, 1000, 1150, 900, 1300],
    )

    best_option, all_results = optimize_price(
        price_grid=price_candidates,
        current_price=current_price,
        historical_users=historical_users,
        elasticity_model=elasticity_model,
        avg_requests_per_user=3.0,
        cost_per_request=0.02,
        objective="hybrid",
        hybrid_weight_growth=0.6,
    )

    print(f"Best price: {best_option.price:.2f}")
    print(f"Predicted users: {best_option.predicted_users:.1f}")
    print(f"Expected profit: {best_option.profit:.2f}")

    # Pure profit objective
    best_profit, _ = optimize_profit(
        price_grid=price_candidates,
        current_price=current_price,
        historical_users=historical_users,
        elasticity_model=elasticity_model,
        avg_requests_per_user=3.0,
        cost_per_request=0.02,
    )
    print(f"Profit-optimal price: {best_profit.price:.2f}")

    # Pure user growth objective
    best_growth, _ = optimize_user_growth(
        price_grid=price_candidates,
        current_price=current_price,
        historical_users=historical_users,
        elasticity_model=elasticity_model,
        avg_requests_per_user=3.0,
        cost_per_request=0.02,
    )
    print(f"User-growth-optimal price: {best_growth.price:.2f}")

    summarize_objectives(
        {
            "Hybrid (growth/profit)": best_option,
            "Profit only": best_profit,
            "User growth only": best_growth,
        }
    )
