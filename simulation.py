import numpy as np
from objectives import revenue_growth_curve, customer_satisfaction, fairness_metric

class Simulation:
    """Runs a month-by-month simulation with dynamic feedback effects."""

    def __init__(self, config, model):
        self.cfg = config
        self.model = model
        self.months = config.get("months")

    # ---------- Dynamic behavior models ----------
    def dynamic_churn(self, price, base_churn):
        baseline_price = self.cfg.get("monthly_price")
        return base_churn + 0.01 * ((price / baseline_price) - 1) * 10

    def dynamic_growth(self, month, base_growth):
        decay_rate = 0.04
        return base_growth * np.exp(-decay_rate * month)

    def dynamic_cost_ratio(self, users, base_cost_ratio):
        scale_factor = np.log10(users + 10) / 4
        improvement = 0.1 * scale_factor
        return base_cost_ratio * (1 - improvement)

    # ---------- Single simulation run ----------
    def run_once(self, seed=None):
        if seed is not None:
            np.random.seed(seed)

        users = self.cfg.get("initial_users")
        base_growth = self.cfg.get("growth_rate")
        base_churn = self.cfg.get("churn_rate")
        base_cost_ratio = self.cfg.get("cost_ratio")
        price = self.model.effective_price_per_user(self.cfg.all())

        profits = []
        revenues = []
        churn = base_churn

        for month in range(1, self.months + 1):
            growth = self.dynamic_growth(month, base_growth)
            churn = self.dynamic_churn(price, base_churn)
            cost_ratio = self.dynamic_cost_ratio(users, base_cost_ratio)

            new_users = users * growth
            lost_users = users * churn
            users = max(users + new_users - lost_users, 0)

            revenue = self.model.calculate_revenue(users, self.cfg.all())
            cost = revenue * cost_ratio
            profit = revenue - cost

            revenues.append(revenue)
            profits.append(profit)

        # --- Fairness Simulation ---
        user_usages = np.random.lognormal(mean=2.5, sigma=0.6, size=100)
        if self.model.__class__.__name__ == "UsageBased":
            user_prices = user_usages * (price / np.mean(user_usages))
        elif self.model.__class__.__name__ == "YearlySubscription":
            user_prices = np.full_like(user_usages, price)
        else:
            user_prices = np.full_like(user_usages, price * 1.05)

        metrics = {
            "profits": np.array(profits),
            "revenues": np.array(revenues),
            "revenue_growth": revenue_growth_curve(revenues),
            "satisfaction": customer_satisfaction(price, churn),
            "fairness": fairness_metric(user_usages, user_prices),
        }
        return metrics

    # ---------- Multi-run simulation ----------
    def multi_run(self, runs=100):
        """Run multiple simulations and aggregate metrics."""
        all_profits = []
        all_revenues = []
        growths, satisfactions, fairnesses = [], [], []

        for i in range(runs):
            metrics = self.run_once(seed=i)
            all_profits.append(metrics["profits"])
            all_revenues.append(metrics["revenues"])
            growths.append(metrics["revenue_growth"])
            satisfactions.append(metrics["satisfaction"])
            fairnesses.append(metrics["fairness"])

        all_profits = np.array(all_profits)
        all_revenues = np.array(all_revenues)

        stats = {
            "mean_profit": all_profits.mean(axis=0),
            "std_profit": all_profits.std(axis=0),
            "mean_revenue": all_revenues.mean(axis=0),
            "revenue_growth": np.mean(growths),
            "satisfaction": np.mean(satisfactions),
            "fairness": np.mean(fairnesses),
        }

        return stats
