import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# COMBINED SIMULATION PLOT (Profit & Users over 24 months)
# ---------------------------------------------------------

def plot_combined(results, months):
    """
    results = {
        "Standard Monthly": {"profits": [...], "users": [...]},
        ...
    }
    """

    x = np.arange(1, months + 1)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # ---- PROFIT ----
    axes[0].set_title("Profit Over Time")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Profit")

    for label, data in results.items():
        axes[0].plot(x, data["profits"], label=label, linewidth=2)

    axes[0].grid(True, linestyle="--", alpha=0.6)
    axes[0].legend()

    # ---- USERS ----
    axes[1].set_title("Users Over Time")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Users")

    for label, data in results.items():
        axes[1].plot(x, data["users"], label=label, linewidth=2)

    axes[1].grid(True, linestyle="--", alpha=0.6)
    axes[1].legend()

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------
# PRICE OPTIMIZATION PLOTS
# ---------------------------------------------------------

def plot_price_results(model_name, results):
    """
    Plot Profit vs Price and Users vs Price for a single subscription type.

    results = list of dicts:
        [{"price": p, "profit": X, "users": Y}, ...]
    """

    prices = [r["price"] for r in results]
    profits = [r["profit"] for r in results]
    users = [r["users"] for r in results]

    plt.figure(figsize=(12, 5))

    # ---- Profit vs Price ----
    plt.subplot(1, 2, 1)
    plt.plot(prices, profits, marker="o", linewidth=2)
    plt.title(f"Profit vs Price — {model_name}")
    plt.xlabel("Price")
    plt.ylabel("Profit")
    plt.grid(True, linestyle="--", alpha=0.6)

    # ---- Users vs Price ----
    plt.subplot(1, 2, 2)
    plt.plot(prices, users, marker="o", linewidth=2)
    plt.title(f"Users vs Price — {model_name}")
    plt.xlabel("Price")
    plt.ylabel("Users")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.show()
