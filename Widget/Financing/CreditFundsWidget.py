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

class CreditFundsWidget(QFrame):
    def __init__(self, input_widget):
        super().__init__()
        self.input_widget = input_widget
        self.inputs = {}  # Для хранения QLineEdit (Сумма, Ставка, Срок)
        self.results = {}  # Для хранения расчетных меток (по месяцам)

        # Шрифты
        self.main_font = QFont("Times New Roman", 12)
        self.bold_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        # Контейнер
        self.setStyleSheet("""
            QFrame#FinContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)
        self.setObjectName("FinContainer")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. ЗАГОЛОВОК
        title = QLabel("Параметры кредитования (Заемные средства)")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333333; border: none; background: transparent;")
        main_layout.addWidget(title)

        # 2. БЛОК ВВОДА ПАРАМЕТРОВ (как в ваших сценариях)
        params_layout = QHBoxLayout()
        params_layout.setSpacing(10)

        param_configs = [
            ("amount", "Сумма займа, руб", "500 000"),
            ("rate", "Ставка в год, %", "12"),
            ("term", "Срок (мес)", "12")
        ]

        for key, label_text, default in param_configs:
            v_box = QVBoxLayout()

            # Шапка (как года в налогах)
            lbl = QLabel(label_text)
            lbl.setFont(self.main_font)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedHeight(35)
            lbl.setStyleSheet("""
                font-weight: bold; color: #333333; 
                background: #D0E6F5; border-radius: 5px; padding: 5px;
            """)

            # Поле ввода
            le = QLineEdit(default)
            le.setFont(self.bold_font)
            le.setAlignment(Qt.AlignmentFlag.AlignCenter)
            le.setFixedHeight(35)
            le.setProperty("key", key)
            self.setup_input_style(le)
            le.editingFinished.connect(self.calculate_loan)

            # Подключаем валидатор перед расчетом
            le.editingFinished.connect(lambda field=le: self.validate_and_calculate(field))

            self.inputs[key] = le
            v_box.addWidget(lbl)
            v_box.addWidget(le)
            params_layout.addLayout(v_box)

        main_layout.addLayout(params_layout)

        # 3. ТАБЛИЦА ВЫПЛАТ (Прокручиваемая область)
        self.scroll_area = QScrollArea()
        self.scroll_area.setMinimumHeight(200)  # Это обеспечит видимость всех строк сразу
        self.scroll_area.setMaximumHeight(250)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Стилизуем скроллбар как в вашем коде
        self.scroll_area.horizontalScrollBar().setStyleSheet(self.get_scrollbar_style())

        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(10)  # Увеличивает расстояние между ячейками по всем осям
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_area.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll_area)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent; /* Убирает фон области прокрутки */
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent; /* Убирает фон внутреннего контейнера */
            }
        """)
        self.setStyleSheet("""
            QFrame#FinContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 12px; 
            }
        """)

        # Начальный расчет
        self.calculate_loan()

    def setup_input_style(self, le):
        le.setStyleSheet("""
            QLineEdit { 
                border: 2px solid #87CEFA; border-radius: 8px; 
                background-color: #E0F7FF; color: #0066CC; padding: 5px; 
            }
        """)

    def get_scrollbar_style(self):
        return """
            QScrollBar:horizontal { border: none; background: #F0F8FF; height: 10px; }
            QScrollBar::handle:horizontal { background: #87CEFA; min-width: 20px; border-radius: 5px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """

    def validate_and_calculate(self, line_edit):
        """Строгая проверка параметров кредитования с детальными окнами ошибок"""
        raw_text = line_edit.text().strip().replace(' ', '').replace(',', '.')
        if raw_text.endswith('.'): raw_text = raw_text[:-1]

        key = line_edit.property("key")  # amount, rate или term

        # Значения по умолчанию при ошибке
        default_map = {
            "amount": "500000",
            "rate": "12",
            "term": "12"
        }
        default = default_map.get(key, "0")

        # Названия для вывода в окне
        names_map = {
            "amount": "Сумма займа",
            "rate": "Процентная ставка",
            "term": "Срок кредитования"
        }
        field_name = names_map.get(key, "Параметр")

        try:
            if not raw_text: raise ValueError
            val = float(raw_text)

            # --- ЛОГИКА ДЛЯ СУММЫ ---
            if key == "amount":
                # --- ЛОГИКА ДЛЯ СУММЫ (от 0 до 2 000 000) ---
                if key == "amount":
                    if not (0 <= val <= 2000000):
                        # Вызываем окно с новым диапазоном
                        self.show_error_msg(field_name, "число от 0 и до 2 000 000", default, "руб.")
                        raise ValueError

                    # Если проверка прошла, форматируем с пробелами (разрядами)
                    line_edit.setText(f"{val:,.0f}".replace(',', ' '))

            # --- ЛОГИКА ДЛЯ СТАВКИ ---
            elif key == "rate":
                if not (10.0 <= val <= 30.0):
                    self.show_error_msg(field_name, "от 10 до 30%", default, "%")
                    raise ValueError
                line_edit.setText(str(val).replace('.', ','))

            # --- ЛОГИКА ДЛЯ СРОКА (ОТ 1 ДО 60) ---
            elif key == "term":
                if not (1 <= val <= 60) or val != int(val):
                    self.show_error_msg(field_name, "целое число от 1 до 60 месяцев", default, "мес.")
                    raise ValueError
                line_edit.setText(str(int(val)))

            # Если всё прошло успешно, запускаем расчет таблицы
            self.calculate_loan()

        except ValueError:
            line_edit.setText(default.replace('.', ','))
            self.calculate_loan()

    def show_error_msg(self, field_name, rules, default_val, unit):
        """Вызов всплывающего окна в стиле налоговых сценариев"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")

        # Оформляем текст через HTML
        error_text = f"Параметр: <b>{field_name}</b><br><br>"
        error_text += f"Допустимые значения: <b>{rules}</b>.<br>"
        error_text += "Символы, буквы и некорректные значения не допускаются.<br><br>"
        error_text += f"Будет восстановлено: <b>{default_val} {unit}</b>"

        msg.setText(error_text)

        # Стилизация под ваш пример (ширина текста и кнопки)
        msg.setStyleSheet("""
                            QMessageBox QLabel { 
                                color: #333333; 
                                min-width: 500px; 
                                max-width: 200px; 
                                font-family: 'Times New Roman'; 
                                font-size: 16px;
                            }
                        
            
               
                QPushButton { 
                    font-family: 'Times New Roman'; 
                    font-size: 14px; 
                    min-width: 90px; 
                    padding: 5px; 
                    background-color: #E0F7FF;
                    border: 1px solid #87CEFA;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #B9D9EB; }
            """)

        msg.exec()

    def calculate_loan(self):
        # 1. Очистка старой сетки
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        try:
            # Чтение данных
            loan_amount = float(self.inputs["amount"].text().replace(' ', '').replace(',', '.'))
            loan_rate = float(self.inputs["rate"].text().replace(',', '.'))
            loan_term = int(self.inputs["term"].text())

            horizon_text = self.input_widget.hor_le.text()
            horizon = int(horizon_text) if horizon_text and horizon_text.isdigit() else 12

            start_month_idx = self.input_widget.month_cb.currentIndex()
            start_year = int(self.input_widget.year_cb.currentText())
            months_list = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

            # 2. ОТРИСОВКА ШАПКИ
            for i in range(horizon):
                # --- СТРОКА 0: Порядковый номер месяца ---
                num_lbl = QLabel(str(i + 1))
                num_lbl.setFont(self.main_font)
                num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                num_lbl.setFixedSize(90, 25)  # Чуть ниже основной шапки
                num_lbl.setStyleSheet("""
                    color:  #333333; 
                    font-weight: bold;
                    background-color: #D0E6F5; 
                    border-radius: 4px;
                    margin-bottom: 2px;
                """)
                self.grid_layout.addWidget(num_lbl, 0, i + 1)

                # --- СТРОКА 1: Календарная дата (Месяц и Год) ---
                m_text = f"{months_list[(start_month_idx + i) % 12]}\n{start_year + (start_month_idx + i) // 12}"
                m_lbl = QLabel(m_text)
                m_lbl.setFont(self.main_font)
                m_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                m_lbl.setFixedSize(90, 45)
                m_lbl.setStyleSheet("""
                    font-weight: bold; 
                    color: #333333; 
                    background-color: #D0E6F5; 
                    border-radius: 8px; 
                    padding: 2px;
                """)
                self.grid_layout.addWidget(m_lbl, 1, i + 1)

            # 3. Названия строк и ячейки с данными (СМЕЩЕНЫ НА +2 по строкам)
            row_names = ["Проценты", "Тело кредита"]
            r_monthly = (loan_rate / 100) / 12

            for r, name in enumerate(row_names):
                name_lbl = QLabel(name)
                name_lbl.setFont(self.main_font)
                name_lbl.setFixedWidth(130)
                name_lbl.setFixedHeight(40)
                name_lbl.setStyleSheet("font-style: italic; color: #555555; border: none;")
                # Смещение r + 2, так как 0 и 1 заняты номерами и датами
                self.grid_layout.addWidget(name_lbl, r + 2, 0)

                for i in range(horizon):
                    period = i + 1
                    val_text = ""

                    if period <= loan_term:
                        if r == 0:
                            val = self.numpy_equivalent_ipmt(r_monthly, period, loan_term, loan_amount)
                        else:
                            val = self.numpy_equivalent_ppmt(r_monthly, period, loan_term, loan_amount)
                        val_text = f"{abs(val):,.2f}".replace(',', ' ').replace('.', ',')

                    res_item = QLabel(val_text)
                    res_item.setFixedSize(90, 40)
                    res_item.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    res_item.setFont(self.main_font)
                    res_item.setStyleSheet("""
                        background-color: #F9F9F9; 
                        border: 2px solid #87CEFA; 
                        border-radius: 8px; 
                        color: #333333;
                    """)
                    self.grid_layout.addWidget(res_item, r + 2, i + 1)

            if hasattr(self.input_widget.window(), 'update_wacc_values'):
                self.input_widget.window().update_wacc_values()

        except Exception as e:
            print(f"Ошибка в методе calculate_loan: {e}")
    def get_financing_totals(self):
        try:
            # Берем данные из новых словарей inputs
            loan_amount = float(self.clean_val(self.inputs["amount"].text()))
            loan_rate = float(self.clean_val(self.inputs["rate"].text()))

            # Эти значения обычно приходят из других виджетов через input_widget
            equity_amount = getattr(self.input_widget, 'equity_value', 0.0)
            investments = getattr(self.input_widget, 'total_investments', 0.0)

            return {
                "equity": equity_amount,
                "loan": loan_amount,
                "investments": investments,
                "total": loan_amount + equity_amount + investments,
                "loan_rate": loan_rate
            }
        except Exception as e:
            print(f"Ошибка получения итогов: {e}")
            return {"equity": 0, "loan": 0, "investments": 0, "total": 0, "loan_rate": 12.0}

    def clean_val(self, text):
        return text.replace(' ', '').replace('\xa0', '').replace(',', '.')


    # (Методы ipmt и ppmt остаются без изменений как в вашем коде)
    def numpy_equivalent_ppmt(self, rate, per, nper, pv):
        if rate == 0: return -pv / nper
        pmt = pv * rate * ((1 + rate) ** nper) / ((1 + rate) ** nper - 1)
        return pmt - self.numpy_equivalent_ipmt(rate, per, nper, pv)

    def numpy_equivalent_ipmt(self, rate, per, nper, pv):
        if rate == 0: return 0
        pmt = pv * rate * ((1 + rate) ** nper) / ((1 + rate) ** nper - 1)
        fv_prev = pv * (1 + rate) ** (per - 1) - pmt * ((1 + rate) ** (per - 1) - 1) / rate
        return fv_prev * rate

    def get_interest_schedule(self):
        """Возвращает словарь {номер_месяца: сумма_процентов} для расчета чистой прибыли"""
        schedule = {}
        try:
            loan_amount = float(self.inputs["amount"].text().replace(' ', '').replace(',', '.'))
            loan_rate = float(self.inputs["rate"].text().replace(',', '.'))
            loan_term = int(self.inputs["term"].text())
            r_monthly = (loan_rate / 100) / 12

            for m in range(1, loan_term + 1):
                # Используем вашу функцию ipmt
                interest = abs(self.numpy_equivalent_ipmt(r_monthly, m, loan_term, loan_amount))
                schedule[m] = interest
        except:
            pass
        return schedule

    def get_body_schedule(self):
        # Должен возвращать [100.0, 100.0, ...]
        return self.body_list if hasattr(self, 'body_list') else []




