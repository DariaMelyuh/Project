from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class OperationalCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("OCFContainer")
        self.setStyleSheet(
            "QFrame#OCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")

        layout = QVBoxLayout(self)
        self.title = QLabel("Операционный денежный поток (по годам)")
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

    def update_data(self, months_per_year, yearly_basic_data, capex_data, vat_map):
        """
        yearly_basic_data: словарь со списками [выручка, опекс, налог_усн] по годам
        capex_data: список словарей [{'cost':..., 'month':...}]
        vat_map: словарь {год: ставка_ндс}
        """
        indicators = [
            "Выручка (без НДС)",
            "Операционные затраты",
            "Налог (УСН)",
            "НДС с продажи",
            "НДС к вычету",
            "НДС к уплате",
            "Переплата по НДС",
            "Итого налоги к уплате",
            "Итого операционный ДП"
        ]

        years = list(months_per_year.keys())
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(len(indicators))
        self.table.setHorizontalHeaderLabels(["Показатель", "Итого"] + [str(y) for y in years])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Распределяем CapEx по календарным годам для вычета НДС
        capex_yearly = {str(y): 0.0 for y in years}
        abs_month_start = 1
        for y in years:
            m_count = months_per_year[y]
            m_end = abs_month_start + m_count - 1
            for asset in capex_data:
                if abs_month_start <= asset['month'] <= m_end:
                    capex_yearly[str(y)] += asset['cost']
            abs_month_start += m_count

        # Инициализация итоговых массивов
        results = {i: [0.0] * len(years) for i in range(len(indicators))}

        for i, year in enumerate(years):
            y_str = str(year)
            vat_rate = vat_map.get(y_str, 0.0)

            # Базовые данные из первой таблицы
            rev = yearly_basic_data['rev'][i]
            opex = yearly_basic_data['opex'][i]
            tax_usn = yearly_basic_data['tax'][i]
            capex = capex_yearly[y_str]

            # РАСЧЕТЫ ПО ВАШЕМУ ТЗ
            vat_sales = rev * vat_rate
            vat_deduction = (capex + opex) * vat_rate

            raw_vat_pay = vat_sales - vat_deduction
            vat_to_pay = max(0, raw_vat_pay)
            overpayment = abs(min(0, raw_vat_pay))

            # Итого налоги = Налог + НДС к уплате
            total_taxes = tax_usn + vat_to_pay

            op_cf = rev - opex - total_taxes

            # Сохраняем для таблицы
            row_vals = [rev, opex, tax_usn, vat_sales, vat_deduction, vat_to_pay, overpayment, total_taxes, op_cf]
            for row_idx, val in enumerate(row_vals):
                results[row_idx][i] = val

        # Заполнение
        for r in range(len(indicators)):
            self.table.setItem(r, 0, QTableWidgetItem(indicators[r]))

            total_sum = sum(results[r])
            total_item = QTableWidgetItem(self.format_money(total_sum))
            total_item.setBackground(QColor("#FFDAB9"))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, total_item)

            for c in range(len(years)):
                val_item = QTableWidgetItem(self.format_money(results[r][c]))
                val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c + 2, val_item)

        self.update_height()

    def update_height(self):
        h = self.table.horizontalHeader().height() + (self.table.rowCount() * 35) + 20
        self.table.setFixedHeight(h)

    # Добавьте это в класс OperatingExpensesWidget
    def get_base_opex(self):
        """Считаем сумму по списку данных, а не из текста таблицы"""
        total_opex = 0.0
        # Используем self.expenses_data, который у нас всегда есть
        for row in self.expenses_data:
            # row[1] - база, row[2] - параметр изменения %
            base = row[1]
            perc = row[2]
            total_opex += base * (1 + perc / 100)
        return total_opex