import sys
from config import Config
from models import FlatMonthly, YearlySubscription, UsageBased
from simulation import Simulation
from visualization import plot_results

def main():
    # ✅ Choose config dynamically from command line
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "configs/config_streaming.json"

    cfg = Config(config_path)
    cfg.summary()

    models = {
        "Flat Monthly": FlatMonthly(),
        "Yearly Subscription": YearlySubscription(),
        "Usage-Based": UsageBased(),
    }

    results = {}
    summary = {}

    for name, model in models.items():
        sim = Simulation(cfg, model)
        stats = sim.multi_run(runs=200)
        results[name] = stats["mean_profit"]
        summary[name] = {
            "Revenue Growth": round(stats["revenue_growth"], 3),
            "Satisfaction": round(stats["satisfaction"], 3),
            "Fairness": round(stats["fairness"], 3),
        }

    plot_results(results, cfg.get("months"))

    print("\n--- Model Summary ---")
    for name, metrics in summary.items():
        print(f"\n{name}")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    print("----------------------\n")

if __name__ == "__main__":
    main()
