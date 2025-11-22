import numpy as np
from simulation import Simulation

def test_price_range(model_class, cfg, price_key, price_values):
    """
    Runs simulations for different prices and finds:
      - profit-maximizing price
      - user-maximizing price

    model_class: (e.g., FlatMonthly)
    cfg: Config instance
    price_key: the parameter in config.json, e.g. "monthly_price", "premium_monthly_price"
    price_values: list of prices to test
    """

    results = []

    for p in price_values:
        cfg.params[price_key] = p  # override the price dynamically

        sim = Simulation(cfg, model_class())
        stats = sim.run_once()

        final_profit = stats["profits"][-1]
        final_users = stats["final_users"]

        results.append({
            "price": p,
            "profit": final_profit,
            "users": final_users,
        })

    # find best
    best_profit = max(results, key=lambda x: x["profit"])
    best_users = max(results, key=lambda x: x["users"])

    return best_profit, best_users, results
