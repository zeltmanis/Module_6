import numpy as np

class PricingModel:
    def calculate_revenue(self, users, params):
        raise NotImplementedError

class FlatMonthly(PricingModel):
    def calculate_revenue(self, users, params):
        return users * params["monthly_price"]

class YearlySubscription(PricingModel):
    def calculate_revenue(self, users, params):
        yearly_discount = params.get("yearly_discount", 0.85)
        monthly_price = params["monthly_price"]
        return users * (monthly_price * 12 * yearly_discount) / 12

class UsageBased(PricingModel):
    def calculate_revenue(self, users, params):
        avg_usage = params.get("avg_usage", 20)
        price_per_unit = params.get("price_per_unit", 0.5)
        usage_factor = np.random.normal(1, 0.1)
        return users * avg_usage * price_per_unit * usage_factor