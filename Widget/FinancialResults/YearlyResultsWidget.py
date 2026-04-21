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


class YearlyResultsWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 11)

        self.setObjectName("YearlyContainer")
        self.setStyleSheet("""
            QFrame#YearlyContainer {
                background-color: white;
                border: 1px solid #D0E6F5;
                border-radius: 15px;
            }
        """)

        # Основной слой
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        self.main_layout.setSpacing(10)

        # 1. Заголовок
        self.title_label = QLabel("Показатели по годам")
        self.title_label.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("border: none; color: #333333; background: transparent;")
        self.main_layout.addWidget(self.title_label)

        # 2. Легенда цветов
        legend_layout = QHBoxLayout()
        colors = [("#FFDAB9", "Итого"), ("#E0F7FF", "Заголовки")]
        for color, text in colors:
            lbl_clr = QLabel()
            lbl_clr.setFixedSize(16, 16)
            lbl_clr.setStyleSheet(f"background-color: {color}; border: 1px solid #C4C4C4; border-radius: 3px;")
            lbl_txt = QLabel(text)
            lbl_txt.setFont(QFont("Times New Roman", 10))
            lbl_txt.setStyleSheet("background: transparent; border: none; color: #555555;")
            legend_layout.addWidget(lbl_clr)
            legend_layout.addWidget(lbl_txt)
            legend_layout.addSpacing(10)
        legend_layout.addStretch()
        self.main_layout.addLayout(legend_layout)

        # 3. Таблица
        self.table = QTableWidget(0, 0)  # Начинаем с пустой, колонки создаст generate_columns
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Только чтение
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E1EFF8;
                border: none;
                font-family: 'Times New Roman';
                font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #D0E6F5;
                font-weight: bold;
                border: 1px solid #D0E6F5;
                height: 35px;
            }
        """)
        self.main_layout.addWidget(self.table)

        # 4. Пружина вниз, чтобы прижать всё к верху
        self.main_layout.addStretch()

    def update_table_height(self):
        """Динамически меняет высоту таблицы в зависимости от количества строк"""
        row_count = self.table.rowCount()
        header_height = self.table.horizontalHeader().height()
        row_height = 35  # стандарт для TNR 11-12

        total_height = header_height + (row_height * row_count) + 5
        self.table.setFixedHeight(total_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)

    def format_money(self, value):
        return f"{value:,.2f}".replace(',', ' ').replace('.', ',')

    def generate_columns(self, start_month, start_year, total_months):
        self.table.blockSignals(True)

        current_month, current_year = start_month, start_year
        years_list = []
        months_per_year = {}

        for _ in range(total_months):
            if current_year not in months_per_year:
                months_per_year[current_year] = 0
                years_list.append(current_year)
            months_per_year[current_year] += 1
            current_month += 1
            if current_month > 12:
                current_month, current_year = 1, current_year + 1

        self.table.setColumnCount(2 + len(years_list))
        headers = ["Показатель", "Итого"] + [str(y) for y in years_list]
        self.table.setHorizontalHeaderLabels(headers)

        # Сбрасываем строки при перегенерации колонок
        self.table.setRowCount(0)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.blockSignals(False)
        return months_per_year


    def update_data(self, months_per_year, products_data, k_scenario,
                    k_scenario_exp, inflation_map, base_opex,
                    seasonal_factors, start_month, sales_capacity_data,
                    capex_data, loan_schedule, tax_rates_map):

        indicators = [
            "1. Выручка, руб",
            "2. Операционные затраты, руб",
            "3. EBITDA, руб",
            "4. Амортизация, руб",
            "5. EBIT, руб",
            "6. Проценты по кредиту, руб",
            "7. EBT (Прибыль до налога), руб",
            "8. Налог (УСН), руб",
            "9. Чистая прибыль, руб"
        ]

        self.table.blockSignals(True)
        self.table.setRowCount(len(indicators))
        calendar_years = list(months_per_year.keys())
        total_months = sum(months_per_year.values())

        # Инициализация помесячных массивов
        m_rev = [0.0] * total_months
        m_opex = [0.0] * total_months
        m_amort = [0.0] * total_months
        m_interest = [loan_schedule.get(m, 0.0) for m in range(1, total_months + 1)]

        # 1. Расчет Выручки и OpEx помесячно
        abs_m = 0
        curr_m_idx = start_month
        for year in calendar_years:
            inf_m = (inflation_map.get(str(year), 0.0)) / 12
            cap_ks = sales_capacity_data.get(str(year), [1.0] * len(products_data))
            for _ in range(months_per_year[year]):
                # Выручка
                k_s = seasonal_factors[curr_m_idx - 1]
                m_sum = 0
                for p_idx, prod in enumerate(products_data):
                    v_g = (prod['v_growth'] / 100) / 12
                    p_g = (prod['p_growth'] / 100) / 12
                    vol = prod['base_vol'] * (1 + v_g) ** abs_m * cap_ks[p_idx] * k_s
                    prc = prod['base_price'] * (1 + p_g) ** abs_m
                    m_sum += (vol * prc)
                m_rev[abs_m] = m_sum * k_scenario

                # OpEx
                m_opex[abs_m] = base_opex * (1 + inf_m) ** abs_m * k_scenario_exp

                abs_m += 1
                curr_m_idx = 1 if curr_m_idx == 12 else curr_m_idx + 1

        # 2. Линейная амортизация
        for asset in capex_data:
            if asset['term'] > 0:
                m_depr = asset['cost'] / asset['term']
                for m in range(asset['month'], min(asset['month'] + asset['term'], total_months + 1)):
                    m_amort[m - 1] += m_depr

        # 3. Агрегация в годовые колонки
        yearly_vals = {i: [0.0] * len(calendar_years) for i in range(len(indicators))}
        abs_m_ptr = 0
        for y_idx, year in enumerate(calendar_years):
            tax_rate = tax_rates_map.get(str(year), 0.06)
            for _ in range(months_per_year[year]):
                rev, opex, amort, intr = m_rev[abs_m_ptr], m_opex[abs_m_ptr], m_amort[abs_m_ptr], m_interest[abs_m_ptr]

                ebitda = rev - opex
                ebit = ebitda - amort
                ebt = ebit - intr
                tax = round(ebitda * tax_rate, 2) if ebitda > 0 else 0  # Налог от EBITDA по вашему ТЗ
                net = ebt - tax

                row_data = [rev, opex, ebitda, amort, ebit, intr, ebt, tax, net]
                for r_i, val in enumerate(row_data):
                    yearly_totals = yearly_vals[r_i]
                    yearly_totals[y_idx] += val
                abs_m_ptr += 1

        # 4. Отрисовка
        for r in range(len(indicators)):
            self.table.setItem(r, 0, self._create_bold_item(indicators[r]))
            self.table.setItem(r, 1, self._create_total_item(sum(yearly_vals[r])))
            for c, val in enumerate(yearly_vals[r]):
                self.table.setItem(r, c + 2, QTableWidgetItem(self.format_money(val)))

        self._apply_alignment()
        self.table.blockSignals(False)
        self.update_table_height()
        return yearly_vals[0]

    # Вспомогательные методы для чистоты кода
    def _create_bold_item(self, text):
        item = QTableWidgetItem(text)
        item.setFont(self.font_tnr_bold)
        item.setBackground(QColor("#F9F9F9"))
        return item

    def _create_total_item(self, value):
        item = QTableWidgetItem(self.format_money(value))
        item.setBackground(QColor("#FFDAB9"))
        item.setFont(self.font_tnr_bold)
        return item

    def _apply_alignment(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                if it: it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)