import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import Algorithm as alg

class LabApp:
    def __init__(self, master):
        self.master = master
        master.title("Лабораторная работа")

        # === Поля для ввода ===
        self.input_frame = ttk.Frame(master, padding=10)
        self.input_frame.pack()

        # Коэффициент
        ttk.Label(self.input_frame, text="Коэффициент понижения \nогневой мощи противника:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.coefficient_entry = ttk.Entry(self.input_frame, width=10)
        self.coefficient_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.coefficient_entry.insert(0,"2")

        # Размер матрицы
        ttk.Label(self.input_frame, text="Размер матрицы:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_entry = ttk.Entry(self.input_frame, width=10)
        self.size_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.size_entry.insert(0, "3")

        # Минимум
        ttk.Label(self.input_frame, text="Минимум:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.min_entry = ttk.Entry(self.input_frame, width=10)
        self.min_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.min_entry.insert(0, "1")

        # Максимум
        ttk.Label(self.input_frame, text="Максимум:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_entry = ttk.Entry(self.input_frame, width=10)
        self.max_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.max_entry.insert(0, "10")

        # === Матрица ===
        self.matrix_frame = ttk.Frame(master, padding=10)
        self.matrix_frame.pack(fill=tk.BOTH, expand=True)

        # Настройка grid для matrix_frame, чтобы полосы прокрутки занимали все доступное пространство
        self.matrix_frame.grid_rowconfigure(0, weight=1)
        self.matrix_frame.grid_columnconfigure(0, weight=1)

        self.matrix_size = 0
        self.matrix_entries = []
        self.matrix = None

        # Canvas для поддержки полос прокрутки
        self.matrix_canvas = tk.Canvas(self.matrix_frame, borderwidth=0, highlightthickness=0) # Убираем рамку
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew") # Используем grid и sticky

        # Полосы прокрутки
        self.vsb = ttk.Scrollbar(self.matrix_frame, orient="vertical", command=self.matrix_canvas.yview)
        self.vsb.grid(row=0, column=1, sticky="ns")  # Используем grid и sticky
        self.hsb = ttk.Scrollbar(self.matrix_frame, orient="horizontal", command=self.matrix_canvas.xview)
        self.hsb.grid(row=1, column=0, sticky="ew")  # Используем grid и sticky

        # Настройка canvas
        self.matrix_canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.matrix_canvas.bind('<Configure>', self.scroll_function)
        self.matrix_canvas.bind_all("<MouseWheel>", self._on_mousewheel) # Добавляем поддержку скролла мышью


        # Фрейм для матрицы (внутри canvas)
        self.matrix_inner_frame = ttk.Frame(self.matrix_canvas)
        self.window_id = self.matrix_canvas.create_window((0, 0), window=self.matrix_inner_frame, anchor="nw")

        # Привязываем изменение размера внутреннего фрейма к обновлению области прокрутки
        self.matrix_inner_frame.bind("<Configure>", self.scroll_function)

        # Кнопки для управления матрицей
        self.matrix_button_frame = ttk.Frame(self.matrix_inner_frame)
        self.matrix_button_frame.grid(row=0, column=0, columnspan=2, pady=5)

        button_frame = ttk.Frame(self.input_frame) # Добавляем фрейм для кнопок
        button_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=5) # columnspan чтобы растянуть на всю ширину

        self.create_button = ttk.Button(button_frame, text="Создать матрицу", command=self.create_matrix)
        self.auto_button = ttk.Button(button_frame, text="Автозаполнение", command=self.auto_populate_matrix)
        self.calculate_button = ttk.Button(button_frame, text="Вычислить", command=self.calculate)

        self.create_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))  # Левый отступ только у первой кнопки
        self.auto_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.calculate_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # === Таблица вывода результата ===
        self.result_frame = ttk.Frame(master, padding=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

    def scroll_function(self, event=None):
        self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Добавляем поддержку скролла мышью"""
        self.matrix_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_matrix(self):
        """Создает матрицу Entry виджетов."""
        try:
            self.matrix_size = int(self.size_entry.get())
            if self.matrix_size <= 0:
                raise ValueError("Размер матрицы должен быть положительным целым числом.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        # Очищаем старую матрицу
        for widget in self.matrix_inner_frame.winfo_children():
            widget.destroy()

        # Кнопки управления матрицей (пересоздаем, чтобы не дублировались)
        self.matrix_entries = []
        self.matrix = np.zeros((self.matrix_size, self.matrix_size))

        for i in range(self.matrix_size):
            row_entries = []
            for j in range(self.matrix_size):
                entry = tk.Entry(self.matrix_inner_frame, width=5) #  Используем tk.Entry
                entry.grid(row=i + 1, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

        # Обновляем scrollregion canvas
        self.scroll_function()

    def auto_populate_matrix(self):
        """Автоматически заполняет матрицу случайными числами."""
        if not self.matrix_entries:
            messagebox.showinfo("Внимание", "Сначала создайте матрицу.")
            return

        try:
            for i in range(self.matrix_size):
                for j in range(self.matrix_size):
                    self.matrix_entries[i][j].delete(0, tk.END)
                    self.matrix_entries[i][j].insert(0, str(np.random.randint(self.min_entry.get(), self.max_entry.get())))
        except AttributeError:
            messagebox.showerror("Ошибка", "Сначала создайте матрицу.")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные значения для генерации.")

        # Обновляем scrollregion canvas
        self.scroll_function()

    def calculate(self):
        """Обработчик нажатия кнопки "Вычислить"."""
        try:
            coefficient = float(self.coefficient_entry.get())
            matrix_values = []
            for i in range(self.matrix_size):
                row_values = []
                for j in range(self.matrix_size):
                    try:
                        value = float(self.matrix_entries[i][j].get())
                        row_values.append(value)
                    except ValueError:
                        messagebox.showerror("Ошибка", "Некорректный ввод в матрице.  Пожалуйста, введите числа.")
                        return
                matrix_values.append(row_values)
            matrix = np.array(matrix_values)
            (sigma1, sigma2), smax, s = alg.find_optimal_pair(matrix, float(self.coefficient_entry.get()))

            # Генерируем матрицу из нулей и единиц
            binary_matrix = np.zeros((self.matrix_size, self.matrix_size), dtype=int)
            for i in range(self.matrix_size):
                binary_matrix[i][sigma1[i]] += 1
                binary_matrix[i][sigma2[i]] += 2

            # Применяем стили к ячейкам в зависимости от значений в binary_matrix
            for i in range(self.matrix_size):
                for j in range(self.matrix_size):
                    if binary_matrix[i][j] == 1:
                        self.matrix_entries[i][j].configure(bg="green3")  # Используем bg для tk.Entry
                    elif binary_matrix[i][j] == 2:
                        self.matrix_entries[i][j].configure(bg="red2")
                    elif binary_matrix[i][j] == 3:
                        self.matrix_entries[i][j].configure(bg="orange")
                    else:
                        self.matrix_entries[i][j].configure(bg="white")  # Возвращаем стандартный цвет фона

            # Очищаем таблицу результатов
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            # Создаем таблицу результатов с помощью grid
            ttk.Label(self.result_frame, text="σ-1").grid(row=0, column=0, padx=5, pady=5)  # Заголовок первого столбца
            ttk.Label(self.result_frame, text="σ-2").grid(row=1, column=0, padx=5, pady=5)

            for i in range(self.matrix_size):
                ttk.Label(self.result_frame, text=str(sigma1[i]+1)).grid(row=0, column=i + 1, padx=5, pady=5)  # Номер
                ttk.Label(self.result_frame, text=str(sigma2[i]+1)).grid(row=1, column=i + 1, padx=5, pady=5)  # Значение
            ttk.Label(self.result_frame, text="Минимальная огневая мощь противника после обстрела:   " + str(s)).grid(row=0, column=self.matrix_size+1, padx=5, pady=5)  # Номер
            ttk.Label(self.result_frame, text="Сумма элементов перестановок:   " + str(smax)).grid(row=1, column=self.matrix_size+1, padx=5, pady=5)  # Значение
            ttk.Label()

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка ввода: {e}")
        except AttributeError as e:
            messagebox.showerror("Ошибка", f"Сначала создайте и заполните матрицу: ggg : {e}")

root = tk.Tk()
root.geometry("800x600")
app = LabApp(root)
root.mainloop()