import sys
from analytics import summarize_db
from config import Config
from models import FlatMonthly, YearlySubscription, UsageBased, TieredPricing
from simulation import Simulation
from visualization import plot_results
from database import save_to_db


def main():
    # ✅ 1. Choose config dynamically from command line
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "configs/config_streaming.json"

    cfg = Config(config_path)
    cfg.summary()

    # ✅ 2. Define pricing models to compare
    models = {
        "Flat Monthly": FlatMonthly(),
        "Yearly Subscription": YearlySubscription(),
        "Usage-Based": UsageBased(),
        "Tiered Pricing": TieredPricing(),
    }

    results = {}        # for plotting profit curves
    summary = {}        # for printing summary metrics
    model_stats = {}    # for saving to database

    # ✅ 3. Run simulations for each model once
    for name, model in models.items():
        sim = Simulation(cfg, model)
        stats = sim.multi_run(runs=200)

        # Store simulation results
        results[name] = stats["mean_profit"]
        model_stats[name] = stats  # full data for database

        # Store summary metrics
        summary[name] = {
            "Revenue Growth": round(stats["revenue_growth"], 3),
            "Satisfaction": round(stats["satisfaction"], 3),
            "Fairness": round(stats["fairness"], 3),
        }

    # ✅ 4. Plot simulation outcomes
    plot_results(results, cfg.get("months"))

    # ✅ 5. Print summary metrics
    print("\n--- Model Summary ---")
    for name, metrics in summary.items():
        print(f"\n{name}")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    print("----------------------\n")

    # ✅ 6. Save all results to SQLite database
    save_to_db(model_stats)
    summarize_db()


if __name__ == "__main__":
    main()
