import numpy as np

class Simulation:
    """Runs a month-by-month simulation with dynamic feedback effects."""

    def __init__(self, config, model):
        self.cfg = config
        self.model = model
        self.months = config.get("months")

    def dynamic_churn(self, price, base_churn):
        """Churn increases if price rises above baseline."""
        baseline_price = self.cfg.get("monthly_price")
        # For every 10% price increase above baseline, churn +1%
        return base_churn + 0.01 * ((price / baseline_price) - 1) * 10

    def dynamic_growth(self, month, base_growth):
        """Growth slows over time (market saturation)."""
        decay_rate = 0.04  # how quickly adoption saturates
        return base_growth * np.exp(-decay_rate * month)

    def dynamic_cost_ratio(self, users, base_cost_ratio):
        """Cost efficiency improves as user base scales."""
        scale_factor = np.log10(users + 10) / 4  # between 0–1 roughly
        improvement = 0.1 * scale_factor  # up to 10% cost reduction
        return base_cost_ratio * (1 - improvement)

    def run(self, seed=None):
        if seed is not None:
            np.random.seed(seed)

        users = self.cfg.get("initial_users")
        base_growth = self.cfg.get("growth_rate")
        base_churn = self.cfg.get("churn_rate")
        base_cost_ratio = self.cfg.get("cost_ratio")
        price = self.cfg.get("monthly_price")

        profits = []

        for month in range(1, self.months + 1):
            # dynamic adjustments
            growth = self.dynamic_growth(month, base_growth)
            churn = self.dynamic_churn(price, base_churn)
            cost_ratio = self.dynamic_cost_ratio(users, base_cost_ratio)

            # user updates
            new_users = users * growth
            lost_users = users * churn
            users += new_users - lost_users
            users = max(users, 0)  # no negatives

            # revenue & cost
            revenue = self.model.calculate_revenue(users, self.cfg.all())
            cost = revenue * cost_ratio
            profit = revenue - cost
            profits.append(profit)

        return profits
