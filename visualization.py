import matplotlib.pyplot as plt
import numpy as np

def plot_combined(all_results, months):
    """
    all_results = {
        "Standard Monthly": {"profits": [...], "users": [...], ...},
        "Premium Monthly": {...},
        ...
    }
    """
    x = np.arange(1, months + 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Users over time
    for label, data in all_results.items():
        axes[0].plot(x, data["users"], label=label, linewidth=2)

    axes[0].set_title("Users Over Time (All Plans)")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Users")
    axes[0].grid(True, linestyle="--", alpha=0.6)

    # Profits over time
    for label, data in all_results.items():
        axes[1].plot(x, data["profits"], label=label, linewidth=2)

    axes[1].set_title("Profit Over Time (All Plans)")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Profit")
    axes[1].grid(True, linestyle="--", alpha=0.6)

    fig.legend(loc="upper center", ncol=4)
    plt.tight_layout()
    plt.show()
