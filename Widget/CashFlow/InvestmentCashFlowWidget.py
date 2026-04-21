from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class InvestmentCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("ICFContainer")
        self.setStyleSheet(
            "QFrame#ICFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")

        layout = QVBoxLayout(self)
        self.title = QLabel("Инвестиционный денежный поток (по годам)")
        self.title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { gridline-color: #E1EFF8; border: none; font-family: 'Times New Roman'; font-size: 11pt; }
            QHeaderView::section { background-color: #D0E6F5; font-weight: bold; border: 1px solid #D0E6F5; height: 35px; }
        """)
        layout.addWidget(self.table)

    def format_money(self, val):
        return f"{val:,.2f}".replace(',', ' ').replace('.', ',')

    def update_data(self, months_per_year, capex_data, asset_sales_data):
        """
        capex_data: список [{'cost':..., 'month':...}]
        asset_sales_data: список [{'income':..., 'month':...}]
        """
        indicators = [
            "Продажа активов (+)",
            "Капитальные затраты (CapEx) (-)",
            "Итого инвестиционный ДП"
        ]

        years = list(months_per_year.keys())
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(len(indicators))
        self.table.setHorizontalHeaderLabels(["Показатель", "Итого"] + [str(y) for y in years])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Подготовка хранилища данных по годам
        results = {i: [0.0] * len(years) for i in range(len(indicators))}

        abs_month_start = 1
        for i, year in enumerate(years):
            m_count = months_per_year[year]
            m_end = abs_month_start + m_count - 1

            # 1. Собираем продажи активов в этом интервале месяцев
            yearly_sales = sum(a['income'] for a in asset_sales_data if abs_month_start <= a['month'] <= m_end)

            # 2. Собираем CapEx (без амортизации, только факт оплаты)
            yearly_capex = sum(c['cost'] for c in capex_data if abs_month_start <= c['month'] <= m_end)

            # 3. Итог = Продажи - Капекс
            total_inv_dp = yearly_sales - yearly_capex

            results[0][i] = yearly_sales
            results[1][i] = yearly_capex
            results[2][i] = total_inv_dp

            abs_month_start += m_count

        # Заполнение таблицы
        for r in range(len(indicators)):
            self.table.setItem(r, 0, QTableWidgetItem(indicators[r]))

            # Колонка "Итого"
            total_sum = sum(results[r])
            total_item = QTableWidgetItem(self.format_money(total_sum))
            total_item.setBackground(QColor("#FFDAB9"))  # Персиковый для итогов
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, total_item)

            # Значения по годам
            for c in range(len(years)):
                val_item = QTableWidgetItem(self.format_money(results[r][c]))
                val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Подсветка отрицательных значений красным
                if results[r][c] < 0:
                    val_item.setForeground(QColor("red"))
                self.table.setItem(r, c + 2, val_item)

        self.update_height()

    def update_height(self):
        h = self.table.horizontalHeader().height() + (self.table.rowCount() * 35) + 20
        self.table.setFixedHeight(h)