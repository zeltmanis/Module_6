import json
import os

class Config:
    """Loads simulation configuration strictly from JSON."""

    def __init__(self, config_path=None):
        if not config_path:
            raise ValueError("No config file provided.")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            self.params = json.load(f)

        print(f"Loaded config: {config_path}")

    def get(self, key):
        return self.params.get(key)

    def all(self):
        return self.params

    def summary(self):
        print("\n--- Configuration ---")
        for key, val in self.params.items():
            print(f"{key}: {val}")
        print("----------------------\n")
