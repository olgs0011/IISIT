"""
Модуль для вычисления метрик качества модели
"""
import numpy as np


class Metrics:
    """
    Класс для вычисления метрик качества классификации
    """

    @staticmethod
    def evaluate_model(network, test_data, classes):
        """
        Вычисление метрик качества модели на тестовой выборке

        Args:
            network: обученная нейронная сеть (с методом predict)
            test_data: список кортежей (inputs, target_outputs)
            classes: список названий классов

        Returns:
            словарь с метриками:
                - accuracy: общая точность
                - precision: среднее precision
                - recall: среднее recall
                - f1: среднее F1
                - per_class_metrics: {индекс_класса: {'precision', 'recall', 'f1', 'support'}}
                - confusion_matrix: матрица ошибок (numpy array)
        """
        num_classes = len(classes)
        confusion_matrix = np.zeros((num_classes, num_classes), dtype=int)

        # Заполнение матрицы ошибок
        for inputs, target_outputs in test_data:
            # Предсказание сети
            predicted_idx = network.predict(inputs)
            # Истинный класс — индекс максимального значения в one-hot векторе
            true_idx = target_outputs.index(max(target_outputs))

            if 0 <= predicted_idx < num_classes and 0 <= true_idx < num_classes:
                confusion_matrix[true_idx][predicted_idx] += 1

        # Accuracy
        total = confusion_matrix.sum()
        correct = np.trace(confusion_matrix)
        accuracy = correct / total if total > 0 else 0.0

        # Метрики по каждому классу
        per_class_metrics = {}
        precisions = []
        recalls = []
        f1_scores = []

        for i in range(num_classes):
            tp = confusion_matrix[i][i]
            fp = confusion_matrix[:, i].sum() - tp   # предсказано i, а на самом деле не i
            fn = confusion_matrix[i, :].sum() - tp   # на самом деле i, а предсказано не i

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall / (precision + recall)
                  if (precision + recall) > 0 else 0.0)

            per_class_metrics[i] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'support': int(confusion_matrix[i, :].sum())
            }

            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)

        # Средние значения (macro-average)
        avg_precision = float(np.mean(precisions)) if precisions else 0.0
        avg_recall = float(np.mean(recalls)) if recalls else 0.0
        avg_f1 = float(np.mean(f1_scores)) if f1_scores else 0.0

        return {
            'accuracy': float(accuracy),
            'precision': avg_precision,
            'recall': avg_recall,
            'f1': avg_f1,
            'per_class_metrics': per_class_metrics,
            'confusion_matrix': confusion_matrix
        }

    @staticmethod
    def print_metrics(metrics, classes):
        """
        Вывод метрик в консоль

        Args:
            metrics: словарь с метриками (результат evaluate_model)
            classes: список названий классов
        """
        print("\n" + "=" * 70)
        print("МЕТРИКИ КАЧЕСТВА МОДЕЛИ")
        print("=" * 70)
        print(f"Точность (Accuracy): {metrics['accuracy']:.4f} "
              f"({metrics['accuracy'] * 100:.2f}%)")
        print(f"Precision (среднее): {metrics['precision']:.4f}")
        print(f"Recall (среднее):    {metrics['recall']:.4f}")
        print(f"F1-score (среднее):  {metrics['f1']:.4f}")

        print("\n" + "-" * 70)
        print(f"{'Класс':<15} {'Precision':<12} {'Recall':<12} {'F1-score':<12} {'Support':<10}")
        print("-" * 70)
        for class_idx, class_name in enumerate(classes):
            if class_idx in metrics['per_class_metrics']:
                m = metrics['per_class_metrics'][class_idx]
                print(f"{class_name:<15} {m['precision']:<12.4f} "
                      f"{m['recall']:<12.4f} {m['f1']:<12.4f} {m['support']:<10}")

        print("\n" + "-" * 70)
        print("Матрица ошибок (Confusion Matrix):")
        print("-" * 70)
        header = f"{'':<15}" + "".join(f"{name[:10]:<12}" for name in classes)
        print(header)
        cm = metrics['confusion_matrix']
        for i, true_class in enumerate(classes):
            row = f"{true_class[:14]:<15}" + "".join(f"{cm[i][j]:<12}" for j in range(len(classes)))
            print(row)
        print("=" * 70 + "\n")