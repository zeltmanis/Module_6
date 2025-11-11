from config import Config
from models import FlatMonthly, YearlySubscription, UsageBased
from simulation import Simulation
from visualization import plot_results

def main():
    cfg = Config()
    models = {
        "Flat Monthly": FlatMonthly(),
        "Yearly": YearlySubscription(),
        "Usage-Based": UsageBased(),
    }

    results = {}
    for name, model in models.items():
        sim = Simulation(cfg, model)
        results[name] = sim.run()

    plot_results(results, cfg.get("months"))

if __name__ == "__main__":
    main()