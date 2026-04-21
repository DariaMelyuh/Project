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


class AccumulatedCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("AccumulatedCFContainer")
        self.setStyleSheet(
            "QFrame#AccumulatedCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }"
        )

        layout = QVBoxLayout(self)

        self.title = QLabel("Накопленный денежный поток (по годам)")
        self.title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        self.title.setStyleSheet("background: transparent; border: none; padding: 5px;")
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # --- УБИРАЕМ СКРОЛЛ ---
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.table.setStyleSheet("""
            QTableWidget { 
                gridline-color: #E1EFF8; 
                border: none; 
                font-family: 'Times New Roman'; 
                font-size: 11pt; 
                background-color: white;
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

    def update_data(self, months_per_year, free_cash_flows_monthly, discounted_flows_monthly, investments_only):
        years = list(months_per_year.keys())
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(2)
        self.table.setHorizontalHeaderLabels(["Наименование", "0 период (Инв.)"] + [str(y) for y in years])

        # Растягиваем колонки
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Фиксируем высоту строк, чтобы точно рассчитать общую высоту
        for i in range(2):
            self.table.setRowHeight(i, 35)

        rows = ["Накопленный свободный ДП", "Накопленный дисконтированный ДП"]
        cum_free = -investments_only
        cum_disc = -investments_only

        self._set_item(0, 1, self.format_money(cum_free), is_negative=(cum_free < 0))
        self._set_item(1, 1, self.format_money(cum_disc), is_negative=(cum_disc < 0))

        current_month_idx = 0
        for col, year in enumerate(years, start=2):
            num_months = months_per_year[year]
            for _ in range(num_months):
                if current_month_idx < len(free_cash_flows_monthly):
                    cum_free += free_cash_flows_monthly[current_month_idx]
                    cum_disc += discounted_flows_monthly[current_month_idx]
                current_month_idx += 1

            self._set_item(0, col, self.format_money(cum_free), is_negative=(cum_free < 0))
            self._set_item(1, col, self.format_money(cum_disc), is_negative=(cum_disc < 0))

        for row_idx, name in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))

        # --- ОБНОВЛЯЕМ ВЫСОТУ ПОСЛЕ ЗАПОЛНЕНИЯ ---
        self.update_height()

    def update_height(self):
        # Высота заголовка (35) + 2 строки по 35 + небольшой запас на рамки
        header_h = self.table.horizontalHeader().height()
        if header_h == 0: header_h = 35  # на случай если заголовок еще не отрисован

        total_h = header_h + (2 * 35) + 5
        self.table.setFixedHeight(total_h)
        self.setMinimumHeight(total_h + 50)  # учитываем заголовок "Накопленный..." и отступы

    def _set_item(self, row, col, text, is_negative=False):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_negative:
            # Более выраженный, но мягкий красный (Rosy Brown / Light Coral mix)
            item.setBackground(QColor("#FFCDD2"))
            # Опционально: можно сделать текст темно-красным для лучшей читаемости
            item.setForeground(QColor("#B71C1C"))
        else:
            # Приятный, заметный зеленый (Light Green / Tea Green)
            item.setBackground(QColor("#C8E6C9"))
            # Опционально: темно-зеленый текст
            item.setForeground(QColor("#1B5E20"))

        self.table.setItem(row, col, item)