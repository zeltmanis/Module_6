import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def summarize_db(db_name="simulation_results.db"):
    """Print and graph average profit and users per model."""

    conn = sqlite3.connect(db_name)

    query = """
        SELECT model,
               AVG(profit) AS avg_profit,
               AVG(users) AS avg_users
        FROM results
        GROUP BY model
        ORDER BY model;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Round for readability
    df["avg_profit"] = df["avg_profit"].round(2)
    df["avg_users"] = df["avg_users"].round(0).astype(int)

    print("\n--- Historical DB Summary ---")
    print(df.to_string(index=False))
    print("---------------------------------\n")

    # === Profit Chart ===
    plt.figure(figsize=(8, 5))
    plt.bar(df["model"], df["avg_profit"])
    plt.title("Average Profit per Model")
    plt.xlabel("Model")
    plt.ylabel("Profit")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

    # === Users Chart ===
    plt.figure(figsize=(8, 5))
    plt.bar(df["model"], df["avg_users"])
    plt.title("Average Users per Model")
    plt.xlabel("Model")
    plt.ylabel("Users")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()
