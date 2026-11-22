"""
Модуль, реализующий многослойный персептрон с обратным распространением ошибки и Softmax
"""
import random
import math
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor

class Neuron:
    def __init__(self, num_inputs):
        limit = math.sqrt(2.0 / num_inputs)
        self.weights = [random.uniform(-limit, limit) for _ in range(num_inputs)]
        self.bias = random.uniform(-0.05, 0.05)
        self.output = 0.0
        self.error = 0.0
        self.inputs = []

    def activate(self, inputs):
        self.inputs = inputs
        weighted_sum = sum(w * x for w, x in zip(self.weights, inputs)) + self.bias
        weighted_sum = max(-30.0, min(30.0, weighted_sum))
        self.output = 1.0 / (1.0 + math.exp(-weighted_sum))
        return self.output

class Layer:
    def __init__(self, num_neurons, num_inputs):
        self.neurons = [Neuron(num_inputs) for _ in range(num_neurons)]
        self.num_neurons = num_neurons

    def forward(self, inputs):
        return [n.activate(inputs) for n in self.neurons]

