import sqlite3
import pandas as pd

def save_to_db(results, db_name="simulation_results.db"):
    conn = sqlite3.connect(db_name)
    for model, stats in results.items():
        df = pd.DataFrame({
            "month": range(1, len(stats["mean_profit"]) + 1),
            "mean_profit": stats["mean_profit"],
            "mean_revenue": stats["mean_revenue"]
        })
        df["model"] = model
        df.to_sql("results", conn, if_exists="append", index=False)
    conn.close()