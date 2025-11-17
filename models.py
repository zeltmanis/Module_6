import numpy as np

class PricingModel:
    """Base class for all pricing models."""
    def calculate_revenue(self, users, params):
        raise NotImplementedError("Subclasses must implement this method.")

    def effective_price_per_user(self, params):
        raise NotImplementedError("Subclasses must implement this method.")


class FlatMonthly(PricingModel):
    def calculate_revenue(self, users, params):
        price = params["monthly_price"]
        return users * price

    def effective_price_per_user(self, params):
        return params["monthly_price"]


class YearlySubscription(PricingModel):
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
        base_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)

        # 🧠 Introduce bursty usage with Poisson-distributed spikes
        spike_events = np.random.poisson(lam=1, size=1)  # expected ~1 spike per period
        usage = base_usage + spike_events * np.random.uniform(5, 15)

        usage_factor = np.random.normal(1, 0.1)
        total_usage = usage * usage_factor

        return users * total_usage * price_per_unit

    def effective_price_per_user(self, params):
        avg_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)
        return avg_usage * price_per_unit


    def effective_price_per_user(self, params):
        avg_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)
        return avg_usage * price_per_unit


# ✅ Add your new class here
class TieredPricing(PricingModel):
    """Pricing model with multiple usage tiers."""
    def calculate_revenue(self, users, params):
        # simulate user usage
        avg_usage = np.random.normal(20, 5)
        # simple tier logic
        if avg_usage <= 10:
            rate = 0.5
        elif avg_usage <= 20:
            rate = 0.8
        else:
            rate = 1.0
        return users * avg_usage * rate

    def effective_price_per_user(self, params):
        return 0.8 * params.get("avg_usage", 20)
