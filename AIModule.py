from sklearn.linear_model import LinearRegression
import numpy as np

class AIModule:
    def __init__(self):
        self.performance_data = []
        self.model = LinearRegression()
        self.base_difficulty = 20
        self.trained = False
        self.ai_activated_shown = False

    def record_performance(self, level, moves_left, score, time_taken):
        """Record player performance metrics"""
        moves_used = self.base_difficulty - moves_left

        self.performance_data.append({
            'level': level,
            'moves_used': moves_used,
            'score': score,
            'time': time_taken
        })

        if len(self.performance_data) >= 1:   # train only on the last level
            self.train_model()

    def train_model(self):
        last = self.performance_data[-1]
        X = np.array([[last['score'], last['time']]])
        y = np.array([last['moves_used']])
        self.model.fit(X, y)
        self.trained = True

        if not self.ai_activated_shown:
            print("🤖 AI Activated!")
            self.ai_activated_shown = True

    def calculate_difficulty(self):
        if self.trained and self.performance_data:
            last = self.performance_data[-1]
            predicted_moves_used = self.model.predict([[last['score'], last['time']]])[0]
            predicted_total_moves = int(round(predicted_moves_used)) + 1

            return max(10, min(30, predicted_total_moves))  # Clamp between 10 and 30
        return self.base_difficulty
