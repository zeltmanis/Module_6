import numpy as np

class PricingModel:
    """Base class for all pricing models."""
    def calculate_revenue(self, users, params):
        raise NotImplementedError("Subclasses must implement this method.")

    def effective_price_per_user(self, params):
        """Estimated per-user cost used for satisfaction/churn calculations."""
        raise NotImplementedError("Subclasses must implement this method.")


class FlatMonthly(PricingModel):
    """Each user pays a flat monthly price."""
    def calculate_revenue(self, users, params):
        price = params["monthly_price"]
        return users * price

    def effective_price_per_user(self, params):
        return params["monthly_price"]


class YearlySubscription(PricingModel):
    """Users pay a discounted yearly rate, spread monthly."""
    def calculate_revenue(self, users, params):
        monthly_price = params["monthly_price"]
        discount = params.get("yearly_discount", 0.85)
        return users * (monthly_price * 12 * discount) / 12

    def effective_price_per_user(self, params):
        monthly_price = params["monthly_price"]
        discount = params.get("yearly_discount", 0.85)
        return monthly_price * discount


class UsageBased(PricingModel):
    """Users pay based on how much they use the service."""
    def calculate_revenue(self, users, params):
        avg_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)
        usage_factor = np.random.normal(1, 0.1)
        return users * avg_usage * price_per_unit * usage_factor

    def effective_price_per_user(self, params):
        avg_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)
        return avg_usage * price_per_unit
