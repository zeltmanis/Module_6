import sys
from config import Config
from simulation import Simulation
from models import (
    FlatMonthly,
    YearlySubscription,
    PremiumMonthly,
    PremiumYearlySubscription,
)
from visualization import plot_combined
from database import save_to_db, summarize_db
from price_optimizer import test_price_range


def main():
    # Load config
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config.json"

    cfg = Config(config_path)
    cfg.summary()

    # Pricing models to compare
    models = {
        "Standard Monthly": FlatMonthly(),
        "Standard Yearly": YearlySubscription(),
        "Premium Monthly": PremiumMonthly(),
        "Premium Yearly": PremiumYearlySubscription(),
    }

    results = {}
    db_results = {}

    for name, model in models.items():
        sim = Simulation(cfg, model)
        stats = sim.run_once()

        results[name] = {
            "profits": stats["profits"],
            "users": stats["users"],
        }

        db_results[name] = stats

        print(f"\n{name}")
        print(f"  Final Users: {stats['final_users']}")
        print(f"  Final Month Profit: {stats['profits'][-1]:.2f}")

    print("-------------------------------")

    print("\n=== PRICE OPTIMIZATION RESULTS ===")

    price_tests = {
        "Standard Monthly": ("monthly_price", [60, 70, 80, 90, 100, 120]),
        "Standard Yearly": ("monthly_price", [60, 70, 80, 90, 100, 120]),
        "Premium Monthly": ("premium_monthly_price", [100, 110, 120, 130, 140]),
        "Premium Yearly": ("premium_monthly_price", [100, 110, 120, 130, 140]),
    }

    for name, model in models.items():
        price_key, price_values = price_tests[name]

        best_profit, best_users, all_results = test_price_range(
            model.__class__, cfg, price_key, price_values
        )

        print(f"\n{name}")
        print(f"  Best Price (Profit): {best_profit['price']} → Profit {best_profit['profit']:.2f}")
        print(f"  Best Price (Users):  {best_users['price']} → Users  {best_users['users']}")

    # Plot graphs
    plot_combined(results, cfg.get("months"))

    # Save to DB
    save_to_db(db_results)

    # Summarize
    summarize_db()


if __name__ == "__main__":
    main()
