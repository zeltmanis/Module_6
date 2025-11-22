import numpy as np

class PricingModel:
    """Base class for all pricing models."""
    def calculate_revenue(self, users, params):
        raise NotImplementedError("Subclasses must implement this method.")

    def effective_price_per_user(self, params):
        raise NotImplementedError("Subclasses must implement this method.")


# ------------------------------------------------------------
# Standard Plans
# ------------------------------------------------------------

class FlatMonthly(PricingModel):
    """Standard monthly subscription per user."""
    def calculate_revenue(self, users, params):
        return users * params["monthly_price"]

    def effective_price_per_user(self, params):
        return params["monthly_price"]


class YearlySubscription(PricingModel):
    """Standard yearly subscription (discount applied)."""
    def calculate_revenue(self, users, params):
        monthly_price = params["monthly_price"]
        discount = params.get("yearly_discount", 0.85)
        return users * (monthly_price * 12 * discount) / 12

    def effective_price_per_user(self, params):
        return params["monthly_price"] * params.get("yearly_discount", 0.85)


# ------------------------------------------------------------
# Premium Plans
# ------------------------------------------------------------

class PremiumMonthly(PricingModel):
    """Premium monthly subscription."""
    def calculate_revenue(self, users, params):
        return users * params["premium_monthly_price"]

    def effective_price_per_user(self, params):
        return params["premium_monthly_price"]


class PremiumYearlySubscription(PricingModel):
    """Premium yearly subscription with discount."""
    def calculate_revenue(self, users, params):
        monthly_price = params["premium_monthly_price"]
        discount = params.get("premium_yearly_discount", 0.70)
        return users * (monthly_price * 12 * discount) / 12

    def effective_price_per_user(self, params):
        return params["premium_monthly_price"] * params.get("premium_yearly_discount", 0.70)


# ------------------------------------------------------------
# Optional Usage-Based Billing
# ------------------------------------------------------------

class UsageBased(PricingModel):
    """Optional: usage-based pricing."""
    def calculate_revenue(self, users, params):
        base_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)

        spike_events = np.random.poisson(lam=1)
        spike_usage = spike_events * np.random.uniform(5, 15)

        usage_variation = np.random.normal(1, 0.1)
        total_usage = (base_usage + spike_usage) * usage_variation

        return users * total_usage * price_per_unit

    def effective_price_per_user(self, params):
        return params.get("avg_usage", 20) * params.get("price_per_unit", 0.5)
