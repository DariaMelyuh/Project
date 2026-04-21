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


class FinancialCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("FCFContainer")
        self.setStyleSheet(
            "QFrame#FCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }"
        )

        layout = QVBoxLayout(self)
        self.title = QLabel("Финансовый денежный поток (по годам)")
        self.title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(
            """
            QTableWidget { gridline-color: #E1EFF8; border: none; font-family: 'Times New Roman'; font-size: 11pt; }
            QHeaderView::section { background-color: #D0E6F5; font-weight: bold; border: 1px solid #D0E6F5; height: 35px; }
            """
        )
        layout.addWidget(self.table)

    def format_money(self, value):
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")

    def update_data(self, months_per_year, funding_data, net_profit_monthly, op_cf_monthly, inv_cf_monthly,
                    interest_schedule, body_schedule):
        indicators = [
            "Инвестиции",
            "Заемные средства",
            "Собственные средства",
            "Выплата дивидендов",
            "Выплата процентов",
            "Тело кредита",
            "Итого",
        ]

        years = list(months_per_year.keys())
        total_months = sum(months_per_year.values())

        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(len(indicators))
        self.table.setHorizontalHeaderLabels(["Показатель", "Итого"] + [str(year) for year in years])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        monthly = {i: [0.0] * total_months for i in range(len(indicators))}

        if total_months > 0:
            monthly[0][0] = funding_data.get("investments", 0.0)
            monthly[1][0] = funding_data.get("loan", 0.0)
            monthly[2][0] = funding_data.get("equity", 0.0)

        for m in range(total_months):
            monthly[4][m] = interest_schedule.get(m + 1, 0.0)
            monthly[5][m] = body_schedule.get(m + 1, 0.0)

            net_profit = net_profit_monthly[m] if m < len(net_profit_monthly) else 0.0
            if net_profit > 0:
                monthly[3][m] = net_profit * 0.3

            monthly[6][m] = (
                monthly[0][m]
                + monthly[1][m]
                + monthly[2][m]
                - monthly[3][m]
                - monthly[4][m]
                - monthly[5][m]
            )



        yearly = self._aggregate_yearly(months_per_year, monthly)

        for row_idx, indicator in enumerate(indicators):
            self.table.setItem(row_idx, 0, QTableWidgetItem(indicator))

            total_value = self._get_total_value(row_idx, yearly[row_idx])
            total_item = QTableWidgetItem(self.format_money(total_value))
            total_item.setBackground(QColor("#FFDAB9"))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, total_item)

            for col_idx, value in enumerate(yearly[row_idx]):
                item = QTableWidgetItem(self.format_money(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx + 2, item)

        self.update_height()

    def _aggregate_yearly(self, months_per_year, monthly):
        yearly = {i: [] for i in monthly.keys()}
        month_ptr = 0

        for year in months_per_year:
            month_count = months_per_year[year]
            segment_end = month_ptr + month_count

            for row_idx, values in monthly.items():
                segment = values[month_ptr:segment_end]
                yearly[row_idx].append(sum(segment))

            month_ptr = segment_end

        return yearly

    def _get_total_value(self, row_idx, values):
        if not values:
            return 0.0
        return sum(values)

    def update_height(self):
        height = self.table.horizontalHeader().height() + (self.table.rowCount() * 35) + 20
        self.table.setFixedHeight(height)
