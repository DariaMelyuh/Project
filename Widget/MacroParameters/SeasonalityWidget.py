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

# --- ТАБЛИЦА: СЕЗОННЫЙ КОЭФФИЦИЕНТ (КОМПАКТНАЯ) ---
class SeasonalityWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.header_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        # Список для хранения ссылок на поля ввода, чтобы достать из них данные позже
        self.inputs = []

        self.setStyleSheet(
            "QFrame#SeasonContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")
        self.setObjectName("SeasonContainer")
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        title = QLabel("Сезонный коэффициент")
        title.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        grid = QGridLayout()
        grid.setVerticalSpacing(4)
        grid.setHorizontalSpacing(8)

        headers = ["Месяц", "Коэффициент"]
        for j, head in enumerate(headers):
            h_lbl = QLabel(head)
            h_lbl.setFont(self.header_font)
            h_lbl.setStyleSheet("border: none; background: transparent; color: #2C3E50;")
            grid.addWidget(h_lbl, 0, j)

        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
                  "Ноябрь", "Декабрь"]

        from PyQt6.QtGui import QRegularExpressionValidator
        validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))

        for i, month in enumerate(months, 1):
            lbl = QLabel(month)
            lbl.setFont(self.label_font)
            lbl.setStyleSheet("font-style: italic; color: #555555; background-color: transparent; border: none;")

            le = QLineEdit("1")
            le.setValidator(validator)
            le.setFont(self.input_font)
            le.setFixedSize(80, 28)
            le.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # НОВЫЙ СТИЛЬ: Толщина 2px, радиус 8px и эффект :focus
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
                                border: 2px solid #0066CC; /* Чуть темнее основного голубого */
                                
                            }
                        """)

            le.setProperty("month_name", month)
            le.editingFinished.connect(lambda field=le: self.validate_season_input(field))

            # Сохраняем поле ввода в наш список
            self.inputs.append(le)

            grid.addWidget(lbl, i, 0)
            grid.addWidget(le, i, 1, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(grid)

    def validate_season_input(self, line_edit):
        """Проверка ввода сезонного коэффициента: от 0.1 до 5"""
        raw_text = line_edit.text().strip()
        if raw_text.endswith(',') or raw_text.endswith('.'):
            raw_text = raw_text[:-1]

        text = raw_text.replace(',', '.')
        month = line_edit.property("month_name")

        min_val = 0.1
        max_val = 5.0
        default = "1"

        try:
            if not text:
                raise ValueError

            value = float(text)

            if value < min_val or value > max_val:
                raise ValueError

            # Убираем лишние .0 для красоты
            clean_val = str(int(value)) if value == int(value) else text.replace('.', ',')
            line_edit.setText(clean_val)

        except ValueError:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка ввода")
            msg.setFont(self.label_font)

            # Текст в едином стиле
            error_text = (
                f"Параметр <b>Коэффициент</b> (месяц: <b>{month}</b>) указан некорректно.<br><br>"
                f"Допустимый диапазон: от <b>{min_val}</b> до <b>{max_val}</b>.<br>"
                f"Буквы и символы не допускаются.<br><br>"
                f"Будет восстановлено значение по умолчанию: <b>{default}</b>"
            )

            msg.setText(error_text)

            # ОБНОВЛЕННАЯ СТИЛИЗАЦИЯ (кнопка как в TaxesWidget)
            msg.setStyleSheet("""
                QMessageBox QLabel { 
                    color: #333333; 
                    min-width: 480px; 
                }
                QPushButton { 
                    font-family: 'Times New Roman'; 
                    font-size: 14px; 
                    min-width: 100px; 
                    padding: 6px; 
                    background-color: #E0F7FF;
                    border: 2px solid #87CEFA; /* Толщина 2px как в инпутах */
                    border-radius: 8px;        /* Радиус 8px для мягкости */
                    color: #0066CC;             /* Яркий синий текст */
                }
                QPushButton:hover { 
                    background-color: #B9D9EB; 
                    border: 2px solid #0066CC; /* Акцент при наведении */
                }
            """)
            msg.exec()

            line_edit.setText(default)

    def get_values(self):
        """Возвращает список из 12 коэффициентов сезонности из QLineEdit"""
        factors = []
        for le in self.inputs:
            try:
                val = float(le.text().replace(',', '.'))
                factors.append(val)
            except ValueError:
                factors.append(1.0)
        return factors
# Добавьте это в конец класса SeasonalityWidget
    def get_factors(self):
        """
        Псевдоним для метода get_values, чтобы main.py мог получить
        список коэффициентов для расчета выручки.
        """
        return self.get_values()