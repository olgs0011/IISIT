"""
Модуль для загрузки и обработки данных обучающей выборки
"""
import csv
import os
from PIL import Image
import numpy as np


class DataLoader:
    """
    Класс для загрузки и управления данными обучающей выборки
    """

    def __init__(self, csv_path=None):
        """
        Инициализация загрузчика данных

        Args:
            csv_path: путь к CSV файлу с данными
        """
        self.csv_path = csv_path
        self.dataset = []
        self.classes = []
        self.class_to_index = {}
        self.index_to_class = {}

    def load_from_csv(self, csv_path):
        """
        Загрузка данных из CSV файла

        Args:
            csv_path: путь к CSV файлу
        """
        self.csv_path = csv_path
        self.dataset = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Пропускаем заголовок

            for row in reader:
                if len(row) < 2:
                    continue

                label = row[0]
                pixels = [float(x) / 255.0 for x in row[1:]]  # Нормализация к [0, 1]

                # Добавление класса в список, если его еще нет
                if label not in self.classes:
                    self.classes.append(label)

                self.dataset.append({
                    'label': label,
                    'pixels': pixels
                })

        # Создание словарей для индексации классов
        self.classes.sort()
        self.class_to_index = {cls: idx for idx, cls in enumerate(self.classes)}
        self.index_to_class = {idx: cls for idx, cls in enumerate(self.classes)}

        print(f"Загружено {len(self.dataset)} примеров, классов: {len(self.classes)}")
        print(f"Классы: {self.classes}")

    def get_training_data(self, train_ratio=0.8):
        """
        Разделение данных на обучающую и тестовую выборки

        Args:
            train_ratio: доля обучающей выборки (0.8 = 80%)
            остальное (0.2 = 20%) - тестовая выборка

        Returns:
            кортеж (train_data, test_data), где каждый элемент - список кортежей (inputs, target_outputs)
        """
        # Перемешивание данных
        import random
        random.shuffle(self.dataset)

        total = len(self.dataset)
        train_end = int(total * train_ratio)

        train_dataset = self.dataset[:train_end]
        test_dataset = self.dataset[train_end:]

        # Преобразование в формат для обучения
        train_data = []
        for item in train_dataset:
            inputs = item['pixels']
            target = self._one_hot_encode(item['label'])
            train_data.append((inputs, target))

        test_data = []
        for item in test_dataset:
            inputs = item['pixels']
            target = self._one_hot_encode(item['label'])
            test_data.append((inputs, target))

        print(f"Разделение данных:")
        print(f"  Обучающая выборка: {len(train_data)} примеров ({len(train_data) / total * 100:.1f}%)")
        print(f"  Тестовая выборка: {len(test_data)} примеров ({len(test_data) / total * 100:.1f}%)")

        return train_data, test_data

    def _one_hot_encode(self, label):
        """
        Преобразование метки класса в one-hot encoding

        Args:
            label: метка класса

        Returns:
            список с one-hot encoding
        """
        encoded = [0.0] * len(self.classes)
        if label in self.class_to_index:
            encoded[self.class_to_index[label]] = 1.0
        return encoded

    def add_sample(self, pixels, label):
        """
        Добавление нового примера в выборку

        Args:
            pixels: список пикселей (нормализованные к [0, 1])
            label: метка класса
        """
        # Добавление нового класса, если его еще нет
        if label not in self.classes:
            self.classes.append(label)
            self.classes.sort()
            self.class_to_index = {cls: idx for idx, cls in enumerate(self.classes)}
            self.index_to_class = {idx: cls for idx, cls in enumerate(self.classes)}

        self.dataset.append({
            'label': label,
            'pixels': pixels
        })

    def remove_sample(self, index):
        """
        Удаление примера из выборки

        Args:
            index: индекс примера для удаления
        """
        if 0 <= index < len(self.dataset):
            del self.dataset[index]

    def update_sample(self, index, pixels=None, label=None):
        """
        Обновление примера в выборке

        Args:
            index: индекс примера
            pixels: новые пиксели (если None, не изменяются)
            label: новая метка (если None, не изменяется)
        """
        if 0 <= index < len(self.dataset):
            if pixels is not None:
                self.dataset[index]['pixels'] = pixels
            if label is not None:
                self.dataset[index]['label'] = label
                if label not in self.classes:
                    self.classes.append(label)
                    self.classes.sort()
                    self.class_to_index = {cls: idx for idx, cls in enumerate(self.classes)}
                    self.index_to_class = {idx: cls for idx, cls in enumerate(self.classes)}

    def save_to_csv(self, csv_path):
        """
        Сохранение данных в CSV файл

        Args:
            csv_path: путь для сохранения
        """
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Заголовок
            header = ['label'] + [f'pixel {i + 1}' for i in range(len(self.dataset[0]['pixels']))]
            writer.writerow(header)

            # Данные
            for item in self.dataset:
                row = [item['label']] + [int(x * 255) for x in item['pixels']]
                writer.writerow(row)

    def image_to_pixels(self, image, size=(64, 64)):
        """
        Преобразование изображения в список пикселей

        Args:
            image: PIL Image объект
            size: размер для изменения изображения

        Returns:
            список нормализованных пикселей [0, 1]
        """
        # Изменение размера и преобразование в grayscale
        image = image.convert('L').resize(size)

        # Преобразование в массив и нормализация
        pixels = list(image.getdata())
        pixels = [p / 255.0 for p in pixels]

        return pixels

    def pixels_to_image(self, pixels, size=(64, 64)):
        """
        Преобразование списка пикселей в изображение

        Args:
            pixels: список нормализованных пикселей [0, 1]
            size: размер изображения

        Returns:
            PIL Image объект
        """
        # Денормализация
        pixels = [int(p * 255) for p in pixels]

        # Создание изображения
        image = Image.new('L', size)
        image.putdata(pixels)

        return image
