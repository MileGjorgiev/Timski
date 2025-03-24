import pygame
from sklearn.linear_model import LinearRegression
import numpy as np

class AIModule:
    def __init__(self):
        self.performance_data = []
        self.base_difficulty = 20

    def record_performance(self, level, moves_left, score, time_taken):
        """Record player performance metrics"""
        self.performance_data.append({
            'level': level,
            'moves_left': moves_left,
            'score': score,
            'time': time_taken,
            'timestamp': pygame.time.get_ticks()
        })

        # Keep only recent data (last 5 levels)
        if len(self.performance_data) > 5:
            self.performance_data = self.performance_data[-5:]

    def calculate_difficulty(self):
        """Calculate new difficulty based on performance"""
        if not self.performance_data:
            return self.base_difficulty

        avg_moves = sum(d['moves_left'] for d in self.performance_data) / len(self.performance_data)

        if avg_moves > 15:  # Player is doing well
            return max(10, self.base_difficulty - 2)
        elif avg_moves < 5:  # Player is struggling
            return min(30, self.base_difficulty + 2)
        else:
            return self.base_difficulty