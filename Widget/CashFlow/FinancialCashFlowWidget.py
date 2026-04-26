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

        self.font_title = QFont("Times New Roman", 16, QFont.Weight.Bold)
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 12)

        self.setObjectName("FCFContainer")
        # 5) Скругление 12px и основной стиль
        self.setStyleSheet(
            "QFrame#FCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 12px; }"
        )

        layout = QVBoxLayout(self)
        # 5) Уменьшаем нижний отступ до 5, чтобы убрать лишнее место внизу
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        self.title = QLabel("Финансовый денежный поток")
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

        # Отключаем скроллбары, чтобы не создавали "щелей"
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Стилизация таблицы согласно общему стилю
        self.table.setStyleSheet(
            """
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
                border: 1px solid #D0E6F5; 
            }
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
        self.table.setHorizontalHeaderLabels(["Показатель,руб", "Итого,руб"] + [str(year) for year in years])

        # 4) Расширяем первый столбец за счет уменьшения остальных
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # По тексту
        for i in range(1, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)  # Остальные тянутся

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
            # Первый столбец: выравнивание по левому краю, жирный шрифт
            name_item = QTableWidgetItem(indicator)
            name_item.setFont(self.font_tnr_bold)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_idx, 0, name_item)

            # Колонка "Итого": персиковый фон, жирный шрифт
            total_value = self._get_total_value(row_idx, yearly[row_idx])
            total_item = QTableWidgetItem(self.format_money(total_value))
            total_item.setBackground(QColor("#FFDAB9"))
            total_item.setFont(self.font_tnr_bold)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # --- ДОБАВЛЕНО: Проверка на отрицательное число для Итого ---
            if total_value < 0:
                total_item.setForeground(QColor("red"))

            self.table.setItem(row_idx, 1, total_item)

            # Годовые значения: обычный 12 шрифт
            for col_idx, value in enumerate(yearly[row_idx]):
                item = QTableWidgetItem(self.format_money(value))
                item.setFont(self.font_tnr_regular)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # --- ДОБАВЛЕНО: Проверка на отрицательное число для годов ---
                if value < 0:
                    item.setForeground(QColor("red"))

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
        # 5) Фиксированная подгонка высоты без лишних зазоров
        row_count = self.table.rowCount()
        header_height = 40
        row_height = 38

        # Точный расчет: заголовок + строки + минимальный запас на границы
        total_height = header_height + (row_height * row_count) + 2

        self.table.setFixedHeight(total_height)
        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)
