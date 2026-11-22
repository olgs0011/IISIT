"""
Модуль, реализующий класс Слой для нейронной сети.
"""
from neuron import Neuron


class Layer:
    """
    Слой нейронов. Поддерживает прямое распространение,
    вычисление ошибок выходного и скрытого слоёв, обновление весов.
    """

    def __init__(self, num_neurons, num_inputs, is_output=False):
        self.neurons = [Neuron(num_inputs) for _ in range(num_neurons)]
        self.num_neurons = num_neurons
        self.is_output = is_output

    def forward(self, inputs):
        return [neuron.activate(inputs) for neuron in self.neurons]

    def softmax(self):
        """
        Применяется только к выходному слою — превращает выходы
        сигмоид в распределение вероятностей (сумма = 1).
        """
        if not self.is_output:
            return [n.output for n in self.neurons]
        values = [n.output for n in self.neurons]
        max_v = max(values)
        exps = [math_exp(v - max_v) for v in values]
        total = sum(exps) if sum(exps) > 0 else 1.0
        probs = [e / total for e in exps]
        for n, p in zip(self.neurons, probs):
            n.output = p
        return probs

    def calculate_output_errors(self, target_outputs):
        """
        Для выходного слоя с softmax + кросс-энтропией:
            dL/dz = output - target
        Знакомая форма — быстро сходится.
        """
        for i, neuron in enumerate(self.neurons):
            neuron.error = neuron.output - target_outputs[i]

    def calculate_hidden_errors(self, next_layer):
        for i, neuron in enumerate(self.neurons):
            error_sum = sum(
                next_layer.neurons[j].error * next_layer.neurons[j].weights[i]
                for j in range(next_layer.num_neurons)
            )
            neuron.error = error_sum * Neuron.sigmoid_derivative(neuron.output)

    def update_weights(self, learning_rate):
        for neuron in self.neurons:
            for i in range(len(neuron.weights)):
                neuron.weights[i] -= learning_rate * neuron.error * neuron.inputs[i]
            neuron.bias -= learning_rate * neuron.error


def math_exp(x):
    import math
    if x < -500.0:
        return 0.0
    if x > 500.0:
        return math.exp(500.0)
    return math.exp(x)