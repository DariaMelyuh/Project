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


# --- ТАБЛИЦА: КОЭФФИЦИЕНТ СЦЕНАРИЯ ---
class ScenarioWidget(QFrame):
    def __init__(self):
        super().__init__()
        # 1. Предварительная настройка шрифтов
        self.header_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        # 2. Внешний вид контейнера
        self.setStyleSheet(
            "QFrame#ScenarioContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")
        self.setObjectName("ScenarioContainer")
        self.setFixedWidth(450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Коэффициент сценария")
        title.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Сетка для таблицы
        grid = QGridLayout()
        grid.setSpacing(12)

        # Шапка таблицы
        headers = ["Наименование", "Для доходов", "Для расходов"]
        for j, text in enumerate(headers):
            h_lbl = QLabel(text)
            h_lbl.setFont(self.header_font)
            h_lbl.setStyleSheet("border: none; background: transparent; color: #2C3E50;")
            grid.addWidget(h_lbl, 0, j)

        # --- НОВАЯ ЧАСТЬ: Инициализация хранилища ---
        self.values = {}

        # Данные сценариев
        scenarios_data = [
            ("Базовый", "1", "1"),
            ("Оптимистичный", "1.1", "0.9"),
            ("Пессимистичный", "0.9", "1.1")
        ]

        # 3. Заполнение таблицы
        for i, (name, def_inc, def_exp) in enumerate(scenarios_data, 1):
            # Название сценария
            name_lbl = QLabel(name)
            name_lbl.setFont(self.label_font)
            name_lbl.setStyleSheet("font-style: italic; color: #555555; background-color: transparent; border: none;")
            grid.addWidget(name_lbl, i, 0)

            # Поле для доходов
            inc_le = QLineEdit(def_inc)
            inc_le.setProperty("type", "income")
            inc_le.setProperty("scenario", name)  # Запоминаем сценарий

            # Поле для расходов
            exp_le = QLineEdit(def_exp)
            exp_le.setProperty("type", "expense")
            exp_le.setProperty("scenario", name)  # Запоминаем сценарий

            # --- ПРОВЕРКА: Если сценарий "Базовый", блокируем ввод и ставим серый стиль ---
            if name == "Базовый":
                self.setup_locked_style(inc_le)
                self.setup_locked_style(exp_le)
            else:
                self.setup_input_style(inc_le)
                self.setup_input_style(exp_le)

            grid.addWidget(inc_le, i, 1)
            grid.addWidget(exp_le, i, 2)

            self.values[name] = {"income": inc_le, "expense": exp_le}

        layout.addLayout(grid)

    def validate_scenario_value(self, line_edit):
        """Строгая проверка границ согласно сценариям"""
        raw_text = line_edit.text().strip().replace(',', '.')
        if raw_text.endswith('.'): raw_text = raw_text[:-1]

        c_type = line_edit.property("type")  # income или expense
        scenario = line_edit.property("scenario")  # Оптимистичный или Пессимистичный

        # Значения по умолчанию, если ввод некорректен
        default_map = {
            ("Оптимистичный", "income"): "1.1",
            ("Пессимистичный", "income"): "0.9",
            ("Оптимистичный", "expense"): "0.9",
            ("Пессимистичный", "expense"): "1.1"
        }
        default = default_map.get((scenario, c_type), "1.0")

        try:
            if not raw_text: raise ValueError
            val = float(raw_text)

            # --- ЛОГИКА ДЛЯ ДОХОДОВ (Оптимистичный = рост, Пессимистичный = падение) ---
            if c_type == "income":
                if scenario == "Оптимистичный":

                    if not (1.01 <= val <= 2.0):
                        self.show_error_msg("Доходы (Оптимистичный)", "1.01", "2.0")
                        raise ValueError
                elif scenario == "Пессимистичный":

                    if not (0.01 <= val <= 1.0):
                        self.show_error_msg("Доходы (Пессимистичный)", "0.01", "1.0")
                        raise ValueError

            # --- ЛОГИКА ДЛЯ РАСХОДОВ (Оптимистичный = падение, Пессимистичный = рост) ---
            else:
                if scenario == "Оптимистичный":
                    # Оптимистично для расходов — это их снижение: от 0.01 до 0.99
                    if not (0.01 <= val <= 1.0):
                        self.show_error_msg("Расходы (Оптимистичный)", "0.01", "1.0")
                        raise ValueError
                elif scenario == "Пессимистичный":
                    # Пессимистично для расходов — это их рост: от 1.01 до 1.99
                    if not (1.01 <= val <= 2.0):
                        self.show_error_msg("Расходы (Пессимистичный)", "1.01", "2.0")
                        raise ValueError

            # Если проверка прошла, фиксируем число
            line_edit.setText(str(val).replace('.', ','))

        except ValueError:
            line_edit.setText(default.replace('.', ','))

    def show_error_msg(self, label, v_min, v_max):
        """Обновленное окно ошибки коэффициентов сценария"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")

        # Используем шрифт меток для основного текста
        msg.setFont(self.label_font)

        # Формируем текст по вашему новому стандарту
        error_text = (
            f"Параметр <b>{label}</b> указан некорректно.<br><br>"
            f"Допустимый диапазон в модели: от <b>{v_min}</b> до <b>{v_max}</b>.<br>"
            f"Буквы и символы не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию."
        )

        msg.setText(error_text)

        # Применяем обновленную стилизацию (кнопка как в TaxesWidget)
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
    def setup_locked_style(self, le):
        le.setFont(self.input_font)
        le.setFixedSize(110, 35)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setReadOnly(True)
        le.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # ДОБАВЬТЕ ЭТО: ячейку нельзя выбрать табом или кликом

        le.setStyleSheet("""
            QLineEdit { 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                background-color: #F9F9F9; 
                color: #333333; 
                padding: 5px; 
            }
        """)
    def setup_input_style(self, le):
        """Вспомогательный метод для настройки стиля: теперь редактируемый и голубой"""
        le.setFont(self.input_font)
        le.setFixedSize(110, 35)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. РАЗБЛОКИРУЕМ ВВОД
        le.setReadOnly(False)

        # 2. УСТАНАВЛИВАЕМ ГОЛУБОЙ СТИЛЬ (как в налогах)
        le.setStyleSheet("""
                            QLineEdit { 
                                border: 2px solid #87CEFA; 
                                border-radius: 8px; 
                                padding: 5px; 
                                background-color: #E0F7FF; 
                                color: #0066CC; 
                            }
                            /* Эффект при наведении курсора */
                            QLineEdit:hover {
                                border: 2px solid #0066CC; /* Чуть темнее основного голубого */
                                
                            }
                            /* Состояние при клике/фокусе */
                            QLineEdit:focus {
                                border: 2px solid #0066CC; /* Темно-синий контур */
                                background-color: white;   /* Белый фон */
                            }
                        """)

        # 3. ДОБАВЛЯЕМ ВАЛИДАТОР (только числа и запятые/точки)
        from PyQt6.QtGui import QRegularExpressionValidator
        from PyQt6.QtCore import QRegularExpression
        validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))
        le.setValidator(validator)

        # 4. ПОДКЛЮЧАЕМ ПРОВЕРКУ (чтобы убирать лишние запятые и следить за диапазоном)
        le.editingFinished.connect(lambda field=le: self.validate_scenario_value(field))

    # --- НОВЫЙ МЕТОД: Получение данных для расчетов ---
    def get_coefficient(self, scenario_name, mode="income"):
        """
        Возвращает число (float) для выбранного сценария.
        scenario_name: 'Базовый', 'Оптимистичный' или 'Пессимистичный'
        mode: 'income' (доходы) или 'expense' (расходы)
        """
        try:
            # Ищем нужный QLineEdit в нашем словаре
            le = self.values.get(scenario_name, {}).get(mode)
            if le:
                # Превращаем текст "1.1" или "0,9" в нормальное число float
                val_text = le.text().replace(',', '.')
                return float(val_text)
        except Exception as e:
            print(f"Ошибка получения коэффициента: {e}")

        return 1.0  # Возвращаем 1.0 (базовый), если произошла ошибка

    # Добавьте это в конец класса ScenarioWidget
    def get_income_multiplier(self):
        """Возвращает множитель для доходов на основе выбранного в комбобоксе сценария"""
        # Находим главное окно, чтобы узнать, какой сценарий выбран в income_selector
        from PyQt6.QtWidgets import QApplication
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == "MainWindow" or hasattr(widget, "income_selector"):
                main_win = widget
                break

        if main_win:
            selected_scenario = main_win.income_selector.combo.currentText()
            return self.get_coefficient(selected_scenario, "income")
        return 1.0

    def get_expense_multiplier(self):
        """Возвращает множитель для расходов на основе выбранного в комбобоксе сценария"""
        from PyQt6.QtWidgets import QApplication
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == "MainWindow" or hasattr(widget, "expense_selector"):
                main_win = widget
                break

        if main_win:
            selected_scenario = main_win.expense_selector.combo.currentText()
            return self.get_coefficient(selected_scenario, "expense")
        return 1.0