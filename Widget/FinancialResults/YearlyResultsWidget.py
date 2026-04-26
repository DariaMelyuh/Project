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
        # Шрифты
        self.font_title = QFont("Times New Roman", 16, QFont.Weight.Bold)
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 12)

        self.setObjectName("YearlyContainer")
        self.setStyleSheet("""
            QFrame#YearlyContainer {
                background-color: #FFFFFF;
                border: 1px solid #D0E6F5;
                border-radius: 12px;
            }
        """)

        # Основной вертикальный слой
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 20, 25, 20)
        self.main_layout.setSpacing(15)

        # --- ВЕРХНЯЯ ПАНЕЛЬ (Заголовок + Легенда) ---
        top_panel_layout = QHBoxLayout()

        self.title_label = QLabel("Отчет о прибылях и убытках")
        self.title_label.setFont(self.font_title)
        self.title_label.setStyleSheet("color: #2C3E50; border: none; background: transparent;")
        top_panel_layout.addWidget(self.title_label)

        top_panel_layout.addStretch()

        # Легенда
        self.legend_container = QFrame()
        self.legend_container.setStyleSheet("border: none; background: transparent;")
        legend_layout = QHBoxLayout(self.legend_container)
        legend_layout.setContentsMargins(0, 0, 0, 0)

        # Описание цветов
        legend_items = [
            ("#D0E6F5", "Шапка"),
            ("#FFFFFF", "Расчетные данные"),
            ("#FFDAB9", "Результат проекта")
        ]

        for color, text in legend_items:
            dot = QLabel()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(f"background-color: {color}; border: 1px solid #B0C4DE; border-radius: 3px;")

            lbl = QLabel(text)
            lbl.setFont(QFont("Times New Roman", 12))  # Установлен шрифт 12
            lbl.setStyleSheet("color: #555555; margin-right: 15px;")

            legend_layout.addWidget(dot)
            legend_layout.addWidget(lbl)

        top_panel_layout.addWidget(self.legend_container)
        self.main_layout.addLayout(top_panel_layout)

        # --- ТАБЛИЦА ---
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)

        # Стилизация таблицы - убираем лишние рамки и серые пятна
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E1EFF8;
                border: 1px solid #E1EFF8;
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
                font-size: 12pt;
                outline: none;
            }
            QHeaderView::section {
                background-color: #D0E6F5;
                color: #2C3E50;
                padding: 5px;
                font-family: 'Times New Roman';
                font-size: 12pt;
                font-weight: bold;
                border: 1px solid #E1EFF8;
            }
        """)
        self.main_layout.addWidget(self.table)

        # Убрали addStretch(), чтобы таблица не "подпрыгивала" и не создавала артефактов

    def update_table_height(self):
        """Динамически меняет высоту таблицы, исключая пустые строки внизу"""
        row_count = self.table.rowCount()
        header_height = self.table.horizontalHeader().height() or 40
        row_height = 38

        # +2 пикселя запаса, чтобы не появлялся скроллбар
        total_height = header_height + (row_height * row_count) + 2
        self.table.setFixedHeight(total_height)
        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)

    def _create_header_col_item(self, text):
        """Первая колонка (названия) - теперь без серой заливки"""
        item = QTableWidgetItem(text)
        item.setFont(self.font_tnr_bold)
        # Убрана серая заливка, используем прозрачный/белый
        item.setBackground(QBrush(Qt.GlobalColor.transparent))
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item

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
        headers = ["Показатель, руб", "Итого,руб"] + [str(y) for y in years_list]
        self.table.setHorizontalHeaderLabels(headers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table.setRowCount(0)
        self.table.blockSignals(False)
        return months_per_year
    def update_data(self, months_per_year, products_data, k_scenario,
                    k_scenario_exp, inflation_map, base_opex,
                    seasonal_factors, start_month, sales_capacity_data,
                    volume_growth_data, price_growth_data,
                    capex_data, loan_schedule, tax_rates_map):

        indicators = [
            "Выручка",
            "Операционные затраты",
            "EBITDA",
            "Амортизация",
            "EBIT",
            "Проценты по кредиту",
            "EBT (Прибыль до налога)",
            "Налог (УСН)",
            "Чистая прибыль"
        ]

        self.table.blockSignals(True)
        self.table.setRowCount(len(indicators))
        calendar_years = list(months_per_year.keys())
        total_months = sum(months_per_year.values())

        # Инициализация помесячных массивов
        m_rev = [0.0] * total_months
        m_opex = [0.0] * total_months
        m_amort = [0.0] * total_months
        # Получаем график процентов
        m_interest = [loan_schedule.get(m, 0.0) for m in range(1, total_months + 1)]

        # 1. Расчет Выручки и OpEx помесячно
        # 1. Расчет Выручки помесячно
        abs_m = 0
        curr_m_idx = start_month

        # Инициализируем текущие значения базы
        curr_v = [prod['base_vol'] for prod in products_data]
        curr_p = [prod['base_price'] for prod in products_data]

        for year in calendar_years:
            year_str = str(year)
            inf_m = (inflation_map.get(year_str, 0.0)) / 12

            num_prods = len(products_data)
            cap_ks = sales_capacity_data.get(year_str, [1.0] * num_prods)
            v_growth_year = volume_growth_data.get(year_str, [0.0] * num_prods)
            p_growth_year = price_growth_data.get(year_str, [0.0] * num_prods)

            for _ in range(months_per_year[year]):
                seasonal_k = seasonal_factors[(curr_m_idx - 1) % len(seasonal_factors)]
                m_sum = 0

                for p_idx in range(num_prods):
                    # Применяем рост СЛЕДУЮЩЕГО шага (цепной метод)
                    # Если это не самый первый месяц проекта, увеличиваем базу
                    if abs_m > 0:
                        v_g_month = (v_growth_year[p_idx] / 100) / 12
                        p_g_month = (p_growth_year[p_idx] / 100) / 12
                        curr_v[p_idx] *= (1 + v_g_month)
                        curr_p[p_idx] *= (1 + p_g_month)

                    vol = curr_v[p_idx] * cap_ks[p_idx] * seasonal_k
                    prc = curr_p[p_idx]
                    m_sum += (vol * prc)

                m_rev[abs_m] = m_sum * k_scenario
                m_opex[abs_m] = base_opex * (1 + inf_m) ** abs_m * k_scenario_exp

                abs_m += 1
                curr_m_idx = 1 if curr_m_idx == 12 else curr_m_idx + 1
        # 2. Линейная амортизация (без изменений)
        for asset in capex_data:
            month = int(asset.get('month', 1))
            term = int(asset.get('term', 0))
            if term > 0:
                m_depr = asset['cost'] / term
                for m in range(month, min(month + term, total_months + 1)):
                    m_amort[m - 1] += m_depr

        # 3. Агрегация в годовые колонки
        yearly_vals = {i: [0.0] * len(calendar_years) for i in range(len(indicators))}
        abs_m_ptr = 0
        for y_idx, year in enumerate(calendar_years):
            # Получаем ставку налога для конкретного года
            raw_tax = tax_rates_map.get(str(year), 6)
            try:
                tax_rate = float(str(raw_tax).replace(',', '.'))
                if tax_rate > 1: tax_rate /= 100
            except:
                tax_rate = 0.06

            for _ in range(months_per_year[year]):
                rev = m_rev[abs_m_ptr]
                opex = m_opex[abs_m_ptr]
                amort = m_amort[abs_m_ptr]
                intr = m_interest[abs_m_ptr]

                ebitda = rev - opex
                ebit = ebitda - amort
                ebt = ebit - intr
                # Налог от EBITDA по вашей логике
                tax = round(ebitda * tax_rate, 2) if ebitda > 0 else 0.0
                net = ebt - tax

                row_data = [rev, opex, ebitda, amort, ebit, intr, ebt, tax, net]
                for r_i, val in enumerate(row_data):
                    yearly_vals[r_i][y_idx] += val
                abs_m_ptr += 1

        # 4. Отрисовка (без изменений)
        for r in range(len(indicators)):
            # Используем кастомный метод для первой колонки
            self.table.setItem(r, 0, self._create_header_col_item(indicators[r]))

            # Используем кастомный метод для колонки "Итого"
            self.table.setItem(r, 1, self._create_total_item(sum(yearly_vals[r])))

            # Используем кастомный метод для расчетных лет
            for c, val in enumerate(yearly_vals[r]):
                self.table.setItem(r, c + 2, self._create_calc_item(val))

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

    def _create_header_col_item(self, text):
        """Первая колонка (названия) - без номера и по левому краю"""
        item = QTableWidgetItem(text)
        item.setFont(self.font_tnr_bold)
        # Прозрачный фон, чтобы не было "серости"
        item.setBackground(QBrush(Qt.GlobalColor.transparent))
        # Выравнивание по левому краю и по центру вертикально
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item

    def _create_total_item(self, value):
        """Колонка Итого (Персиковая)"""
        item = QTableWidgetItem(self.format_money(value))
        item.setBackground(QBrush(QColor("#FFDAB9")))
        item.setFont(self.font_tnr_bold)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Подсветка отрицательного итога
        if value < 0:
            item.setForeground(QBrush(QColor("red")))

        return item

    def _create_calc_item(self, value):
        """Годовые данные (Белые)"""
        item = QTableWidgetItem(self.format_money(value))
        item.setFont(self.font_tnr_regular)
        item.setBackground(QBrush(QColor("#FFFFFF")))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Если число меньше нуля — красим текст в красный
        if value < 0:
            item.setForeground(QBrush(QColor("red")))

        return item
    def _apply_alignment(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                if it:
                    if c == 0:
                        # Первую колонку оставляем по левому краю
                        it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    else:
                        # Остальные — по центру
                        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_table_height(self):
        row_count = self.table.rowCount()
        header_height = 40 # Немного увеличим для 12 шрифта
        row_height = 38
        total_height = header_height + (row_height * row_count) + 2
        self.table.setFixedHeight(total_height)
        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)