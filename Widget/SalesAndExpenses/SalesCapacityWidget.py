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


class SalesCapacityWidget(QFrame):
    def __init__(self):
        super().__init__()
        # 1. Настройка шрифтов
        self.title_font = QFont("Times New Roman", 14, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.msg_font = QFont("Times New Roman", 12)

        self.product_labels = {}  # Здесь будем хранить QLabel-ы с названиями
        self.last_known_names = [f"Продукт {i}" for i in range(1, 21)]  # Запасной список имен

        # 2. Стиль контейнера
        self.setStyleSheet(
            "QFrame#CapacityContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")
        self.setObjectName("CapacityContainer")
        self.setFixedWidth(800)
        self.setFixedHeight(350)

        # Основной лейаут виджета
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Коэффициент мощности продаж, %")
        title.setFont(self.title_font)
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3. СОЗДАЕМ СКРОЛЛ (сначала создаем, потом стилизуем!)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Красивый стиль скроллбара
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F8FF;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #B9D9EB;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A1C9DE;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Контент внутри скролла
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: white;")
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(10, 10, 20, 10)  # Отступ справа для скроллбара
        self.grid.setColumnMinimumWidth(0, 150)

        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
        self.stored_data = {}
        # Данные
        self.years = ["2026"]
        self.inputs = {}
        self.num_validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))

        # Первичная инициализация колонок
        self.update_years("2026", 0, "1")

    def update_product_names(self, names_list):
        """Метод вызывается сигналом из таблицы товаров"""
        self.last_known_names = names_list  # Запоминаем имена на случай перерисовки лет
        for i, name in enumerate(names_list, 1):
            if i in self.product_labels:
                self.product_labels[i].setText(name)
                # Также обновляем внутреннее имя для окон ошибок
                for year in self.years:
                    key = f"cap_{i}_{year}"
                    if key in self.inputs:
                        self.inputs[key].setProperty("name", f"{name} ({year})")

    def _create_edit(self, default_val, name, product_row, year):
        """Создание поля ввода с расширенной стилизацией (как в Seasonality)"""
        # Проверка сохраненных данных
        current_val = self.stored_data.get((product_row, year), default_val)

        le = QLineEdit(str(current_val).replace('.', ','))
        le.setValidator(self.num_validator)
        le.setFont(self.input_font)
        le.setFixedSize(80, 35)  # Высота чуть больше для удобства ввода
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ПРИМЕНЯЕМ СТИЛЬ ИЗ SeasonalityWidget
        le.setStyleSheet("""
            QLineEdit {
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                background-color: #E0F7FF; 
                color: #0066CC; 
                padding: 2px;
            }
            QLineEdit:focus {
                border: 2px solid #0066CC; 
                background-color: white;
            }
            /* Эффект при наведении курсора */
            QLineEdit:hover {
                border: 2px solid #0066CC; 
            }
        """)

        # Сохраняем свойства
        le.setProperty("default", default_val)
        le.setProperty("name", name)
        le.setProperty("product_row", product_row)
        le.setProperty("year", year)

        le.editingFinished.connect(lambda field=le: self.validate_input(field))
        return le
    def validate_input(self, le):
        """Проверка: от 0 до 100% и сохранение в хранилище"""
        text = le.text().replace(',', '.')
        product_row = le.property("product_row")
        year = le.property("year")
        default = le.property("default")

        try:
            if not text: raise ValueError
            val = float(text)
            if not (0 <= val <= 100): raise ValueError

            # СОХРАНЯЕМ ВЕРНОЕ ЗНАЧЕНИЕ
            self.stored_data[(product_row, year)] = f"{val:.0f}"
            le.setText(f"{val:.0f}")

        except ValueError:
            self.show_error(le.property("name"), default)
            # Возвращаем дефолт в хранилище при ошибке
            self.stored_data[(product_row, year)] = default
            le.setText(default)

    def show_error(self, name, default):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(self.msg_font)
        msg.setText(f"Параметр: <b>{name}</b><br><br>Введите значение от 0 до 100.<br>Восстановлено: {default}%")
        msg.setStyleSheet("""
            QMessageBox QLabel { min-width: 400px; color: #333333; }
            QPushButton { 
                min-width: 80px; padding: 5px; background-color: #E0F7FF; 
                border: 1px solid #87CEFA; border-radius: 5px; 
            }
        """)
        msg.exec()

    def update_years(self, start_year, start_month_idx, duration_years):
        """Обновление колонок без потери данных"""
        try:
            y, m = int(start_year), int(start_month_idx) + 1
            unique_years = []
            curr_y, curr_m = y, m
            for _ in range(int(duration_years) * 12):
                if curr_y not in unique_years: unique_years.append(curr_y)
                curr_m += 1
                if curr_m > 12: curr_m = 1; curr_y += 1

            self.years = [str(yr) for yr in unique_years]

            # Очистка сетки
            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)

            self.product_labels = {}
            self.inputs = {} # Очищаем словарь активных виджетов

            # Отрисовка заголовков лет
            for col, year in enumerate(self.years):
                lbl = QLabel(year)
                lbl.setFont(self.label_font)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("font-weight: bold; background: #D0E6F5; border-radius: 5px; padding: 5px;")
                self.grid.addWidget(lbl, 0, col + 1)

            for row in range(1, 21):
                prod_name = self.last_known_names[row - 1]
                p_lbl = QLabel(prod_name)
                p_lbl.setFont(self.label_font)
                p_lbl.setStyleSheet("font-style: italic; color: #555555; border: none;")
                self.grid.addWidget(p_lbl, row, 0)
                self.product_labels[row] = p_lbl

                for col, year in enumerate(self.years):
                    # ВАЖНО: передаем 4 аргумента: дефолт, имя, номер строки и год
                    le = self._create_edit("100", f"{prod_name} ({year})", row, year)
                    self.grid.addWidget(le, row, col + 1)
                    self.inputs[f"cap_{row}_{year}"] = le

            self.grid.setColumnStretch(len(self.years) + 1, 10)

        except Exception as e:
            print(f"Ошибка CapacityWidget: {e}")

    def get_all_capacity_coefficients(self):
        """Возвращает коэффициенты мощности для всех лет и продуктов в виде {год: [список_коэф]}"""
        result = {}
        for year in self.years:
            year_ks = []
            for row in range(1, 21):
                key = f"cap_{row}_{year}"
                if key in self.inputs:
                    text = self.inputs[key].text().replace(',', '.')
                    try:
                        # Делим на 100, так как в расчетах нужен коэффициент (0.8), а вводим % (80)
                        val = float(text) / 100.0
                    except:
                        val = 1.0
                    year_ks.append(val)
                else:
                    year_ks.append(1.0)
            result[year] = year_ks
        return result


# Добавьте это в конец класса SalesCapacityWidget
    def get_data(self):
        """
        Псевдоним для метода get_all_capacity_coefficients.
        Необходим для корректной работы синхронизации в main.py.
        """
        return self.get_all_capacity_coefficients()