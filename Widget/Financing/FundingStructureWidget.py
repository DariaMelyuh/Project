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

class FundingStructureWidget(QFrame):
    def __init__(self, financing_widget):
        super().__init__()
        self.fin_widget = financing_widget
        self.inputs = {}
        self.shares = {}

        # 1. СНАЧАЛА ОБЯЗАТЕЛЬНО ОБЪЯВЛЯЕМ ШРИФТЫ (как в налогах)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

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

        # Заголовок виджета
        title = QLabel("Структура финансирования проекта")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("border: none; background: transparent; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- ШАПКА ТАБЛИЦЫ ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Задаем те же ширины, что и у ячеек ниже: 150 (текст), 0 (растягивается), 100 (доля)
        # Но для простоты добавим их в те же контейнеры
        headers = [
            ("Источник", 150),
            ("Итого, руб", 0),  # 0 значит растягивается как QLineEdit
            ("Доля, %", 100)
        ]

        for text, width in headers:
            lbl = QLabel(text)
            lbl.setFont(self.label_font)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedHeight(35)  # Высота как у ячеек
            if width > 0:
                lbl.setFixedWidth(width)

            lbl.setStyleSheet("""
                        font-weight: bold; 
                        color: #333333; 
                        background: #D0E6F5; 
                        border-radius: 5px; 
                    """)
            header_layout.addWidget(lbl)
        layout.addLayout(header_layout)

        # --- И СЛЕДОМ ВТОРОЙ КУСОК (СТРОКИ) ---
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
                le.editingFinished.connect(self.calculate_totals)

            self.inputs[key] = le

            # 3. Доля, %
            share_lbl = QLabel("0.00%")
            share_lbl.setFont(self.label_font)
            share_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            share_lbl.setFixedWidth(100)
            share_lbl.setFixedHeight(35)

            # Добавляем font-weight: bold во все стили долей
            if key == "total":
                share_style = """
                                background: #FFDAB9; 
                                font-weight: bold; 
                                border: 2px solid #87CEFA; 
                                border-radius: 8px; 
                                color: #333333;
                            """
            else:
                share_style = """
                                background: #F9F9F9; 
                                font-weight: bold; 
                                border: 2px solid #87CEFA; 
                                border-radius: 8px; 
                                color: #777777;
                            """

            share_lbl.setStyleSheet(share_style)
            self.shares[key] = share_lbl

            row_layout.addWidget(name_lbl)
            row_layout.addWidget(le)
            row_layout.addWidget(share_lbl)
            layout.addLayout(row_layout)

        # Конец инициализации (синхронизация и расчеты)
        self.fin_widget.inputs["amount"].textChanged.connect(self.sync_loan_amount)
        self.sync_loan_amount()
        self.calculate_totals()

    def setup_input_style(self, le):
        """Редактируемые ячейки (Собственные/Инвестиции)"""
        le.setFont(self.input_font)  # Убеждаемся, что шрифт тот же
        le.setReadOnly(False)
        le.setStyleSheet("""
            QLineEdit { 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                background-color: #E0F7FF; 
                color: #0066CC; 
                padding: 5px; 
            }
        """)

    def setup_locked_style(self, le, is_total=False):
        """Заблокированные ячейки (Кредиты/ИТОГО) — теперь выглядят так же по размеру"""
        le.setFont(self.input_font)  # ШРИФТ ТЕПЕРЬ ОДИНАКОВЫЙ
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
        """)

    def format_money(self, value):
        return f"{value:,.2f}".replace(',', ' ').replace('.', ',')

    def clean_val(self, text):
        return text.replace(' ', '').replace('\xa0', '').replace(',', '.')

    def sync_loan_amount(self):
        # Берем текст напрямую из нового поля ввода
        val_text = self.clean_val(self.fin_widget.inputs["amount"].text())
        try:
            val = float(val_text) if val_text else 0.0
            self.inputs["loan"].setText(self.format_money(val))
            self.calculate_totals()
        except:
            pass

    def calculate_totals(self):
        try:
            total_sum = 0.0
            vals = {}

            # Лимит в 8 миллионов
            MAX_LIMIT = 8000000.0

            # Значения по умолчанию для восстановления при ошибке или превышении лимита
            defaults = {"equity": 500000.0, "investments": 1000000.0}

            for key, le in self.inputs.items():
                if key == "total": continue

                txt = self.clean_val(le.text())
                try:
                    val = float(txt) if txt else 0.0

                    # ПРОВЕРКА: Если это капитал или инвестиции и значение > 8 млн
                    if key in ["equity", "investments"] and val > MAX_LIMIT:
                        # Выводим красивое сообщение об ошибке
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Превышение лимита")

                        msg.setFont(self.label_font)

                        rus_name = "Собственный капитал" if key == "equity" else "Инвестиции"
                        msg.setText(f"Сумма в поле <b>{rus_name}</b> не может превышать <b>8 000 000 руб.</b>")
                        msg.setInformativeText(
                            f"Будет установлено значение по умолчанию: {self.format_money(defaults[key])} руб.")

                        # Стилизация окна
                        msg.setStyleSheet("""
                                       QMessageBox QLabel { 
                                           color: #333333; 
                                           min-width: 480px; 
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

                        # Возвращаем дефолтное значение
                        val = defaults[key]

                    if val < 0: raise ValueError

                except ValueError:
                    val = defaults.get(key, 0.0)

                vals[key] = val
                total_sum += val

                # Обновляем текст в поле (с форматированием)
                le.blockSignals(True)  # Блокируем сигналы, чтобы не зациклить редактирование
                le.setText(self.format_money(val))
                le.blockSignals(False)

            # Устанавливаем ИТОГО
            self.inputs["total"].setText(self.format_money(total_sum))

            # Расчет долей
            for key in ["equity", "loan", "investments"]:
                share = (vals[key] / total_sum * 100) if total_sum > 0 else 0
                self.shares[key].setText(f"{share:.2f}%")
            self.shares["total"].setText("100.00%")

        except Exception as e:
            print(f"Ошибка расчета: {e}")
    def get_funding_data(self):
        return {
            "equity": float(self.clean_val(self.inputs["equity"].text())),
            "loan": float(self.clean_val(self.inputs["loan"].text())),
            "investments": float(self.clean_val(self.inputs["investments"].text())),
            "total": float(self.clean_val(self.inputs["total"].text()))
        }
