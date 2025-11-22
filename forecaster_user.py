import numpy as np

def forecast_next_active_users(users):
    """
    users: list or array of historical active user counts [U_0, U_1, ..., U_T]
    returns: (objective_value, diagnostics)

    - objective_value: the next expected active users (scalar) for user-growth optimization
    - diagnostics: dict with probability of increase and expected deltas for debugging/analysis
    """
    users = np.array(users, dtype=float)
    if len(users) < 2:
        raise ValueError("Need at least 2 data points to compute changes.")
    
    # 1. Compute changes
    deltas = users[1:] - users[:-1]   # Δ_t
    
    # Define up/down
    up_mask = deltas > 0
    down_mask = deltas < 0
    
    k = up_mask.sum()            # number of increases
    n = (up_mask | down_mask).sum()  # number of non-zero changes
    
    if n == 0:
        # All changes are zero → no info, just return last value
        diagnostics = {
            "p_up": 0.5,  # arbitrary
            "expected_change": 0.0,
            "forecast_next": users[-1]
        }
        return users[-1], diagnostics
    
    # 2. Estimate probability of increase (binomial MLE)
    p_up = k / n
    
    # 3. Magnitude of changes
    up_changes = deltas[up_mask]
    down_changes = deltas[down_mask]
    
    # Avoid empty arrays
    if len(up_changes) == 0:
        mu_up = 0.0
    else:
        mu_up = up_changes.mean()
    
    if len(down_changes) == 0:
        mu_down = 0.0
    else:
        mu_down = down_changes.mean()
    
    # Expected change using mixture of up/down scenarios
    expected_change = p_up * mu_up + (1 - p_up) * mu_down
    
    # 4. Taylor-like forecast: U_{T+1} ≈ U_T + expected_change
    forecast_next = users[-1] + expected_change

    diagnostics = {
        "p_up": p_up,
        "expected_change": expected_change,
        "forecast_next": forecast_next
    }

    # Tuple so optimizers can use the scalar directly while still keeping context
    return forecast_next, diagnostics



# Example usage:
if __name__ == "__main__":
    historical_users = [100, 110, 105, 120, 115, 130]
    next_users, debug = forecast_next_active_users(historical_users)
    print("Expected next users:", next_users)
    print("Diagnostics:", debug)




class PriceElasticityModel:
    def __init__(self):
        self.elasticity_ = None  # estimated price elasticity

    def fit(self, prices, users):
        """
        Estimate price elasticity of demand from historical data.

        prices: list/array of prices [P1, P2, ..., PT]
        users:  list/array of active users [Q1, Q2, ..., QT]
        """
        prices = np.array(prices, dtype=float)
        users = np.array(users, dtype=float)

        if len(prices) != len(users):
            raise ValueError("prices and users must have the same length.")
        if len(prices) < 2:
            raise ValueError("Need at least 2 observations to estimate elasticity.")

        # Remove non-positive values (cannot take log of <= 0)
        mask = (prices > 0) & (users > 0)
        if mask.sum() < 2:
            raise ValueError("Need at least 2 positive (price, user) pairs.")
        
        prices = prices[mask]
        users = users[mask]

        logP = np.log(prices)
        logQ = np.log(users)

        # Simple linear regression: logQ = a + b*logP
        # np.polyfit returns [b, a] when deg=1
        b, a = np.polyfit(logP, logQ, 1)
        self.elasticity_ = b

        return self.elasticity_

    def predict_users(self, current_price, new_price, current_users):
        """
        Predict users and user loss for a new price using the estimated elasticity.

        current_price: current price P0
        new_price:     new price P1
        current_users: current number of users Q0

        Returns: dict with predicted_users, user_loss, elasticity_used
        """
        if self.elasticity_ is None:
            raise ValueError("Model not fitted yet. Call fit(prices, users) first.")

        P0 = float(current_price)
        P1 = float(new_price)
        Q0 = float(current_users)

        if P0 <= 0 or P1 <= 0:
            raise ValueError("Prices must be positive.")
        if Q0 < 0:
            raise ValueError("Current users cannot be negative.")

        # % change in price
        pct_change_price = (P1 - P0) / P0

        # % change in quantity: ε * %ΔP
        pct_change_users = self.elasticity_ * pct_change_price

        # Predicted new users
        Q1 = Q0 * (1 + pct_change_users)

        # User loss (if Q1 < Q0, this is positive)
        user_loss = Q0 - Q1

        return {
            "elasticity_used": self.elasticity_,
            "predicted_users": Q1,
            "user_loss": user_loss
        }


# Example usage:
if __name__ == "__main__":
    # Historical data: prices and corresponding active users
    historical_prices = [10, 12, 11, 13, 9, 8]
    historical_users  = [1000, 900, 950, 850, 1100, 1200]

    model = PriceElasticityModel()
    elasticity = model.fit(historical_prices, historical_users)
    print(f"Estimated elasticity: {elasticity:.3f}")

    # Suppose current price is 10, current users 1000, and we want to raise price to 12
    result = model.predict_users(current_price=10, new_price=12, current_users=1000)
    print(result)
