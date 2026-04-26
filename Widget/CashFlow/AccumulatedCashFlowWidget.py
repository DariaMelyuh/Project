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
        # 1-2) Определение шрифтов
        self.font_title = QFont("Times New Roman", 16, QFont.Weight.Bold)
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 12)

        self.setObjectName("AccumulatedCFContainer")
        # 5) Скругление и стиль внешней рамки
        self.setStyleSheet(
            "QFrame#AccumulatedCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 12px; }"
        )

        layout = QVBoxLayout(self)
        # 5) Уменьшаем нижний отступ до 5
        layout.setContentsMargins(25, 20, 25, 5)
        layout.setSpacing(15)

        self.title = QLabel("Накопленный денежный поток (по годам)")
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

        # Стилизация согласно общему стандарту
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

    def update_data(self, months_per_year, free_cash_flows_monthly, discounted_flows_monthly, investments_only):
        years = list(months_per_year.keys())
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель, руб", "0 период (Инв.)"] + [str(y) for y in years])

        # 4) Настройка размеров колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Первый по тексту
        for i in range(1, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)  # Остальные тянутся

        rows = ["Накопленный свободный ДП", "Накопленный дисконтированный ДП"]

        # Расчеты
        cum_free = -investments_only
        cum_disc = -investments_only

        # Заполнение 0 периода
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

        # Заполнение названий строк
        for row_idx, name in enumerate(rows):
            name_item = QTableWidgetItem(name)
            name_item.setFont(self.font_tnr_bold)  # 12 шрифт жирный
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_idx, 0, name_item)

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
        item.setFont(self.font_tnr_regular) # 12 шрифт
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_negative:
            # Отрицательные: красный текст на бледно-красном фоне
            item.setBackground(QColor("#FFCDD2"))
            item.setForeground(QColor("#B71C1C"))
        else:
            # Положительные: зеленый текст на светло-зеленом фоне
            item.setBackground(QColor("#C8E6C9"))
            item.setForeground(QColor("#1B5E20"))

        self.table.setItem(row, col, item)

    def update_height(self):
        row_count = self.table.rowCount()
        header_height = 40
        row_height = 38

        # Точный расчет высоты таблицы
        total_table_height = header_height + (row_height * row_count) + 2
        self.table.setFixedHeight(total_table_height)

        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)