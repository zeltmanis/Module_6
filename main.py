import sys
from config import Config
from models import FlatMonthly, YearlySubscription, UsageBased
from simulation import Simulation
from visualization import plot_results

def main():
    # Choose config dynamically
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Default: streaming scenario
        config_path = "configs/config_streaming.json"

    cfg = Config(config_path)
    cfg.summary()

    # Define pricing models
    models = {
        "Flat Monthly": FlatMonthly(),
        "Yearly Subscription": YearlySubscription(),
        "Usage-Based": UsageBased(),
    }

    # Run simulations
    results = {}
    for name, model in models.items():
        sim = Simulation(cfg, model)
        results[name] = sim.run(seed=42)

    # Visualize results
    plot_results(results, cfg.get("months"))

if __name__ == "__main__":
    main()
