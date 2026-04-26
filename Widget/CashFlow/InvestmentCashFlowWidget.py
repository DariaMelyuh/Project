from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class InvestmentCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        # 1-2) Шрифты
        self.font_title = QFont("Times New Roman", 16, QFont.Weight.Bold)
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 12)

        self.setObjectName("ICFContainer")
        # 5) Скругление 12px и основной стиль
        self.setStyleSheet(
            "QFrame#ICFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 12px; }")

        layout = QVBoxLayout(self)
        # 5) Уменьшаем нижний отступ до 5, чтобы убрать лишнее место
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        self.title = QLabel("Инвестиционный денежный поток")
        self.title.setFont(self.font_title)
        # 3) Убираем фон у названия
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
    def format_money(self, val):
        return f"{val:,.2f}".replace(',', ' ').replace('.', ',')

    def update_data(self, months_per_year, capex_data, asset_sales_data):
        indicators = [
            "Продажа активов (+)",
            "Капитальные затраты (-)",
            "Итого"
        ]

        years = list(months_per_year.keys())
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(len(indicators))
        self.table.setHorizontalHeaderLabels(["Показатель,руб", "Итого,руб"] + [str(y) for y in years])

        # 4) Расширяем первый столбец
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        results = {i: [0.0] * len(years) for i in range(len(indicators))}
        abs_month_start = 1
        for i, year in enumerate(years):
            m_count = months_per_year[year]
            m_end = abs_month_start + m_count - 1
            yearly_sales = sum(a['income'] for a in asset_sales_data if abs_month_start <= a['month'] <= m_end)
            yearly_capex = sum(c['cost'] for c in capex_data if abs_month_start <= c['month'] <= m_end)
            total_inv_dp = yearly_sales - yearly_capex

            results[0][i] = yearly_sales
            results[1][i] = yearly_capex
            results[2][i] = total_inv_dp
            abs_month_start += m_count

        for r in range(len(indicators)):
            # Названия (лево)
            name_item = QTableWidgetItem(indicators[r])
            name_item.setFont(self.font_tnr_bold)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 0, name_item)

            # Итого
            total_sum = sum(results[r])
            total_item = QTableWidgetItem(self.format_money(total_sum))
            total_item.setBackground(QColor("#FFDAB9"))
            total_item.setFont(self.font_tnr_bold)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, total_item)

            # Года
            for c in range(len(years)):
                val_item = QTableWidgetItem(self.format_money(results[r][c]))
                val_item.setFont(self.font_tnr_regular)
                val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if results[r][c] < 0:
                    val_item.setForeground(QColor("red"))
                self.table.setItem(r, c + 2, val_item)

        self.update_height()

    def update_height(self):
        # 5) Фиксированная высота без лишних зазоров
        row_count = self.table.rowCount()
        header_height = 40
        row_height = 38
        total_height = header_height + (row_height * row_count) + 2

        self.table.setFixedHeight(total_height)
        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)