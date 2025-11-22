import sqlite3
import pandas as pd
import os


def initialize_db(db_name="simulation_results.db"):
    """Create the database schema if it does not exist."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            month INTEGER NOT NULL,
            profit REAL NOT NULL,
            revenue REAL NOT NULL,
            users INTEGER NOT NULL
        );
    """)

    conn.commit()
    conn.close()


def save_to_db(results, db_name="simulation_results.db"):
    """
    Save all simulation results into SQLite.

    results = {
        "Standard Monthly": {
            "profits": [...],
            "revenues": [...],
            "final_users": X,
            ...
        },
        ...
    }
    """
    initialize_db(db_name)
    conn = sqlite3.connect(db_name)

    rows_to_insert = []

    for model_name, model_data in results.items():
        profits = model_data["profits"]
        revenues = model_data["revenues"]
        final_users = model_data["final_users"]

        for month_idx, (profit, revenue) in enumerate(zip(profits, revenues), start=1):
            rows_to_insert.append(
                (model_name, month_idx, float(profit), float(revenue), int(final_users))
            )

    df = pd.DataFrame(
        rows_to_insert,
        columns=["model", "month", "profit", "revenue", "users"]
    )

    df.to_sql("results", conn, if_exists="append", index=False)
    conn.close()
    print("✅ Results saved to database.")


def summarize_db(db_name="simulation_results.db"):
    """Print a rounded summary: average profit and users per model."""

    if not os.path.exists(db_name):
        print("⚠️ Database does not exist.")
        return

    conn = sqlite3.connect(db_name)

    query = """
        SELECT model,
               AVG(profit) AS avg_profit,
               AVG(users)  AS avg_users
        FROM results
        GROUP BY model
        ORDER BY model;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Round for readability
    df["avg_profit"] = df["avg_profit"].round(2)  # 2 decimals for money
    df["avg_users"] = df["avg_users"].round(0).astype(int)

    print("\n--- Historical DB Summary ---")
    print(df.to_string(index=False))
    print("---------------------------------\n")

    return df
