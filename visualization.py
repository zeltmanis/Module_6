import matplotlib.pyplot as plt

def plot_results(results, months):
    plt.figure(figsize=(10,6))
    for label, profits in results.items():
        plt.plot(range(1, months+1), profits, label=label, linewidth=2)
    plt.title("Profit Comparison Across Pricing Models")
    plt.xlabel("Month")
    plt.ylabel("Profit")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()