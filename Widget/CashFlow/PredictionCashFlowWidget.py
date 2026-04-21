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
        self.setObjectName("PredictionCFContainer")
        # Оставляем только те данные, которые могут понадобиться для расчета итогов в таблице
        self.discounted_flows = []

        self.setStyleSheet(
            "QFrame#PredictionCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }"
        )

        layout = QVBoxLayout(self)

        self.title = QLabel("Чистый денежный поток (по годам)")
        self.title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
        layout.addWidget(self.table)

    def format_money(self, value):
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")

    def update_data(self, months_per_year, op_cf_monthly, inv_cf_monthly,
                    funding_data, net_profit_monthly,
                    interest_schedule, body_schedule,
                    monthly_rate_widget=None):

        self.yearly_labels = []  # Года
        self.yearly_free_cf = []  # Свободный ДП
        self.yearly_discounted_cf = []  # Дисконтированный ДП

        years = list(months_per_year.keys())
        total_months = sum(months_per_year.values())

        # Настройка таблицы
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(["Показатель", "Итого"] + [str(y) for y in years])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # --- 1. ПОДГОТОВКА ПОТОКОВ ---
        fin_cf_monthly = [0.0] * total_months
        if total_months > 0:
            fin_cf_monthly[0] += funding_data.get("investments", 0.0)
            fin_cf_monthly[0] += funding_data.get("loan", 0.0)
            fin_cf_monthly[0] += funding_data.get("equity", 0.0)

        for m in range(total_months):
            interest = interest_schedule.get(m + 1, 0.0)
            body = body_schedule.get(m + 1, 0.0)
            net_profit = net_profit_monthly[m] if m < len(net_profit_monthly) else 0.0
            # Дивиденды — внутренняя логика потока
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

        # --- 2. СТАВКИ ДИСКОНТИРОВАНИЯ ---
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

        # --- 3. ПОМЕСЯЧНОЕ ДИСКОНТИРОВАНИЕ ---
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

        # --- 4. АГРЕГАЦИЯ ПО ГОДАМ ---
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
        # В конец метода update_data добавьте:
        self.yearly_labels = [str(y) for y in years]
        self.yearly_free_cf = yearly_free
        self.yearly_discounted_cf = yearly_disc

    def _fill_row(self, row_idx, name, data_list):
        self.table.setItem(row_idx, 0, QTableWidgetItem(name))

        total_val = sum(data_list)
        total_item = QTableWidgetItem(self.format_money(total_val))
        total_item.setBackground(QColor("#FFDAB9"))
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_idx, 1, total_item)

        for i, val in enumerate(data_list):
            item = QTableWidgetItem(self.format_money(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if val < 0:
                item.setForeground(QColor("red"))
            self.table.setItem(row_idx, i + 2, item)

    def update_height(self):
        h = self.table.horizontalHeader().height() + (3 * 35) + 10
        self.table.setFixedHeight(h)
        self.table.setMinimumHeight(h)