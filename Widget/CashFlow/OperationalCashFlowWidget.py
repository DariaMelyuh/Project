from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt


class OperationalCashFlowWidget(QFrame):
    def __init__(self):
        super().__init__()
        # 1-2) Определение шрифтов (Times New Roman)
        self.font_title = QFont("Times New Roman", 16, QFont.Weight.Bold)
        self.font_tnr_bold = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.font_tnr_regular = QFont("Times New Roman", 12)

        self.setObjectName("OCFContainer")
        # 5) Уменьшаем нижний отступ в setContentsMargins (последнее число 5 вместо 20)
        self.setStyleSheet(
            "QFrame#OCFContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 12px; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)  # Убираем лишнее место внизу блока
        layout.setSpacing(15)

        self.title = QLabel("Операционный денежный поток")
        self.title.setFont(self.font_title)  # Название 16 шрифтом
        # 3) Убираем серый фон у названия (background: transparent)
        self.title.setStyleSheet("color: #2C3E50; border: none; background: transparent;")
        layout.addWidget(self.title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(True)

        # Настройка скроллбаров, чтобы не создавали "щели"
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
    def format_money(self, val):
        return f"{val:,.2f}".replace(',', ' ').replace('.', ',')

    def update_data(self, months_per_year, yearly_basic_data, capex_data, vat_map):
        """
        yearly_basic_data: словарь со списками [выручка, опекс, налог_усн] по годам
        capex_data: список словарей [{'cost':..., 'month':...}]
        vat_map: словарь {год: ставка_ндс}
        """
        indicators = [
            "Выручка", "Операционные затраты", "Налог (УСН)",
            "НДС с продажи", "НДС к вычету", "НДС к уплате",
            "Переплата по НДС", "Итого налоги к уплате", "Итого"
        ]

        years = list(months_per_year.keys())
        self.table.setColumnCount(len(years) + 2)
        self.table.setRowCount(len(indicators))
        self.table.setHorizontalHeaderLabels(["Показатель,руб", "Итого,руб"] + [str(y) for y in years])

        # 4) Расширяем первый столбец, остальные сжимаем
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # По тексту
        for i in range(1, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)  # Остаток поровну

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
            # Названия строк (лево)
            name_item = QTableWidgetItem(indicators[r])
            name_item.setFont(self.font_tnr_bold)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 0, name_item)

            # Колонка Итого (персиковая)
            total_sum = sum(results[r])
            total_item = QTableWidgetItem(self.format_money(total_sum))
            total_item.setBackground(QColor("#FFDAB9"))
            total_item.setFont(self.font_tnr_bold)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # --- ДОБАВЛЕНО: Проверка на отрицательное значение в Итого ---
            if total_sum < 0:
                total_item.setForeground(QColor("red"))

            self.table.setItem(r, 1, total_item)

            # Годовые данные
            for c in range(len(years)):
                val = results[r][c]
                val_item = QTableWidgetItem(self.format_money(val))
                val_item.setFont(self.font_tnr_regular)  # 12 шрифт
                val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # --- ДОБАВЛЕНО: Проверка на отрицательное значение в годах ---
                if val < 0:
                    val_item.setForeground(QColor("red"))

                self.table.setItem(r, c + 2, val_item)

        self.update_height()
    def update_height(self):
        """Точная подгонка высоты для удаления пустых мест снизу"""
        row_count = self.table.rowCount()
        header_height = 40
        row_height = 38

        # +2 пикселя для плотного прилегания границ
        total_height = header_height + (row_height * row_count) + 2

        self.table.setFixedHeight(total_height)
        self.table.horizontalHeader().setFixedHeight(header_height)
        for i in range(row_count):
            self.table.setRowHeight(i, row_height)

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