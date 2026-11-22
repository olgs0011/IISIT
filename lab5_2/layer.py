"""
Модуль, реализующий класс Слой для нейронной сети
"""
from neuron import Neuron


class Layer:
    """
    Класс, представляющий слой нейронов в нейронной сети
    """
    def __init__(self, num_neurons, num_inputs):
        self.neurons = [Neuron(num_inputs) for _ in range(num_neurons)]
        self.num_neurons = num_neurons

    def forward(self, inputs):
        outputs = []
        for neuron in self.neurons:
            outputs.append(neuron.activate(inputs))
        return outputs

    def calculate_output_errors(self, target_outputs):
        for i, neuron in enumerate(self.neurons):
            error = (target_outputs[i] - neuron.output) * neuron.sigmoid_derivative(neuron.output)
            neuron.error = error

    def calculate_hidden_errors(self, next_layer):
        for i, neuron in enumerate(self.neurons):
            error_sum = sum(
                next_layer.neurons[j].error * next_layer.neurons[j].weights[i]
                for j in range(next_layer.num_neurons)
            )
            neuron.error = error_sum * neuron.sigmoid_derivative(neuron.output)

    def update_weights(self, learning_rate):
        """
        Обновление весов с защитой от "взрыва" (clipping)
        """
        # Максимально допустимый вес, чтобы сеть не сломалась
        MAX_WEIGHT = 2.0
        for neuron in self.neurons:
            for i in range(len(neuron.weights)):
                delta = learning_rate * neuron.error * neuron.inputs[i]
                new_weight = neuron.weights[i] - delta
                # Добавлено затухание весов (weight decay) для предотвращения насыщения
                new_weight *= 0.999
                neuron.weights[i] = max(-MAX_WEIGHT, min(MAX_WEIGHT, new_weight))

            new_bias = neuron.bias - learning_rate * neuron.error
            neuron.bias = max(-MAX_WEIGHT, min(MAX_WEIGHT, new_bias))