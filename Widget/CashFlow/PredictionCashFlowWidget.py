import math
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class PredictionCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        # 1-2) Определение шрифтов (Times New Roman)
        self.font_title = QFont("Times New Roman", 16, QFont.Weight.Bold)
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 12)

        self.setObjectName("PredictionCFContainer")
        self.discounted_flows = []

        # 5) Скругление 12px и основной стиль
        self.setStyleSheet(
            "QFrame#PredictionCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 12px; }"
        )

        layout = QVBoxLayout(self)
        # 5) Уменьшаем нижний отступ до 5, чтобы убрать лишнее место
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        self.title = QLabel("Чистый денежный поток")
        self.title.setFont(self.font_title)  # Название 16 шрифтом
        # 3) Убираем фон у названия (background: transparent)
        self.title.setStyleSheet("color: #2C3E50; border: none; background: transparent;")
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(True)

        # Отключаем скроллбары
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Стилизация таблицы согласно общему стилю
        # Стилизация таблицы с закруглением углов шапки
        self.table.setStyleSheet("""
                    QTableWidget {
                        gridline-color: #E1EFF8;
                        border: none; /* Убираем внешнюю рамку, так как она есть у контейнера YearlyContainer */
                        background-color: #FFFFFF;
                        font-family: 'Times New Roman';
                        font-size: 12pt;
                        outline: none;
                    }

                    /* Контейнер всей шапки */
                    QHeaderView {
                        background-color: transparent;
                        border-top-left-radius: 12px;
                        border-top-right-radius: 12px;
                    }

                    /* Общие стили для всех ячеек шапки */
                    QHeaderView::section {
                        background-color: #D0E6F5;
                        color: #2C3E50;
                        padding: 5px;
                        font-family: 'Times New Roman';
                        font-size: 12pt;
                        font-weight: bold;
                        border: none;
                        border-right: 1px solid #E1EFF8;
                        border-bottom: 1px solid #E1EFF8;
                    }

                    /* Скругление левого верхнего угла первой колонки */
                    QHeaderView::section:horizontal:first {
                        border-top-left-radius: 12px;
                    }

                    /* Скругление правого верхнего угла последней колонки */
                    QHeaderView::section:horizontal:last {
                        border-top-right-radius: 12px;
                        border-right: none; /* Убираем лишнюю полоску справа */
                    }
                """)
        layout.addWidget(self.table)
    def format_money(self, value):
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")

    def update_data(self, months_per_year, op_cf_monthly, inv_cf_monthly,
                    funding_data, net_profit_monthly,
                    interest_schedule, body_schedule,
                    monthly_rate_widget=None):

        self.yearly_labels = []
        self.yearly_free_cf = []
        self.yearly_discounted_cf = []

        years = list(months_per_year.keys())
        total_months = sum(months_per_year.values())

        # Настройка столбцов
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(["Показатель,руб", "Итого,руб"] + [str(y) for y in years])

        # 4) Расширяем первый столбец за счет уменьшения остальных
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # --- (Логика расчетов остается без изменений) ---
        fin_cf_monthly = [0.0] * total_months
        if total_months > 0:
            fin_cf_monthly[0] += funding_data.get("investments", 0.0)
            fin_cf_monthly[0] += funding_data.get("loan", 0.0)
            fin_cf_monthly[0] += funding_data.get("equity", 0.0)

        for m in range(total_months):
            interest = interest_schedule.get(m + 1, 0.0)
            body = body_schedule.get(m + 1, 0.0)
            net_profit = net_profit_monthly[m] if m < len(net_profit_monthly) else 0.0
            dividends = net_profit * 0.3 if net_profit > 0 else 0.0
            fin_cf_monthly[m] += -dividends - interest - body

        net_cf_monthly = []
        free_cf_monthly = []
        for m in range(total_months):
            op = op_cf_monthly[m] if m < len(op_cf_monthly) else 0.0
            inv = inv_cf_monthly[m] if m < len(inv_cf_monthly) else 0.0
            fin = fin_cf_monthly[m]
            net_cf_monthly.append(op + inv + fin)
            free_cf_monthly.append(op + inv)

        monthly_rates_map = {}
        if monthly_rate_widget:
            for y in years:
                le = monthly_rate_widget.cells.get(str(y))
                if le:
                    try:
                        val = le.text().replace(",", ".").strip()
                        monthly_rates_map[str(y)] = float(val) / 100 if val else 0.0
                    except:
                        monthly_rates_map[str(y)] = 0.0

        flat_rates = []
        for y in years:
            r = monthly_rates_map.get(str(y), 0.0)
            flat_rates.extend([r] * months_per_year[y])

        discounted_cf_monthly = []
        for t in range(total_months):
            fcf = free_cf_monthly[t]
            r = flat_rates[t] if t < len(flat_rates) else 0.0
            month_number = t + 1
            if r > 0:
                res = fcf / ((1 + r) ** month_number)
                discounted_cf_monthly.append(res)
            else:
                discounted_cf_monthly.append(fcf)

        self.discounted_flows = discounted_cf_monthly

        yearly_net = []
        yearly_free = []
        yearly_disc = []
        ptr = 0
        for y in years:
            cnt = months_per_year[y]
            yearly_net.append(sum(net_cf_monthly[ptr: ptr + cnt]))
            yearly_free.append(sum(free_cf_monthly[ptr: ptr + cnt]))
            yearly_disc.append(sum(self.discounted_flows[ptr: ptr + cnt]))
            ptr += cnt

        # --- 5. ВЫВОД В ТАБЛИЦУ ---
        self._fill_row(0, "Чистый ДП", yearly_net)
        self._fill_row(1, "Свободный ДП", yearly_free)
        self._fill_row(2, "Дисконтированный свободный ДП", yearly_disc)

        self.update_height()
        self.yearly_labels = [str(y) for y in years]
        self.yearly_free_cf = yearly_free
        self.yearly_discounted_cf = yearly_disc

    def _fill_row(self, row_idx, name, data_list):
        # Первый столбец: жирный шрифт, левый край
        name_item = QTableWidgetItem(name)
        name_item.setFont(self.font_tnr_bold)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row_idx, 0, name_item)

        # Итого: жирный шрифт, персиковый фон
        total_val = sum(data_list)
        total_item = QTableWidgetItem(self.format_money(total_val))
        total_item.setBackground(QColor("#FFDAB9"))
        total_item.setFont(self.font_tnr_bold)
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_idx, 1, total_item)

        # Года: обычный шрифт
        for i, val in enumerate(data_list):
            item = QTableWidgetItem(self.format_money(val))
            item.setFont(self.font_tnr_regular)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if val < 0:
                item.setForeground(QColor("red"))
            self.table.setItem(row_idx, i + 2, item)

    def update_height(self):
        # 5) Фиксированная подгонка высоты без лишних зазоров
        row_count = self.table.rowCount()
        header_height = 40
        row_height = 38

        # Точный расчет: заголовок + строки + запас на границы
        total_height = header_height + (row_height * row_count) + 2

        self.table.setFixedHeight(total_height)
        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)