from sklearn.linear_model import LinearRegression
import numpy as np


class AIModule:
    def __init__(self):
        self.performance_data = []
        self.move_model = LinearRegression()
        self.time_model = LinearRegression()  # New model for time prediction
        self.base_difficulty = 20
        self.base_time_limit = 60  # Initial time limit (1 minute)
        self.trained = False
        self.ai_activated_shown = False

    def record_performance(self, level, moves_left, score, time_taken):
        """Record player performance metrics"""
        moves_used = self.base_difficulty - moves_left
        time_used = time_taken

        self.performance_data.append({
            'level': level,
            'moves_used': moves_used,
            'score': score,
            'time_used': time_used
        })

        if len(self.performance_data) >= 2:  # Need at least 2 data points
            self.train_models()

    def train_models(self):
        # Prepare data
        X = np.array([[d['score'], d['level']] for d in self.performance_data])
        y_moves = np.array([d['moves_used'] for d in self.performance_data])
        y_time = np.array([d['time_used'] for d in self.performance_data])

        # Train both models
        self.move_model.fit(X, y_moves)
        self.time_model.fit(X, y_time)
        self.trained = True

        if not self.ai_activated_shown:
            print("🤖 AI Activated! Now predicting moves and time requirements")
            self.ai_activated_shown = True

    def calculate_difficulty(self):
        if self.trained and self.performance_data:
            last = self.performance_data[-1]

            # Predict moves needed
            predicted_moves = self.move_model.predict(
                [[last['score'], last['level'] + 1]]
            )[0]

            # Predict time needed (in seconds)
            predicted_time = self.time_model.predict(
                [[last['score'], last['level'] + 1]]
            )[0]

            # Return both values (moves and time limit)
            return (
                max(10, min(30, int(round(predicted_moves)) + 1)),  # moves
                max(30, min(120, int(round(predicted_time)) + 10)  # seconds (30s-2min)
                    ))
        return self.base_difficulty, self.base_time_limit