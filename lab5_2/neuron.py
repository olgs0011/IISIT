"""
Модуль, реализующий класс Нейрон для нейронной сети
"""
import random
import math


class Neuron:
    """
    Класс, представляющий нейрон в нейронной сети
    """

    def __init__(self, num_inputs):
        """
        Инициализация нейрона
        Args:
            num_inputs: количество входных связей
        """
        limit = math.sqrt(2.0 / num_inputs)
        self.weights = [random.uniform(-limit, limit) for _ in range(num_inputs)]
        self.bias = 0.0

        self.output = 0.0
        self.error = 0.0
        self.inputs = []

    def activate(self, inputs):
        """
        Активация нейрона (прямое распространение)
        """
        self.inputs = inputs

        # Делим сумму на коэффициент (например, 10.0 или sqrt(len(inputs))),
        # чтобы аргумент сигмоиды не улетал в бесконечность (+inf / -inf),
        # из-за чего сигмоида ломается и выдает везде единицы.
        scale_factor = max(1.0, math.sqrt(len(inputs)))
        weighted_sum = sum(w * x for w, x in zip(self.weights, inputs)) / scale_factor
        weighted_sum += self.bias

        self.output = self._sigmoid(weighted_sum)
        return self.output

    def _sigmoid(self, x):
        """Безопасная сигмоида"""
        # Защита от переполнения
        if x < -500: return 0.0
        if x > 500: return 1.0
        return 1.0 / (1.0 + math.exp(-x))

    def sigmoid_derivative(self, x):
        """Производная сигмоиды"""
        return x * (1.0 - x)