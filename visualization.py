import matplotlib.pyplot as plt
import numpy as np

def plot_results(results, months, deviations=None):
    plt.figure(figsize=(10, 6))
    x = np.arange(1, months + 1)

    for label, profits in results.items():
        plt.plot(x, profits, label=label, linewidth=2)
        if deviations and label in deviations:
            std = deviations[label]
            plt.fill_between(x, profits - std, profits + std, alpha=0.2)

    plt.title("Multiple Run Simulation: Profit Comparison (Mean ± Std)", fontsize=14)
    plt.xlabel("Month")
    plt.ylabel("Profit (relative units)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()
