"""
Главный модуль приложения для распознавания знаков валют
"""
import tkinter as tk
import io
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
import pickle
import os
from neural_network import NeuralNetwork
from data_loader import DataLoader
from metrics import Metrics
from PIL import Image, ImageDraw
import numpy as np
import threading
from datetime import datetime

class CurrencyRecognizerApp:
    """
    Главный класс приложения для распознавания валют
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Распознавание геометрических фигур - Нейронная сеть")
        self.root.geometry("1200x800")

        self.canvas_size = 256
        self.image_size = 64
        self.grid = [[0 for _ in range(self.image_size)] for _ in range(self.image_size)]
        self.drawing = False
        self.last_x = None
        self.last_y = None

        self.network = None
        self.data_loader = DataLoader()

        self.learning_rate = 0.1
        self.epochs = 3
        self.batch_size = 32
        self.num_threads = 4
        self.is_training = False

        self.create_widgets()
        self.load_default_dataset()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        left_frame = ttk.LabelFrame(main_frame, text="Рисование образа", padding="10")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas = tk.Canvas(
            left_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="white",
            cursor="pencil"
        )
        self.canvas.grid(row=0, column=0, padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        draw_buttons = ttk.Frame(left_frame)
        draw_buttons.grid(row=1, column=0, pady=5)

        ttk.Button(draw_buttons, text="Очистить", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Button(draw_buttons, text="Распознать", command=self.recognize).pack(side=tk.LEFT, padx=5)
        ttk.Button(draw_buttons, text="Добавить в выборку", command=self.add_to_dataset).pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(left_frame, text="Результат", padding="10")
        result_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))

        self.result_label = ttk.Label(result_frame, text="Нарисуйте геометрическую фигуру", font=("Arial", 12))
        self.result_label.pack()

        self.probability_label = ttk.Label(result_frame, text="", font=("Arial", 10))
        self.probability_label.pack()

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        network_frame = ttk.LabelFrame(right_frame, text="Нейронная сеть", padding="10")
        network_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(network_frame, text="Архитектура:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.arch_label = ttk.Label(network_frame, text="Не инициализирована")
        self.arch_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Button(network_frame, text="Создать сеть", command=self.create_network).grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.train_button = ttk.Button(network_frame, text="Обучить сеть", command=self.train_network)
        self.train_button.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(network_frame, text="Сохранить сеть", command=self.save_network).grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(network_frame, text="Загрузить сеть", command=self.load_network).grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(network_frame, text="Визуализировать архитектуру", command=self.visualize_architecture).grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        progress_frame = ttk.Frame(network_frame)
        progress_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(progress_frame, text="Прогресс обучения:", font=("Arial", 9, "bold")).pack(anchor=tk.W)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(fill=tk.X, pady=2)

        self.progress_label = ttk.Label(progress_frame, text="Ожидание начала обучения...", font=("Arial", 9))
        self.progress_label.pack(anchor=tk.W, pady=2)

        self.progress_percent_label = ttk.Label(progress_frame, text="0%", font=("Arial", 12, "bold"), foreground="blue")
        self.progress_percent_label.pack(anchor=tk.W)

        params_frame = ttk.LabelFrame(right_frame, text="Параметры обучения", padding="10")
        params_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(params_frame, text="Скорость обучения:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lr_var = tk.StringVar(value="0.1")
        ttk.Entry(params_frame, textvariable=self.lr_var, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(params_frame, text="(рекомендуется: 0.1)", font=("Arial", 8), foreground="gray").grid(row=0, column=2, sticky=tk.W, padx=2)

        ttk.Label(params_frame, text="Количество эпох:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.epochs_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.epochs_var, width=10).grid(row=1, column=1, padx=5)

        # Возвращенные поля батчей и потоков (как на скриншоте у однокурсника)
        ttk.Label(params_frame, text="Размер батча:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.batch_size_var = tk.StringVar(value="32")
        ttk.Entry(params_frame, textvariable=self.batch_size_var, width=10).grid(row=2, column=1, padx=5)

        ttk.Label(params_frame, text="Количество потоков:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.num_threads_var = tk.StringVar(value="4")
        ttk.Entry(params_frame, textvariable=self.num_threads_var, width=10).grid(row=3, column=1, padx=5)

        data_frame = ttk.LabelFrame(right_frame, text="Обучающая выборка", padding="10")
        data_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.dataset_size_label = ttk.Label(data_frame, text="")
        self.dataset_size_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Button(data_frame, text="Загрузить из CSV", command=self.load_csv).grid(row=1, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(data_frame, text="Сохранить в CSV", command=self.save_csv).grid(row=2, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(data_frame, text="Просмотр выборки", command=self.view_dataset).grid(row=3, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))

        training_log_frame = ttk.LabelFrame(right_frame, text="Журнал обучения", padding="10")
        training_log_frame.grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.training_log = scrolledtext.ScrolledText(
            training_log_frame,
            height=10,
            width=40,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Courier", 9)
        )
        self.training_log.pack(fill=tk.BOTH, expand=True)

        ttk.Button(training_log_frame, text="Очистить журнал", command=self.clear_training_log).pack(pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        if self.drawing:
            self.canvas.create_line(
                self.last_x, self.last_y,
                event.x, event.y,
                width=12, fill="black", capstyle=tk.ROUND  # Поставили width=12 вместо 8
            )
            self.update_grid(event.x, event.y)
            self.last_x = event.x
            self.last_y = event.y

    def update_grid(self, x, y):
        # Аккуратно переводим координаты мыши с холста 256х256 в матрицу 64х64
        grid_x = int((x / self.canvas_size) * self.image_size)
        grid_y = int((y / self.canvas_size) * self.image_size)
        grid_x = max(0, min(self.image_size - 1, grid_x))
        grid_y = max(0, min(self.image_size - 1, grid_y))

        # Закрашиваем кистью точку и соседние пиксели для плотности линии
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = grid_x + dx, grid_y + dy
                if 0 <= nx < self.image_size and 0 <= ny < self.image_size:
                    self.grid[ny][nx] = 1


    def stop_drawing(self, event):
        self.drawing = False

    def clear_canvas(self):
        self.canvas.delete("all")
        self.grid = [[0 for _ in range(self.image_size)] for _ in range(self.image_size)]
        self.result_label.config(text="Нарисуйте геометрическую фигуру")
        self.probability_label.config(text="")

    def canvas_to_pixels_simple(self):
        pixels = []
        for row in self.grid:
            # Прямая передача: то, что нарисовано (1), инвертируем под белый фон датасета (0 - линия, 1 - фон)
            pixels.extend([1.0 - float(p) for p in row])

        pixels_array = np.array(pixels, dtype=np.float32).reshape(self.image_size, self.image_size)
        return pixels_array.flatten().tolist()

    def recognize(self):
        if self.network is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте и обучите нейронную сеть!")
            return

        pixels = self.canvas_to_pixels_simple()
        try:
            probabilities = self.network.predict_proba(pixels)
            predicted_class_idx = self.network.predict(pixels)

            if predicted_class_idx < len(self.data_loader.classes):
                predicted_class = self.data_loader.classes[predicted_class_idx]
                confidence = probabilities[predicted_class_idx] * 100

                self.result_label.config(text=f"Распознано: {predicted_class}")
                self.probability_label.config(text=f"Уверенность: {confidence:.2f}%")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при распознавании: {str(e)}")

    def add_to_dataset(self):
        pixels = self.canvas_to_pixels_simple()
        label = simpledialog.askstring("Добавление примера", "Введите метку класса:")
        if label:
            self.data_loader.add_sample(pixels, label)
            self.update_dataset_info()
            messagebox.showinfo("Успех", f"Пример добавлен с меткой: {label}")

    def create_network(self):
        if len(self.data_loader.classes) == 0:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные!")
            return

        input_size = self.image_size * self.image_size  # 64 * 64 = 4096
        hidden_sizes = [128, 64]
        output_size = len(self.data_loader.classes)

        self.network = NeuralNetwork(input_size, hidden_sizes, output_size)

        arch = self.network.get_architecture()
        self.arch_label.config(
            text=f"Вход: {arch['input_size']}, Скрытые: {arch['hidden_layers']}, Выход: {arch['output_size']}"
        )
        messagebox.showinfo("Успех", "Нейронная сеть создана!")

    def train_network(self):
        if self.is_training:
            messagebox.showwarning("Предупреждение", "Обучение уже выполняется!")
            return

        if self.network is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте нейронную сеть!")
            return

        if len(self.data_loader.dataset) == 0:
            messagebox.showwarning("Предупреждение", "Нет данных для обучения!")
            return

        try:
            self.learning_rate = float(self.lr_var.get())
            self.epochs = int(self.epochs_var.get())
            self.batch_size = int(self.batch_size_var.get())
            self.num_threads = int(self.num_threads_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные параметры обучения!")
            return

        train_data, test_data = self.data_loader.get_training_data()

        self.clear_training_log()
        self.progress_var.set(0)
        self.progress_percent_label.config(text="0%", foreground="blue")
        self.progress_label.config(text="Обучение...")

        self.is_training = True
        self.train_button.config(state=tk.DISABLED, text="Обучение...")

        training_thread = threading.Thread(
            target=self._train_network_thread,
            args=(train_data, test_data),
            daemon=True
        )
        training_thread.start()

    def _train_network_thread(self, train_data, test_data):
        try:
            def progress_callback(epoch, total_epochs, train_error, train_acc, val_error, val_acc, is_finished):
                self.root.after(0, self._update_training_progress, epoch, total_epochs, train_error, train_acc, is_finished)

            history = self.network.train(
                train_data,
                self.epochs,
                self.learning_rate,
                progress_callback=progress_callback,
                batch_size=self.batch_size,
                num_threads=self.num_threads
            )

            if test_data and len(test_data) > 0:
                self.root.after(0, self._evaluate_test_set, test_data)

            final_error = history['train_errors'][-1] if history['train_errors'] else 0
            self.root.after(0, lambda: messagebox.showinfo("Успех", f"Обучение завершено!\nФинальная ошибка: {final_error:.6f}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при обучении: {str(e)}"))
        finally:
            self.root.after(0, self._training_finished)

    def _training_finished(self):
        self.is_training = False
        self.train_button.config(state=tk.NORMAL, text="Обучить сеть")

    def _update_training_progress(self, epoch, total_epochs, train_error, train_acc, is_finished):
        progress = (epoch / total_epochs) * 100 if total_epochs > 0 else 0
        self.progress_var.set(progress)
        self.progress_percent_label.config(text=f"{progress:.1f}%", foreground="blue")

        if is_finished:
            self.progress_label.config(text="Обучение завершено!")
            self.progress_percent_label.config(text="100%", foreground="green")
        else:
            self.progress_label.config(text=f"Эпоха {epoch}/{total_epochs} | Ошибка: {train_error:.4f} | Точность: {train_acc:.2f}%")

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] Эпоха {epoch:4d}/{total_epochs} | Ошибка: {train_error:.6f} | Точность: {train_acc:5.2f}%"
        self._append_to_log(log_message)

    def _evaluate_test_set(self, test_data):
        try:
            metrics = Metrics.evaluate_model(self.network, test_data, self.data_loader.classes)
            Metrics.print_metrics(metrics, self.data_loader.classes)
            self._show_metrics_window(metrics)
        except Exception as e:
            self._append_to_log(f"Ошибка при вычислении метрик: {str(e)}\n")

    def _append_to_log(self, message):
        self.training_log.config(state=tk.NORMAL)
        self.training_log.insert(tk.END, message + "\n")
        self.training_log.see(tk.END)
        self.training_log.config(state=tk.DISABLED)

    def clear_training_log(self):
        self.training_log.config(state=tk.NORMAL)
        self.training_log.delete(1.0, tk.END)
        self.training_log.config(state=tk.DISABLED)

    def save_network(self):
        if self.network is None:
            messagebox.showwarning("Предупреждение", "Нет сети для сохранения!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
        if filename:
            try:
                data = {'network': self.network, 'classes': self.data_loader.classes}
                with open(filename, 'wb') as f:
                    pickle.dump(data, f)
                messagebox.showinfo("Успех", "Сеть сохранена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

    def load_network(self):
        filename = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if filename:
            try:
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                self.network = data['network']
                self.data_loader.classes = data['classes']
                messagebox.showinfo("Успех", "Сеть загружена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")

    def visualize_architecture(self):
        if self.network is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте нейронную сеть!")
            return
        messagebox.showinfo("Информация", "Архитектура: Вход (4096) -> Скрытые слои -> Выход с Softmax")

    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                self.data_loader.load_from_csv(filename)
                self.update_dataset_info()
                messagebox.showinfo("Успех", "Данные загружены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")

    def save_csv(self):
        if len(self.data_loader.dataset) == 0:
            messagebox.showwarning("Предупреждение", "Нет данных!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if filename:
            self.data_loader.save_to_csv(filename)
            messagebox.showinfo("Успех", "Сохранено!")

    def view_dataset(self):
        if len(self.data_loader.dataset) == 0:
            messagebox.showwarning("Предупреждение", "Нет данных!")
            return
        view_window = tk.Toplevel(self.root)
        view_window.title("Выборка")
        view_window.geometry("400x300")
        listbox = tk.Listbox(view_window)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for i, item in enumerate(self.data_loader.dataset):
            listbox.insert(tk.END, f"{i + 1}. Метка: {item['label']}")

    def load_default_dataset(self):
        possible_paths = [
            os.path.join("datasets", "datasets.csv"),
            os.path.join("lab5", "datasets", "datasets.csv"),
            os.path.join(os.path.dirname(__file__), "datasets", "datasets.csv")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    self.data_loader.load_from_csv(path)
                    self.update_dataset_info()
                    return
                except Exception:
                    pass

    def _show_metrics_window(self, metrics):
        metrics_window = tk.Toplevel(self.root)
        metrics_window.title("Метрики качества")
        metrics_window.geometry("500x400")
        text_area = scrolledtext.ScrolledText(metrics_window, wrap=tk.WORD, font=("Courier", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, f"Точность (Accuracy): {metrics['accuracy'] * 100:.2f}%\n")
        text_area.config(state=tk.DISABLED)

    def update_dataset_info(self):
        count = len(self.data_loader.dataset)
        classes = len(self.data_loader.classes)
        self.dataset_size_label.config(text=f"Примеров: {count}, Классов: {classes}")

def main():
    root = tk.Tk()
    app = CurrencyRecognizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()