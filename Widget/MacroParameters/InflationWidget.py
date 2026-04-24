
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
class InflationWidget(QFrame):
    data_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.stored_data = {}
        # Шрифты как в Налогах
        self.title_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        self.setStyleSheet("""
            QFrame#MacroContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)
        self.setObjectName("MacroContainer")

        # Устанавливаем ширину 700, как в виджете налогов
        self.setFixedWidth(700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок("Макроэкономические показатели")
        title = QLabel("Инфляция по годам", self)
        title.setFont(self.title_font)
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Сетка для данных
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setHorizontalSpacing(5)
        # Устанавливаем фиксированную ширину для первой колонки с текстом
        self.grid.setColumnMinimumWidth(0, 160)
        self.grid.setColumnStretch(0, 0)

        layout.addLayout(self.grid)

        # Хранилище для полей ввода
        self.inputs = {}

    def update_years(self, start_year, start_month_idx, duration_years):
        """Динамическое создание колонок инфляции"""
        # 1. Очистка старых данных
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # КЛЮЧЕВОЙ МОМЕНТ: Фиксируем ширину первой колонки сразу после очистки
        # Это гарантирует старт ячеек со 161-го пикселя, как в налогах
        self.grid.setColumnMinimumWidth(0, 160)
        self.grid.setColumnStretch(0, 0)

        # 2. Логика расчета лет (без изменений)
        try:
            y = int(start_year)
            m = int(start_month_idx) + 1
            d_years = int(duration_years)
            total_months = d_years * 12
            unique_years = []
            curr_y = y
            curr_m = m
            for _ in range(total_months):
                if curr_y not in unique_years:
                    unique_years.append(curr_y)
                curr_m += 1
                if curr_m > 12:
                    curr_m = 1
                    curr_y += 1
            years_list = unique_years
        except:
            return

        # 3. Создание подписи строки (Инфляция)
        label_inf = QLabel("Инфляция, %")
        label_inf.setFont(self.label_font)
        label_inf.setStyleSheet("font-style: italic; color: #555555; background: transparent; border: none;")
        # Добавляем AlignLeft, чтобы текст не центрировался в широкой колонке
        self.grid.addWidget(label_inf, 1, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # 4. Создание колонок для каждого года
        self.inputs = {}
        for col, year in enumerate(years_list):
            year_str = str(year)
            # Год
            year_label = QLabel(str(year))
            year_label.setFont(self.label_font)
            year_label.setFixedSize(80, 28)  # Фиксация размера как в налогах
            year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            year_label.setStyleSheet("""
                font-weight: bold; color: #333333; background: #D0E6F5; 
                border-radius: 5px; padding: 2px;
            """)
            # Добавляем в строку 0, колонка col + 1 (начало с индекса 1)
            self.grid.addWidget(year_label, 0, col + 1, Qt.AlignmentFlag.AlignLeft)
            current_val = self.stored_data.get(year_str, "10")
            # Поле ввода
            line_edit = QLineEdit(str(current_val).replace('.', ','))
            line_edit.setFont(self.input_font)
            line_edit.setFixedSize(80, 35)
            line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

            line_edit.setStyleSheet("""
                            QLineEdit {
                                border: 2px solid #87CEFA; 
                                border-radius: 8px; 
                                background-color: #E0F7FF; 
                                color: #0066CC;
                                padding: 2px;
                            }
                            /* Эффект при клике (нажатии) */
                            QLineEdit:focus {
                                border: 2px solid #0066CC; /* Темно-синий контур */
                                background-color: white;   /* Белый фон */
                            }
                            /* Эффект при наведении курсора */
                            QLineEdit:hover {
                                border: 2px solid #0066CC; /* Чуть темнее основного голубого */
                                
                            }
                        """)
            line_edit.setProperty("year", year_str)
            line_edit.editingFinished.connect(self.validate_inflation)

            # Добавляем строго по левому краю ячейки
            self.grid.addWidget(line_edit, 1, col + 1, Qt.AlignmentFlag.AlignLeft)
            self.inputs[year_str] = line_edit

        # 5. РАСПРЕДЕЛЕНИЕ МЕСТА
        # Сбрасываем старые растяжения
        # for i in range(1, self.grid.columnCount()):
        #     self.grid.setColumnStretch(i, 0)

        # Устанавливаем растяжение для ячеек данных
        for col_idx in range(1, len(years_list) + 1):
            self.grid.setColumnStretch(col_idx, 1)
        self.grid.setColumnStretch(len(years_list) + 1, 10)

        # Добавляем "пружину" в конце
        self.grid.setColumnStretch(len(years_list) + 1, 10)

    def validate_inflation(self):
        """Проверка ввода инфляции: от 0 до 40% с обновленным стилем"""
        line_edit = self.sender()
        text_raw = line_edit.text().strip()

        # Убираем лишние разделители в конце
        if text_raw.endswith(',') or text_raw.endswith('.'):
            text_raw = text_raw[:-1]

        text = text_raw.replace(',', '.')
        year = line_edit.property("year")

        max_val = 40.0
        min_val = 0.0
        default = "10"  # Значение по умолчанию для инфляции

        try:
            if not text: raise ValueError
            value = float(text)
            if value < min_val or value > max_val: raise ValueError

            # Форматирование для красоты (убираем .0, если число целое)
            clean_val = str(int(value)) if value == int(value) else text.replace('.', ',')

            self.stored_data[year] = clean_val
            line_edit.setText(clean_val.replace('.', ','))
            self.data_changed.emit()

        except ValueError:
            # Вызов обновленного окна ошибки
            self.show_error(year, default, max_val)

            # Восстановление значения по умолчанию
            line_edit.setText(default.replace('.', ','))
            self.stored_data[year] = default
            self.data_changed.emit()

    def show_error(self, year, default, max_val):
        """Обновленное окно ошибки для инфляции в стиле TaxesWidget"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(self.label_font)

        # Формируем текст по вашему шаблону
        error_text = (
            f"Параметр <b>Инфляция</b> (год <b>{year}</b>) указан некорректно.<br><br>"
            f"Допустимый диапазон: от <b>0</b> до <b>{int(max_val)}%</b>.<br>"
            f"Буквы и символы не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию: <b>{default}</b>"
        )

        msg.setText(error_text)

        # Применяем единую стилизацию кнопок и меток
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

    def get_inflation_for_year(self, year):
        """Возвращает значение инфляции для конкретного года (числом)"""
        try:
            # Ищем поле ввода для конкретного года
            if year in self.inputs:
                text = self.inputs[year].text().replace(',', '.')
                return float(text)
            # Если года нет в списке (например, проект на 5 лет, а макро на 1)
            # Берем последнее доступное значение или 10% по умолчанию
            elif self.inputs:
                last_year = max(self.inputs.keys())
                return float(self.inputs[last_year].text().replace(',', '.'))
            return 10.0
        except:
            return 10.0

    # Добавьте это в конец класса MacroeconomicsWidget
    def get_inflation_map(self):
        """Теперь берет данные из памяти, если виджеты еще не созданы"""
        inflation_map = {}
        # Сначала пробуем взять из живых полей (самые свежие)
        if self.inputs:
            for year, le in self.inputs.items():
                try:
                    val = float(le.text().replace(',', '.'))
                    inflation_map[str(year)] = val / 100.0
                except:
                    continue
        # Если полей нет, берем из сохраненного словаря
        elif self.stored_data:
            for year, val_str in self.stored_data.items():
                try:
                    val = float(val_str.replace(',', '.'))
                    inflation_map[str(year)] = val / 100.0
                except:
                    continue

        return inflation_map if inflation_map else {"default": 0.10}