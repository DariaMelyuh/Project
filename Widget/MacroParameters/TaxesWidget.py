import sys
import math
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QRegularExpressionValidator, QColor, QBrush
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
QSizePolicy
)
from PyQt6.QtGui import QFont, QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFrame, QLabel,
    QAbstractItemView, QHeaderView ,QPushButton
)

class TaxesWidget(QFrame):
    data_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        # Шрифты интерфейса (сохранено)
        self.title_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.msg_font = QFont("Times New Roman", 12)
        self.stored_data = {}
        self.setStyleSheet(
            "QFrame#TaxContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")
        self.setObjectName("TaxContainer")
        # Увеличиваем ширину, так как теперь таблица горизонтальная
        self.setFixedWidth(700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Налоговые ставки")
        title.setFont(self.title_font)


        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setHorizontalSpacing(5)
        self.grid.setColumnMinimumWidth(0, 160)
        self.grid.setColumnStretch(0, 0)

        # По умолчанию ставим параметры запуска
        self.years = ["2026"]
        self.inputs = {}
        self.num_validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))

        # Первичная отрисовка (для Января 2026, 1 год)
        self.update_years("2026", 0, "1")

        layout.addLayout(self.grid)

        # --- Создаем заголовки (Года) ---
        for col, year in enumerate(self.years):
            year_label = QLabel(year)
            year_label.setFont(self.label_font)
            year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            year_label.setStyleSheet(
                "font-weight: bold; color: #333333; background: #D0E6F5; border-radius: 5px; padding: 5px;")
            self.grid.addWidget(year_label, 0, col + 1)

        # --- 1. Строка УСН ---
        self._add_tax_row("УСН, %", "15", row=1, per_year=True)

        # --- 2. Строка Социальные взносы ---
        # Здесь одна ячейка на все года (объединяем колонки)
        self._add_tax_row("Социальные взносы, %", "30", row=2, per_year=False)

        # --- 3. Строка НДС ---
        self._add_tax_row("Налог на добавленную стоимость, %", "0", row=3, per_year=True)

        layout.addLayout(self.grid)

    def _create_edit(self, default_val, tax_name, year=None):
        """Вспомогательный метод для создания стилизованного поля ввода"""
        # Ключ должен быть идентичен тому, что в validate_tax_input
        storage_key = f"{tax_name}_{year}" if year else tax_name

        # ПРОВЕРЯЕМ: если данные уже есть в памяти — берем их, иначе дефолт
        current_val = self.stored_data.get(storage_key, default_val)

        # Устанавливаем актуальное значение в поле
        line_edit = QLineEdit(str(current_val).replace('.', ','))
        line_edit.setValidator(self.num_validator)
        line_edit.setFont(self.input_font)

        line_edit.setMinimumWidth(60)
        line_edit.setMaximumWidth(100)
        line_edit.setFixedHeight(35)

        line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                padding: 5px; 
                background-color: #E0F7FF; 
                color: #0066CC;
            }
            QLineEdit:focus {
                border: 2px solid #0066CC;
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #0066CC;
            }
        """)

        line_edit.setProperty("default", default_val)
        line_edit.setProperty("tax_name", tax_name)
        line_edit.setProperty("year", year)
        # Сохраняем ключ в свойство, чтобы валидатор его видел
        line_edit.setProperty("storage_key", storage_key)

        line_edit.editingFinished.connect(lambda le=line_edit: self.validate_tax_input(le))
        return line_edit
    def _add_tax_row(self, name, default_val, row, per_year=True):
        label = QLabel(name)
        label.setFont(self.label_font)
        label.setStyleSheet("font-style: italic; color: #555555; background: transparent; border: none;")
        self.grid.addWidget(label, row, 0)

        if per_year:
            for col, year_text in enumerate(self.years):
                le = self._create_edit(default_val, name, year_text)
                self.grid.addWidget(le, row, col + 1, Qt.AlignmentFlag.AlignLeft)
                self.inputs[f"{name}_{year_text}"] = le
        else:
            # Для социальных взносов (одна ячейка на все года)
            le = self._create_edit(default_val, name)
            column_count = len(self.years)
            self.grid.addWidget(le, row, 1, 1, column_count)
            le.setMaximumWidth(16777215)
            self.inputs[name] = le

    def validate_tax_input(self, line_edit):
        """Проверка ввода и сохранение в память с обновленным стилем ошибок"""
        text_raw = line_edit.text().strip()
        # Убираем лишние разделители в конце
        if text_raw.endswith(',') or text_raw.endswith('.'):
            text_raw = text_raw[:-1]

        text = text_raw.replace(',', '.')
        default = line_edit.property("default")
        tax_name = line_edit.property("tax_name")
        year = line_edit.property("year")
        storage_key = line_edit.property("storage_key")

        max_val = 50.0
        min_val = 0.0

        try:
            if not text: raise ValueError
            value = float(text)
            if value < min_val or value > max_val: raise ValueError

            # Форматирование для красоты (убираем .0)
            clean_val = str(int(value)) if value == int(value) else text.replace('.', ',')

            self.stored_data[storage_key] = clean_val
            line_edit.setText(clean_val.replace('.', ','))
            self.data_changed.emit()

        except ValueError:
            # Подготавливаем значение по умолчанию для восстановления
            def_val_float = float(str(default).replace(',', '.'))
            clean_def = str(int(def_val_float)) if def_val_float == int(def_val_float) else str(default)

            # Вызов обновленного окна ошибки
            self.show_error(tax_name, year, clean_def, max_val)

            # Восстановление значения
            line_edit.setText(clean_def.replace('.', ','))
            self.stored_data[storage_key] = clean_def.replace('.', ',')

    def show_error(self, tax_name, year, default, max_val):
        """Обновленное окно ошибки с кнопкой и расширенным текстом"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(self.label_font)  # Используем шрифт меток для текста

        display_name = f"<b>{tax_name}</b>"
        if year:
            display_name += f" (год <b>{year}</b>)"

        error_text = (
            f"Параметр {display_name} указан некорректно.<br><br>"
            f"Допустимый диапазон: от <b>0</b> до <b>{int(max_val)}%</b>.<br>"
            f"Буквы и символы не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию: <b>{default}</b>"
        )

        msg.setText(error_text)

        # Стилизация в стиле SeasonalityWidget (кнопки и отступы)
        msg.setStyleSheet("""
            QMessageBox QLabel { 
                color: #333333; 
                min-width: 500px; 
            }
            QPushButton { 
                font-family: 'Times New Roman'; 
                font-size: 14px; 
                min-width: 100px; 
                padding: 6px; 
                background-color: #E0F7FF;
                border: 2px solid #87CEFA;
                border-radius: 8px;
                color: #0066CC;
            }
            QPushButton:hover { 
                background-color: #B9D9EB; 
                border: 2px solid #0066CC;
            }
        """)
        msg.exec()

    def update_years(self, start_year, start_month_idx, duration_years):
        try:
            y, m = int(start_year), int(start_month_idx) + 1
            unique_years = []
            curr_y, curr_m = y, m
            for _ in range(int(duration_years) * 12):
                if curr_y not in unique_years: unique_years.append(curr_y)
                curr_m += 1
                if curr_m > 12: curr_m = 1; curr_y += 1

            self.years = [str(yr) for yr in unique_years]
            self.clear_grid_data()
            self.inputs = {} # Важно очищать ссылки на старые виджеты

            for col, year_text in enumerate(self.years):
                year_label = QLabel(year_text)
                year_label.setFont(self.label_font)
                year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                year_label.setStyleSheet("font-weight: bold; background: #D0E6F5; border-radius: 5px; padding: 5px;")
                self.grid.addWidget(year_label, 0, col + 1)

            # Перерисовываем строки (теперь они подхватят данные из stored_data)
            self._add_tax_row("УСН, %", "15", row=1, per_year=True)
            self._add_tax_row("Социальные взносы, %", "30", row=2, per_year=False)
            self._add_tax_row("Налог на добавленную стоимость, %", "0", row=3, per_year=True)

            for col in range(1, len(self.years) + 1):
                self.grid.setColumnStretch(col, 1)
            self.grid.setColumnStretch(len(self.years) + 1, 10)

        except Exception as e:
            print(f"Ошибка TaxesWidget: {e}")

    def clear_grid_data(self):
        for i in reversed(range(self.grid.count())):
            pos = self.grid.getItemPosition(i)
            if pos[1] > 0:
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)

    def get_tax_rates_by_year(self):
        rates = {}
        for y in self.years:
            key = f"УСН, %_{y}"
            # Берем из stored_data, если нет - берем дефолт 15
            val = self.stored_data.get(key, "15")
            rates[str(y)] = float(str(val).replace(',', '.')) / 100
        return rates

    def get_vat_rates_by_year(self):
        """Возвращает словарь {год: ставка_НДС_десятичная}"""
        rates = {}
        for year_str in self.years:
            # Ключ формируется в _add_tax_row: "Название_Год"
            key = f"Налог на добавленную стоимость, %_{year_str}"
            if key in self.inputs:
                try:
                    rates[year_str] = float(self.inputs[key].text().replace(',', '.')) / 100
                except:
                    rates[year_str] = 0.0  # Дефолт 0%
        return rates

    def get_vat_rates_by_year(self):
        """Возвращает словарь {год: ставка_НДС_десятичная}"""
        rates = {}
        for year_str in self.years:
            key = f"Налог на добавленную стоимость, %_{year_str}"
            if key in self.inputs:
                try:
                    rates[year_str] = float(self.inputs[key].text().replace(',', '.')) / 100
                except:
                    rates[year_str] = 0.0
        return rates

