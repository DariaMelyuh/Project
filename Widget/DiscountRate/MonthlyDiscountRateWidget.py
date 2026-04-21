import sys
import math
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QLineEdit, QPushButton
)


class MonthlyDiscountRateWidget(QFrame):
    data_confirmed = pyqtSignal()

    def __init__(self, wacc_widget):
        super().__init__()
        self.wacc_widget = wacc_widget
        self.years = ["2026"]
        self.cells = {}

        # Шрифты
        self.title_font = QFont("Times New Roman", 14, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.val_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        self.setObjectName("MonthlyRateContainer")
        self.setStyleSheet("""
            QFrame#MonthlyRateContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)
        self.setFixedWidth(950)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Ставка дисконтирования")
        title.setFont(self.title_font)
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Сетка
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setColumnMinimumWidth(0, 250)
        layout.addLayout(self.grid)

        # Валидатор для чисел
        self.validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))

        # Первичная отрисовка
        self.update_data()

    def on_cell_changed(self):
        # Теперь вместо смены стиля кнопки просто сигнализируем об изменении данных
        self.data_confirmed.emit()

    def update_data(self):
        """Перестройка сетки на основе данных из WACC"""
        try:
            if not self.wacc_widget or not hasattr(self.wacc_widget, 'years'):
                return

            self.years = self.wacc_widget.years

            # Очистка сетки
            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)
            self.cells.clear()

            # Сбрасываем растяжение
            for i in range(self.grid.columnCount()):
                self.grid.setColumnStretch(i, 0)

            title_lbl = QLabel("Итого (WACC в месяц), %")
            title_lbl.setFixedWidth(280)
            title_lbl.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
            title_lbl.setStyleSheet("""
                color: #333333;
                background: transparent;
                border: none;
            """)
            self.grid.addWidget(title_lbl, 1, 0)

            # Отрисовка заголовков и ячеек
            for col, year in enumerate(self.years):
                # 1. Заголовок года
                year_lbl = QLabel(year)
                year_lbl.setFont(self.label_font)
                year_lbl.setFixedSize(100, 30)
                year_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                year_lbl.setStyleSheet(
                    "font-weight: bold; color: #333333; background: #B9D9EB; border-radius: 5px;")
                self.grid.addWidget(year_lbl, 0, col + 1)

                # 2. Поле ввода (теперь только для чтения)
                val_le = QLineEdit("0,00")
                val_le.setFont(self.val_font)
                val_le.setFixedSize(100, 35)
                val_le.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
                val_le.setReadOnly(True)  # Запрещаем ввод
                val_le.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Убираем выделение при клике
                # -----------------------

                val_le.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #87CEFA; 
                        background-color: #FFDAB9; 
                        color: #333333; 
                        border-radius: 8px;
                    }
                """)

                self.cells[year] = val_le
                self.grid.addWidget(val_le, 1, col + 1)

                # Т.к. поле ReadOnly, сигнал textChanged будет срабатывать только программно из refresh_calculations
                val_le.textChanged.connect(self.on_cell_changed)

            # Пружина в конце
            self.grid.setColumnStretch(len(self.years) + 1, 1)

            self.refresh_calculations()

        except Exception as e:
            print(f"Monthly Rate Update Error: {e}")
    def refresh_calculations(self):
        """Расчет месячной ставки на основе годового WACC"""
        for year in self.years:
            wacc_lbl = self.wacc_widget.cells.get(f"wacc_{year}")
            if not wacc_lbl or year not in self.cells:
                continue

            try:
                wacc_text = wacc_lbl.text().replace(",", ".").strip()
                wacc_annual = float(wacc_text) / 100 if wacc_text else 0.0

                if wacc_annual > 0:
                    # Формула: (1 + i_year)^(1/12) - 1
                    monthly_rate = (pow(1 + wacc_annual, 1 / 12) - 1) * 100
                else:
                    monthly_rate = 0.0

                new_val_text = f"{monthly_rate:.2f}".replace(".", ",")

                self.cells[year].blockSignals(True)
                self.cells[year].setText(new_val_text)
                self.cells[year].blockSignals(False)
                self.data_confirmed.emit()
            except Exception as e:
                print(f"Error calculating monthly rate for {year}: {e}")

    def format_percent(self, val):
        return f"{val:.2f}".replace(".", ",")