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
class CAPMWidget(QFrame):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # Для связи с расчетами WACC

        # Шрифты
        self.title_font = QFont("Times New Roman", 14, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.msg_font = QFont("Times New Roman", 12)

        self.setStyleSheet("""
            QFrame#CAPMContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)
        self.setObjectName("CAPMContainer")
        self.setFixedWidth(950)  # Увеличили ширину для таблицы

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Норма доходности собственного капитала (CAPM)")
        title.setFont(self.title_font)
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Сетка для таблицы
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setColumnMinimumWidth(0, 220)  # Ширина под названия параметров
        layout.addLayout(self.grid)
        self.stored_data = {}
        # Данные
        self.years = ["2026"]
        self.inputs = {}  # Хранит объекты QLineEdit
        self.results = {}  # Хранит объекты QLabel с итогом Re
        self.num_validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))

        # Первичная отрисовка
        self.update_years("2026", 0, "1")

    def _create_edit(self, default_val, key, year):
        """Создание стилизованного поля ввода"""
        # 1. Сначала проверяем, есть ли уже сохраненное значение для этой ячейки
        current_val = self.stored_data.get((key, year), default_val)

        # 2. ИСПОЛЬЗУЕМ current_val вместо default_val для текста поля
        le = QLineEdit(str(current_val).replace('.', ','))

        le.setValidator(self.num_validator)
        le.setFont(self.input_font)
        le.setMinimumWidth(80)
        le.setMaximumWidth(100)
        le.setFixedHeight(35)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setStyleSheet("""
            border: 2px solid #87CEFA; border-radius: 8px; 
            padding: 5px; background-color: #E0F7FF; color: #0066CC;
        """)

        # Свойства для валидации
        le.setProperty("key", key)
        le.setProperty("year", year)
        le.setProperty("default", default_val)

        le.editingFinished.connect(lambda field=le: self.validate_and_calculate(field))
        return le
    def _add_capm_row(self, name, key, default_val, row):
        """Добавление строки параметров (Rf, Beta, Rm)"""
        label = QLabel(name)
        label.setFont(self.label_font)
        label.setStyleSheet("font-style: italic; color: #555555; background: transparent; border: none;")
        self.grid.addWidget(label, row, 0)

        for col, year in enumerate(self.years):
            le = self._create_edit(default_val, key, year)
            self.grid.addWidget(le, row, col + 1)
            self.inputs[f"{key}_{year}"] = le

    def _add_result_row(self, row):
        """Добавление строки с итоговым расчетом Re"""
        label = QLabel("Итого (%)")
        label.setFont(self.input_font)
        label.setStyleSheet("color: #333333; background: transparent; border: none;")
        self.grid.addWidget(label, row, 0)

        for col, year in enumerate(self.years):
            res_val = QLabel("0,00")
            res_val.setFont(self.input_font)
            res_val.setFixedSize(100, 35)
            res_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # ИЗМЕНЕНО: border установлен в 2px solid #87CEFA (нежно-голубой)
            res_val.setStyleSheet("""
                border: 2px solid #87CEFA; 
                background-color: #FFDAB9; 
                color: #333333; 
                border-radius: 8px;
            """)
            self.grid.addWidget(res_val, row, col + 1)
            self.results[year] = res_val

    def validate_and_calculate(self, le):
        """Валидатор как в Taxes и запуск пересчета"""
        text = le.text().replace(',', '.')
        key = le.property("key")
        year = le.property("year")
        default = str(le.property("default"))

        # Границы для разных полей
        limits = {
            "rf": (1.0, 20.0, "Безрисковая ставка"),
            "beta": (0.1, 2.0, "Бета коэффициент"),
            "rm": (1.0, 30.0, "Доходность рынка")
        }
        min_v, max_v, name = limits.get(key)

        try:
            if not text: raise ValueError
            val = float(text)
            if not (min_v <= val <= max_v): raise ValueError
            self.stored_data[(key, year)] = val
            # Форматирование после ввода
            if key == "beta":
                le.setText(f"{val:.2f}".replace('.', ','))
            else:
                le.setText(f"{val:.1f}".replace('.', ','))

        except ValueError:
            self.show_error(name, min_v, max_v, default)
            self.stored_data[(key, year)] = float(default)
            le.setText(default.replace('.', ','))

        self.calculate_all()

    def show_error(self, name, min_v, max_v, default):
        """Обновленное окно ошибки для CAPM в едином стиле"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(self.msg_font)

        # Формируем текст сообщения по вашему стандарту
        error_text = (
            f"Параметр <b>{name}</b> указан некорректно.<br><br>"
            f"Допустимый диапазон в модели: от <b>{min_v}</b> до <b>{max_v}</b>.<br>"
            f"Буквы и символы не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию: <b>{default}</b>"
        )

        msg.setText(error_text)

        # Стилизация окна и кнопки (как в TaxesWidget)
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
        """Полная перерисовка при изменении сроков проекта"""
        try:
            y, m = int(start_year), int(start_month_idx) + 1
            total_months = int(duration_years) * 12

            unique_years = []
            curr_y, curr_m = y, m
            for _ in range(total_months):
                if curr_y not in unique_years: unique_years.append(curr_y)
                curr_m += 1
                if curr_m > 12: curr_m = 1; curr_y += 1

            self.years = [str(yr) for yr in unique_years]

            # Очистка
            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)

            # 1. Заголовки (Года)
            for col, year_text in enumerate(self.years):
                year_label = QLabel(year_text)
                year_label.setFont(self.label_font)
                year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                year_label.setStyleSheet(
                    "font-weight: bold; color: #333333; background: #B9D9EB; border-radius: 5px; padding: 5px;")
                self.grid.addWidget(year_label, 0, col + 1)

            # 2. Строки данных (Rf, Beta, Rm)
            self._add_capm_row("Безрисковая ставка, %", "rf", 7.0, 1)
            self._add_capm_row("Коэффициент Бета", "beta", 1.2, 2)
            self._add_capm_row("Рыночная доходность, %", "rm", 12.0, 3)

            self._add_mrp_row(4)  # MRP - Market Risk Premium

            # 3. Строка Итого (теперь будет в 5-й строке)
            self._add_result_row(5)

            # Распорка
            self.grid.setColumnStretch(len(self.years) + 1, 10)
            self.calculate_all()

        except Exception as e:
            print(f"CAPM Update Error: {e}")

    def _add_mrp_row(self, row):
        """Добавление расчетной строки: Премия за риск рынка (с голубой границей)"""
        label = QLabel("Премия за риск рынка, %")
        label.setFont(self.label_font)
        label.setStyleSheet("font-style: italic; color: #555555; background: transparent; border: none;")
        self.grid.addWidget(label, row, 0)

        # Инициализируем словарь для хранения меток, если его еще нет
        if not hasattr(self, 'mrp_labels'):
            self.mrp_labels = {}

        for col, year in enumerate(self.years):
            mrp_val = QLabel("0,00")
            mrp_val.setFont(self.input_font)
            mrp_val.setFixedSize(100, 35)
            mrp_val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # СТИЛЬ: граница #87CEFA (как у ввода), но фон белый
            mrp_val.setStyleSheet("""
                border: 2px solid #87CEFA; 
                background-color: #FFFFFF; 
                color: #555555; 
                border-radius: 8px;
            """)
            self.grid.addWidget(mrp_val, row, col + 1)
            self.mrp_labels[year] = mrp_val
    def calculate_all(self):
        """Расчет MRP и Re для каждого года"""
        for year in self.years:
            try:
                rf = float(self.inputs[f"rf_{year}"].text().replace(',', '.'))
                beta = float(self.inputs[f"beta_{year}"].text().replace(',', '.'))
                rm = float(self.inputs[f"rm_{year}"].text().replace(',', '.'))

                # 1. Расчет премии за риск (Rm - Rf)
                mrp = rm - rf
                if hasattr(self, 'mrp_labels') and year in self.mrp_labels:
                    self.mrp_labels[year].setText(f"{mrp:.2f}".replace('.', ','))

                # 2. Итоговая формула CAPM: Re = Rf + Beta * MRP
                re = rf + beta * mrp

                self.results[year].setText(f"{max(0, re):.2f}".replace('.', ','))
            except Exception as e:
                if year in self.results: self.results[year].setText("0,00")
                if hasattr(self, 'mrp_labels') and year in self.mrp_labels:
                    self.mrp_labels[year].setText("0,00")

        if hasattr(self.main_window, 'update_wacc_values'):
            self.main_window.update_wacc_values()

    def get_re_for_year(self, year_str):
        """Метод для получения значения конкретного года извне"""
        try:
            return float(self.results[year_str].text().replace(',', '.'))
        except:
            return 13.4
