import numpy as np

def revenue_growth_curve(revenues):
    """Average revenue growth rate over time (normalized to 0–1)."""
    revenues = np.array(revenues, dtype=float)  # ensure NumPy array
    if len(revenues) < 2 or np.all(revenues == 0):
        return 0
    growth_rates = np.diff(revenues) / (revenues[:-1] + 1e-9)
    avg_growth = np.clip(np.mean(growth_rates), -1, 1)
    return (avg_growth + 1) / 2  # normalize to 0–1 range


def customer_satisfaction(price, churn_rate, base_price=10):
    """
    Estimate satisfaction based on churn and perceived price fairness.
    Higher churn or excessive pricing reduces satisfaction.
    """
    base = max(0, 1 - churn_rate)  # churn inverse
    price_penalty = max(0, (price / base_price) - 1) * 0.5
    return np.clip(base - price_penalty, 0, 1)


def fairness_metric(user_usages, user_prices):
    """
    Measures fairness: how consistent profit is across users.
    Uses coefficient of variation (std/mean) as inequality measure.
    """
    user_usages = np.array(user_usages)
    user_prices = np.array(user_prices)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.divide(user_prices, user_usages, out=np.zeros_like(user_prices), where=user_usages != 0)
    inequality = np.std(ratios) / (np.mean(ratios) + 1e-9)
    fairness = 1 - np.clip(inequality, 0, 1)
    return fairness
