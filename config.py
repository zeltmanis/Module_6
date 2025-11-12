import json
import os

class Config:
    """Holds and validates all simulation parameters."""

    def __init__(self, config_path=None):
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.params = json.load(f)
            print(f"✅ Loaded config: {config_path}")
        else:
            if config_path:
                print(f"⚠️  Config file '{config_path}' not found. Using defaults.")
            self.params = {}
        self._apply_defaults()

    def _apply_defaults(self):
        defaults = {
            "months": 24,
            "initial_users": 1000,
            "growth_rate": 0.08,
            "churn_rate": 0.03,
            "monthly_price": 10,
            "cost_ratio": 0.6,
            "yearly_discount": 0.85,
            "avg_usage": 20,
            "price_per_unit": 0.5,
        }
        for key, val in defaults.items():
            self.params.setdefault(key, val)

    def get(self, key):
        return self.params.get(key)

    def all(self):
        return self.params

    def summary(self):
        print("\n--- Configuration Summary ---")
        for k, v in self.params.items():
            print(f"{k}: {v}")
        print("------------------------------\n")
