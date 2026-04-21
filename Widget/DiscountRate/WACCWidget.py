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
class WACCWidget(QFrame):
    def __init__(self, main_window=None):

        super().__init__()
        self.main_window = main_window

        # Шрифты
        self.title_font = QFont("Times New Roman", 14, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.val_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        self.setStyleSheet("""
            QFrame#WACCContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)
        self.setObjectName("WACCContainer")
        self.setFixedWidth(950)  # Соответствует ширине CAPM

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Средневзвешенная стоимость капитала (WACC)")
        title.setFont(self.title_font)
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Сетка для отображения данных по годам
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setColumnMinimumWidth(0, 250)
        layout.addLayout(self.grid)

        self.years = ["2026"]
        self.cells = {}  # Хранит QLabel для динамического обновления

        # Первичная отрисовка
        # Запускаем через 10мс, когда MainWindow уже точно создаст все свои атрибуты
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(10, lambda: self.update_years("2026", 0, "1"))

    def update_years(self, start_year, start_month_idx, duration_years):
        """Перестройка колонок при изменении длительности проекта"""
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

            # Очистка сетки
            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)

            # 1. Заголовки (Года)
            for col, year_text in enumerate(self.years):
                year_lbl = QLabel(year_text)
                year_lbl.setFont(self.label_font)
                year_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                year_lbl.setStyleSheet(
                    "font-weight: bold; color: #333333; background: #B9D9EB; border-radius: 5px; padding: 5px;")
                self.grid.addWidget(year_lbl, 0, col + 1)

            # 2. Создание строк (только для чтения)
            # Внутри метода update_years
            row_titles = [
                ("Стоимость собств. капитала, %", "re"),
                ("Доля собств. капитала, %", "we"),
                ("Стоимость заемного капитала, %", "rd"),
                ("Доля заемного капитала, %", "wd"),
                ("Общая стоимость капитала", "total_cap"),  # Новая строка
                ("Ставка налога на прибыль, %", "tax"),
                ("Итого, %", "wacc")
            ]

            for row_idx, (name, key) in enumerate(row_titles, start=1):
                title_lbl = QLabel(name)
                title_lbl.setFont(self.label_font if key != "wacc" else self.val_font)
                title_lbl.setStyleSheet("background: transparent; border: none; color: #555555;")
                self.grid.addWidget(title_lbl, row_idx, 0)

                for col, year in enumerate(self.years):
                    val_lbl = QLabel("0,00")
                    val_lbl.setFont(self.val_font)
                    val_lbl.setFixedSize(100, 35)
                    val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Стиль: итоговая строка выделена цветом, остальные - просто в рамках
                    if key == "wacc":
                        # Итоговая строка (WACC): Персиковый фон + Голубая рамка 2px
                        style = "border: 2px solid #87CEFA; background-color: #FFDAB9; color: #333333; border-radius: 8px;"
                    else:
                        # Обычные строки: Светло-серый фон + Голубая рамка 2px
                        style = "border: 2px solid #87CEFA; background-color: #F8F9FA; color: #555555; border-radius: 8px;"

                    val_lbl.setStyleSheet(style)
                    self.grid.addWidget(val_lbl, row_idx, col + 1)
                    self.cells[f"{key}_{year}"] = val_lbl

            self.grid.setColumnStretch(len(self.years) + 1, 10)

            # Если данные в главном окне уже есть, можно запустить расчет
            if self.main_window and hasattr(self.main_window, 'funding_widget'):
                self.refresh_calculations()

        except Exception as e:
            print(f"WACC Update Error: {e}")

    def update_years(self, start_year, start_month_idx, duration_years):
        """Перестройка колонок при изменении длительности проекта"""
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

            # Очистка сетки и СЛОВАРЯ
            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)

            self.cells.clear()  # ВАЖНО: Очищаем старые ссылки

            # 1. Заголовки (Года)
            for col, year_text in enumerate(self.years):
                year_lbl = QLabel(year_text)
                year_lbl.setFont(self.label_font)
                year_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                year_lbl.setStyleSheet(
                    "font-weight: bold; color: #333333; background: #B9D9EB; border-radius: 5px; padding: 5px;")
                self.grid.addWidget(year_lbl, 0, col + 1)

            # 2. Создание строк
            row_titles = [
                ("Стоимость собств. капитала, %", "re"),
                ("Доля собств. капитала, %", "we"),
                ("Стоимость заемного капитала, %", "rd"),
                ("Доля заемного капитала, %", "wd"),
                ("Общая стоимость капитала", "total_cap"),
                ("Ставка налога на прибыль, %", "tax"),
                ("Итого, %", "wacc")
            ]

            for row_idx, (name, key) in enumerate(row_titles, start=1):
                title_lbl = QLabel(name)

                # Устанавливаем шрифт (жирный для ИТОГО, обычный для остальных)
                title_lbl.setFont(self.label_font if key != "wacc" else self.val_font)

                # УБИРАЕМ ЗАЛИВКУ И ДОБАВЛЯЕМ КУРСИВ
                if key == "wacc":
                    # Для итоговой строки оставляем прямой шрифт и темный цвет
                    title_lbl.setStyleSheet("background: transparent; border: none; color: #333333;")
                else:
                    # Для всех остальных параметров: курсив, серый цвет, без фона
                    title_lbl.setStyleSheet(
                        "font-style: italic; color: #555555; background: transparent; border: none;")

                self.grid.addWidget(title_lbl, row_idx, 0)

                for col, year in enumerate(self.years):
                    val_lbl = QLabel("0,00")
                    val_lbl.setFont(self.val_font)
                    val_lbl.setFixedSize(100, 35)
                    val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    if key == "wacc":
                        style = "border: 2px solid #87CEFA; background-color: #FFDAB9; color: #333333; border-radius: 8px;"
                    else:
                        style = "border: 2px solid #87CEFA; background-color: #F8F9FA; color: #555555; border-radius: 8px;"

                    val_lbl.setStyleSheet(style)
                    self.grid.addWidget(val_lbl, row_idx, col + 1)
                    # Сначала создаем ячейку в словаре, потом вызываем расчет
                    self.cells[f"{key}_{year}"] = val_lbl

            self.grid.setColumnStretch(len(self.years) + 1, 10)

            # Вызываем расчет только ПОСЛЕ того, как все ячейки созданы в self.cells
            self.refresh_calculations()

        except Exception as e:
            print(f"WACC Update Error: {e}")

    def refresh_calculations(self):
        if not self.main_window: return

        # ПРОВЕРКА 1: Существует ли WACC в главном окне (защита от AttributeError)
        if not hasattr(self.main_window, 'wacc_widget'):
            return

        # ПРОВЕРКА 2: Созданы ли остальные зависимости
        needed = ['funding_widget', 'fin_widget', 'taxes_widget', 'capm_widget']
        if not all(hasattr(self.main_window, w) for w in needed):
            return

        try:
            struct = self.main_window.funding_widget.get_funding_data()
            total_funding = float(struct.get("total", 0))
            fund_data = self.main_window.fin_widget.get_financing_totals()
            rd_val = float(fund_data.get("loan_rate", 0.0))

            for year in self.years:
                # 2. Защита от отсутствия ключа в словаре (если расчет вызван до отрисовки ячеек)
                if f"re_{year}" not in self.cells:
                    continue

                re_val = self.main_window.capm_widget.get_re_for_year(year)

                # Налог
                tax_field = self.main_window.taxes_widget.inputs.get(f"УСН, %_{year}")
                if not tax_field:
                    tax_field = self.main_window.taxes_widget.inputs.get("УСН, %")
                tax_val = float(tax_field.text().replace(',', '.')) if tax_field else 20.0

                if total_funding > 0:
                    equity_sum = float(struct.get("equity", 0)) + float(struct.get("investments", 0))
                    loan_sum = float(struct.get("loan", 0))
                    we = equity_sum / total_funding
                    wd = loan_sum / total_funding
                else:
                    we, wd = 1.0, 0.0

                wacc_result = ((re_val / 100) * we) + ((rd_val / 100) * wd * (1 - tax_val / 100))
                wacc_result *= 100

                # Безопасное обновление текста
                self.cells[f"re_{year}"].setText(f"{re_val:.2f}".replace('.', ','))
                self.cells[f"we_{year}"].setText(f"{we * 100:.2f}".replace('.', ','))
                self.cells[f"rd_{year}"].setText(f"{rd_val:.2f}".replace('.', ','))
                self.cells[f"wd_{year}"].setText(f"{wd * 100:.2f}".replace('.', ','))

                formatted_total = f"{total_funding:,.2f}".replace(',', ' ').replace('.', ',')
                self.cells[f"total_cap_{year}"].setText(formatted_total)
                self.cells[f"tax_{year}"].setText(f"{tax_val:.2f}".replace('.', ','))
                self.cells[f"wacc_{year}"].setText(f"{wacc_result:.2f}".replace('.', ','))

        except Exception as e:
            # Если это ошибка ключа (KeyError), мы её подавляем, так как интерфейс скоро обновится
            if not isinstance(e, KeyError):
                print(f"WACC Calculation Error: {e}")
