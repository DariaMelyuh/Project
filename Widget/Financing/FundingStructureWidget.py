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

import sys
import math
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox
)

class FundingStructureWidget(QFrame):
    def __init__(self, financing_widget):
        super().__init__()
        self.credit_widget = financing_widget
        self.inputs = {}
        self.shares = {}

        # 1. Шрифты и валидаторы
        self.num_validator = QRegularExpressionValidator(QRegularExpression(r"^[0-9\s.,]*$"))
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.msg_font = QFont("Times New Roman", 12) # Обязательно объявляем

        self.setStyleSheet("""
            QFrame#FundingContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px;
            }
        """)
        self.setObjectName("FundingContainer")
        self.setFixedWidth(550)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Структура финансирования проекта")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("border: none; background: transparent; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- ШАПКА ТАБЛИЦЫ ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        headers = [("Источник", 150), ("Итого, руб", 0), ("Доля, %", 100)]

        for text, width in headers:
            lbl = QLabel(text)
            lbl.setFont(self.label_font)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedHeight(35)
            if width > 0: lbl.setFixedWidth(width)
            lbl.setStyleSheet("font-weight: bold; color: #333333; background: #D0E6F5; border-radius: 5px;")
            header_layout.addWidget(lbl)
        layout.addLayout(header_layout)

        # --- СТРОКИ ---
        self.sources = [
            ("equity", "Капитал", 500000.0, False),
            ("loan", "Кредит", 0.0, True),
            ("investments", "Инвестиции", 1000000.0, False),
            ("total", "ИТОГО", 0.0, True)
        ]

        for key, name, default, readonly in self.sources:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)

            name_lbl = QLabel(name)
            name_lbl.setFont(self.label_font)
            name_lbl.setFixedWidth(150)
            name_lbl.setStyleSheet("font-style: italic; color: #555555; background: transparent; border: none;")

            le = QLineEdit(self.format_money(default))
            le.setFont(self.input_font)
            le.setAlignment(Qt.AlignmentFlag.AlignCenter)
            le.setFixedHeight(35)

            if readonly:
                self.setup_locked_style(le, is_total=(key == "total"))
            else:
                self.setup_input_style(le)
                le.setValidator(self.num_validator)
                le.setProperty("key", key)
                # Подключаем валидацию по завершению ввода
                le.editingFinished.connect(lambda field=le: self.validate_and_calculate(field))

            self.inputs[key] = le

            share_lbl = QLabel("0.00%")
            share_lbl.setFont(self.label_font)
            share_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            share_lbl.setFixedWidth(100)
            share_lbl.setFixedHeight(35)

            if key == "total":
                share_style = "background: #FFDAB9; color: #333333;"
            else:
                share_style = "background: #F9F9F9; color: #777777;"

            share_lbl.setStyleSheet(f"{share_style} font-weight: bold; border: 2px solid #87CEFA; border-radius: 8px;")
            self.shares[key] = share_lbl

            row_layout.addWidget(name_lbl)
            row_layout.addWidget(le)
            row_layout.addWidget(share_lbl)
            layout.addLayout(row_layout)

        # Синхронизация с кредитным виджетом
        self.credit_widget.inputs["amount"].textChanged.connect(self.sync_loan_amount)
        self.sync_loan_amount()
        self.calculate_totals()

    def setup_input_style(self, le):
        """Редактируемые ячейки (Собственные/Инвестиции) с эффектами наведения и клика"""
        le.setFont(self.input_font)
        le.setReadOnly(False)
        le.setStyleSheet("""
            QLineEdit { 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                background-color: #E0F7FF; 
                color: #0066CC; 
                padding: 5px; 
            }
            /* Эффект при наведении курсора */
            QLineEdit:hover {
                border: 2px solid #0066CC; /* Делаем рамку темнее */
            }
            /* Эффект при клике (фокусе) */
            QLineEdit:focus {
                border: 2px solid #0066CC; /* Темная рамка */
                background-color: white;   /* Белый фон, чтобы было удобно печатать */
                color:  #0066CC;            /* Более контрастный цвет текста */
            }
        """)
    def setup_locked_style(self, le, is_total=False):
        """Заблокированные ячейки теперь тоже будут немного подсвечиваться при наведении"""
        le.setFont(self.input_font)
        le.setReadOnly(True)
        bg = "#FFDAB9" if is_total else "#F9F9F9"

        le.setStyleSheet(f"""
            QLineEdit {{ 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                background-color: {bg}; 
                color: #333333; 
                padding: 5px; 
            }}
            QLineEdit:hover {{
                border: 2px solid #B0C4DE; /* Мягкая подсветка для заблокированных полей */
            }}
        """)

    def format_money(self, value):
        return f"{value:,.2f}".replace(',', ' ').replace('.', ',')

    def clean_val(self, text):
        return text.replace(' ', '').replace('\xa0', '').replace(',', '.')

    def sync_loan_amount(self):
        val_text = self.clean_val(self.credit_widget.inputs["amount"].text())
        try:
            val = float(val_text) if val_text else 0.0
            self.inputs["loan"].setText(self.format_money(val))
            self.calculate_totals()
        except: pass

    def validate_and_calculate(self, line_edit):
        """Метод строгой проверки параметров"""
        raw_text = self.clean_val(line_edit.text()).strip()
        key = line_edit.property("key")

        MAX_LIMIT = 8000000.0
        defaults = {"equity": 500000.0, "investments": 1000000.0}
        names_map = {"equity": "Собственный капитал", "investments": "Инвестиции"}

        try:
            if not raw_text: raise ValueError
            val = float(raw_text)

            if not (0 <= val <= MAX_LIMIT):
                self.show_error_msg(names_map[key], "от 0 до 8 000 000", self.format_money(defaults[key]), "руб.")
                val = defaults[key]

            line_edit.setText(self.format_money(val))
            self.calculate_totals()

        except ValueError:
            line_edit.setText(self.format_money(defaults.get(key, 0.0)))
            self.calculate_totals()

    def calculate_totals(self):
        """Простой пересчет всех значений и долей"""
        try:
            total_sum = 0.0
            current_vals = {}

            for key, le in self.inputs.items():
                if key == "total": continue
                val = float(self.clean_val(le.text()))
                current_vals[key] = val
                total_sum += val

            self.inputs["total"].setText(self.format_money(total_sum))

            for key in ["equity", "loan", "investments"]:
                share = (current_vals[key] / total_sum * 100) if total_sum > 0 else 0
                self.shares[key].setText(f"{share:.2f}%")
            self.shares["total"].setText("100.00%")

        except Exception as e:
            print(f"Ошибка расчета: {e}")

    def show_error_msg(self, field_name, rules, default_val, unit):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(self.msg_font)
        msg.setText(f"Параметр <b>{field_name}</b> указан некорректно.<br><br>"
                   f"Допустимый диапазон: <b>{rules}</b>.<br>Буквы и символы не допускаются.<br><br>"
                   f"Будет восстановлено значение по умолчанию: <b>{default_val} {unit}</b>")
        msg.setStyleSheet("""
            QMessageBox QLabel { color: #333333; min-width: 500px; }
            QPushButton { font-family: 'Times New Roman'; font-size: 14px; min-width: 100px; padding: 6px; 
                          background-color: #E0F7FF; border: 2px solid #87CEFA; border-radius: 8px; color: #0066CC; }
            QPushButton:hover { background-color: #B9D9EB; border: 2px solid #0066CC; }
        """)
        msg.exec()

    def get_funding_data(self):
        return {k: float(self.clean_val(self.inputs[k].text())) for k in ["equity", "loan", "investments", "total"]}