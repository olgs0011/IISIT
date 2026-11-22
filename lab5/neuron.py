"""
Модуль, реализующий класс Нейрон для нейронной сети.
Единственный класс Neuron в проекте — используется всеми остальными модулями.
"""
import random
import math


class Neuron:
    """
    Нейрон с сигмоидной активацией.

    Входные значения ожидаются в диапазоне [0, 1],
    веса инициализируются по схеме He (sqrt(2/n)) — это даёт
    взвешенную сумму порядка ±2, что хорошо для сигмоиды.
    """

    def __init__(self, num_inputs):
        limit = math.sqrt(2.0 / max(1, num_inputs))
        self.weights = [random.uniform(-limit, limit) for _ in range(num_inputs)]
        self.bias = 0.0

        self.output = 0.0
        self.error = 0.0
        self.inputs = []

    def activate(self, inputs):
        """Прямое распространение через сигмоиду."""
        self.inputs = inputs
        weighted_sum = sum(w * x for w, x in zip(self.weights, inputs)) + self.bias
        self.output = self._sigmoid(weighted_sum)
        return self.output

    @staticmethod
    def _sigmoid(x):
        # Защита от переполнения math.exp
        if x < -500.0:
            return 0.0
        if x > 500.0:
            return 1.0
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def sigmoid_derivative(output):
        """Производная сигмоиды, выраженная через её же выход."""
        return output * (1.0 - output)