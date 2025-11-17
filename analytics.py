import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def summarize_db(db_name="simulation_results.db"):
    """Show average monthly profit and revenue for each model."""
    conn = sqlite3.connect(db_name)
    df = pd.read_sql("SELECT model, AVG(mean_profit) as avg_profit, AVG(mean_revenue) as avg_revenue FROM results GROUP BY model", conn)
    conn.close()

    print("\n--- Historical Averages from Database ---")
    print(df)
    print("------------------------------------------\n")

    # Optional: visualize the comparison
    df.plot(kind="bar", x="model", y=["avg_profit", "avg_revenue"], figsize=(8, 5))
    plt.title("Average Profit and Revenue per Model (Historical)")
    plt.ylabel("Value")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()
