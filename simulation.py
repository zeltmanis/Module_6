import numpy as np

class Simulation:
    """Runs a month-by-month simulation for a single subscription plan."""

    def __init__(self, config, model):
        self.cfg = config
        self.model = model
        self.months = config.get("months")

    # ------------------------------------------------------------
    # Dynamic behaviors (SaaS realistic)
    # ------------------------------------------------------------

    def dynamic_churn(self, price, base_churn):
        """
        Churn increases if price is higher than baseline.
        Decreases slightly if price is lower.
        """
        baseline_price = self.cfg.get("monthly_price")
        return max(base_churn + 0.01 * ((price / baseline_price) - 1) * 10, 0)

    def dynamic_growth(self, month, base_growth):
        """
        Growth decays slowly over time.
        """
        decay_rate = 0.04
        return base_growth * np.exp(-decay_rate * month)

    def dynamic_cost_ratio(self, users, base_cost_ratio):
        """
        Costs decrease slightly with scale (economies of scale).
        """
        scale_factor = np.log10(users + 10) / 4
        improvement = 0.1 * scale_factor
        return base_cost_ratio * (1 - improvement)

    # ------------------------------------------------------------
    # Single simulation run
    # ------------------------------------------------------------

    def run_once(self, seed=None):
        if seed is not None:
            np.random.seed(seed)

        users = int(self.cfg.get("initial_users"))
        base_growth = self.cfg.get("growth_rate")
        base_churn = self.cfg.get("churn_rate")
        base_cost_ratio = self.cfg.get("cost_ratio")

        # Each model defines effective price
        price = self.model.effective_price_per_user(self.cfg.all())

        profits = []
        revenues = []
        user_counts = []

        for month in range(1, self.months + 1):
            # dynamic effects
            growth = self.dynamic_growth(month, base_growth)
            churn = self.dynamic_churn(price, base_churn)
            cost_ratio = self.dynamic_cost_ratio(users, base_cost_ratio)

            # update users
            new_users = users * growth
            lost_users = users * churn
            users = max(int(users + new_users - lost_users), 0)

            # revenue & profit
            revenue = float(self.model.calculate_revenue(users, self.cfg.all()))
            cost = revenue * cost_ratio
            profit = revenue - cost

            revenues.append(revenue)
            profits.append(profit)
            user_counts.append(users)

        return {
            "profits": np.array(profits),
            "revenues": np.array(revenues),
            "users": np.array(user_counts),
            "final_users": int(user_counts[-1])
        }
