import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class CapitalExpenditureWidget(QFrame):
    data_confirmed = pyqtSignal()
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setObjectName("CapExContainer")

        self.PROJECT_HORIZON = 12
        self.current_data = []

        # Данные
        self.default_data_list = [
            ["Актив 1", 0, 1, 10, 1000.0, 0], ["Актив 2", 0, 1, 12, 10000.0, 0],
            ["Актив 3", 0, 2, 11, 5000.0, 0], ["Актив 4", 0, 1, 5, 7000.0, 0],
            ["Актив 5", 0, 1, 12, 500.0, 0], ["Актив 6", 0, 1, 10, 650.0, 0],
            ["Актив 7", 0, 3, 12, 300.0, 0], ["Актив 8", 0, 5, 5, 250.0, 0],
            ["Актив 9", 0, 6, 10, 1500.0, 0], ["Актив 10", 0, 1, 12, 8000.0, 0]
        ]

        self.setStyleSheet(
            "QFrame#CapExContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)

        # 1. ЗАГОЛОВОК: Черный цвет шрифта
        title = QLabel("Капитальные затраты")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background: transparent; border: none;")  # Установлен черный цвет
        self.layout.addWidget(title)

        # 2. ТАБЛИЦА

        self.table = QTableWidget(10, 6)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        headers = [
            "Наименование актива", "Итоговая\nстоимость, руб", "Месяц\nпокупки",
            "Срок службы\n(мес)", "Базовая\nстоимость, руб", "Параметр изм.\nцены, %"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(65)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)

        self.setFixedWidth(860)
        self.setFixedHeight(427)
        self.table.setFixedWidth(790)



        self.table.setColumnWidth(0, 200)
        for i in range(1, 6):
            self.table.setColumnWidth(i, 115)

        # 3. СТИЛИЗАЦИЯ ТАБЛИЦЫ И ЦВЕТНОГО СКРОЛЛБАРА
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #D0E6F5; 
                border-radius: 15px;      
                gridline-color: #E1EFF8; 
                font-family: 'Times New Roman'; 
                font-size: 12pt;
                background-color: white; 
                outline: 0;
            }
            QHeaderView::section { 
                background-color: #B9D9EB; 
                color: black; 
                font-family: 'Times New Roman'; 
                font-weight: bold; 
                font-size: 11pt;
                border: 1px solid #D0E6F5; 
                padding: 2px; 
            }
            QHeaderView::section:horizontal:first { border-top-left-radius: 15px; }
            QHeaderView::section:horizontal:last { border-top-right-radius: 15px; }

            /* ВЕРТИКАЛЬНЫЙ СКРОЛЛБАР */
            QScrollBar:vertical {
                border: none;
                background: #F0F8FF;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #B9D9EB;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background-color: #A1C9DE; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

            /* ГОРИЗОНТАЛЬНЫЙ СКРОЛЛБАР */
            QScrollBar:horizontal {
                border: none;
                background: #F0F8FF;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #B9D9EB;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """)

        self.fill_default_data()
        self.table.cellChanged.connect(self.validate_cell)
        self.table.setFixedHeight(35 * 9)
        self.layout.addWidget(self.table)

        self.apply_btn = QPushButton("Принять данные")
        self.apply_btn.setFixedSize(220, 35)
        self.set_apply_btn_style("default")
        self.apply_btn.clicked.connect(self.accept_data)
        self.layout.addWidget(self.apply_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.accept_data()

    # ... (методы format_val, fill_default_data, recalculate_row остаются без изменений) ...

    def validate_cell(self, row, col):
        # Если сигналы заблокированы или это колонка с названием актива (0) — выходим
        if self.table.signalsBlocked() or col == 0:
            return

        item = self.table.item(row, col)
        if not item:
            return

        # 1. ОЧИСТКА ВВОДА: Удаляем пробелы и меняем запятую на точку для расчетов
        raw_text = item.text().strip()
        clean_text = raw_text.replace(' ', '').replace(',', '.')

        asset_name_item = self.table.item(row, 0)
        asset_name = asset_name_item.text().strip() if asset_name_item else f"Строка {row + 1}"

        try:
            # Преобразуем в число
            val = float(clean_text)
            if val < 0:
                raise ValueError("Отрицательное значение")

            # 2. ПРОВЕРКИ ПО КОЛОНКАМ

            # Месяц покупки (Колонка 2)
            if col == 2:
                if not val.is_integer():
                    raise ValueError("Должно быть целым числом")
                if val < 1 or val > self.PROJECT_HORIZON:
                    raise ValueError(f"Месяц должен быть от 1 до {self.PROJECT_HORIZON}")

            # Срок службы (Колонка 3)
            elif col == 3:
                if not val.is_integer():
                    raise ValueError("Должно быть целым числом")
                # Получаем месяц покупки из таблицы (чистим его от пробелов на всякий случай)
                m_item = self.table.item(row, 2)
                m_val = int(float(m_item.text().replace(' ', '').replace(',', '.'))) if m_item else 1

                if val < 1:
                    raise ValueError("Минимум 1 месяц")
                # Условие: Месяц покупки + срок службы - 1 <= Горизонт проекта
                if (m_val + val - 1) > self.PROJECT_HORIZON:
                    raise ValueError(f"Выход за горизонт планирования ({self.PROJECT_HORIZON} мес.)")

            # Базовая стоимость (Колонка 4)
            elif col == 4:
                if val > 1_000_000_000:  # 1 миллиард
                    raise ValueError("Слишком большая сумма")

                # СРАЗУ КРАСИВО ФОРМАТИРУЕМ ВВОД
                self.table.blockSignals(True)
                item.setText(self.format_as_money(val))
                self.table.blockSignals(False)

            # Параметр изменения цены % (Колонка 5)
            elif col == 5:
                if val > 100:
                    raise ValueError("Максимум 100%")

            # 3. ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ
            self.apply_btn.setText("Принять изменения*")
            self.set_apply_btn_style("warning")

            # Пересчитываем итоговую стоимость (Col 1), если изменилась цена или %
            if col in [4, 5]:
                self.recalculate_row(row)



        except ValueError as e:
            # 1. Блокируем сигналы, чтобы избежать бесконечного цикла (рекурсии)
            self.table.blockSignals(True)
            # Показываем окно с ошибкой (вызываем ваш метод)
            self.show_error(str(e), asset_name, col)
            # 2. Вовращаем старое (дефолтное) значение из списка
            # Внимание: убедитесь, что индексы в default_data_list совпадают!
            # (Название 0, Итого 1, Месяц 2, Срок 3, База 4, % 5)
            original_val = self.default_data_list[row][col]
            if col in [4]:  # Если это стоимость
                item.setText(self.format_as_money(original_val))
            else:
                item.setText(self.format_val(original_val))
            # 3. Возвращаем цвет фона (светло-голубой для ввода)
            item.setBackground(QBrush(QColor("#E0F7FF")))
            # 4. Пересчитываем строку, если нужно
            self.recalculate_row(row)
            # 5. РАЗБЛОКИРУЕМ сигналы обратно
            self.table.blockSignals(False)
    def show_error(self, message, asset_name, col):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(QFont("Times New Roman", 12))

        # Динамическая подсказка
        if col == 2:
            limit_hint = f"целое число от <b>1</b> до <b>{self.PROJECT_HORIZON}</b>"
        elif col == 3:
            limit_hint = f"целое число (сумма месяца покупки и срока не более <b>{self.PROJECT_HORIZON}</b>)"
        elif col == 4:
            limit_hint = "положительное число от <b>0</b> до <b>1 000 000</b>"
        elif col == 5:
            limit_hint = "процент от <b>0</b> до <b>100</b>"
        else:
            limit_hint = "положительное число"

        error_text = f"Актив: <b>{asset_name}</b><br><br>"
        error_text += f"Ошибка: <b>{message}</b><br>"
        error_text += f"Требование: {limit_hint}.<br><br>"
        error_text += "Будет возвращено исходное значение."

        msg.setText(error_text)
        msg.setStyleSheet("""
            QMessageBox QLabel { color: #333333; min-width: 500px; }
            QPushButton { 
                min-width: 90px; padding: 5px; background-color: #E0F7FF;
                border: 1px solid #87CEFA; border-radius: 5px; 
            }
        """)
        msg.exec()

    def format_val(self, val):
        """Вспомогательная функция для форматирования чисел в таблицу"""
        return str(val).replace('.', ',')

    def fill_default_data(self):
        self.table.blockSignals(True)
        for r in range(10):
            data = self.default_data_list[r]
            total_val = data[4] + (data[4] * data[5] / 100)
            data[1] = total_val

            for c in range(6):
                # Для стоимости используем денежный формат, для остальных — обычный
                if c in [1, 4]:
                    val_text = self.format_as_money(data[c])
                else:
                    val_text = self.format_val(data[c])

                item = QTableWidgetItem(val_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if c == 1:
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    item.setBackground(QBrush(QColor("#F9F9F9")))
                else:
                    item.setBackground(QBrush(QColor("#E0F7FF")))
                self.table.setItem(r, c, item)
            self.table.setRowHeight(r, 35)
        self.table.blockSignals(False)

    def recalculate_row(self, row):
        # Здесь сигналы УЖЕ заблокированы в validate_cell (в блоке except),
        # но добавим страховку на случай вызова из других мест
        was_blocked = self.table.signalsBlocked()
        if not was_blocked: self.table.blockSignals(True)

        try:
            base_item = self.table.item(row, 4)
            param_item = self.table.item(row, 5)
            if base_item and param_item:
                base = float(base_item.text().replace(',', '.'))
                param = float(param_item.text().replace(',', '.'))
                total = base + (base * (param / 100))
                self.table.item(row, 1).setText(self.format_as_money(total))
        except:
            pass

        if not was_blocked: self.table.blockSignals(False)



    def set_apply_btn_style(self, state):
        styles = {
            "default": "background-color: #E0F7FF; color: #2C3E50; border-radius: 8px; font-weight: bold; border: 1px solid #B0D4E3;",
            "success": "background-color: #C8E6C9; color: #2E7D32; border-radius: 8px; font-weight: bold; border: 1px solid #A5D6A7;",
            "warning": "background-color: #FFF9C4; color: #827717; border-radius: 8px; font-weight: bold; border: 1px solid #FFF176;"
        }
        self.apply_btn.setStyleSheet(styles.get(state, styles["default"]))

    def accept_data(self):
        new_data = []
        for r in range(self.table.rowCount()):
            row_data = []
            for c in range(6):
                item = self.table.item(r, c)
                val = item.text().replace(' ', '').replace(',', '.')
                if c > 0:
                    try:
                        val = float(val)
                    except:
                        val = 0.0
                else:
                    val = item.text() if item else ""
                row_data.append(val)
            new_data.append(row_data)
        self.current_data = new_data
        self.apply_btn.setText("Данные приняты ✓")
        self.set_apply_btn_style("success")
        QTimer.singleShot(2000, self.reset_button)
        self.data_confirmed.emit()
    def reset_button(self):
        self.apply_btn.setText("Принять данные")
        self.set_apply_btn_style("default")

    def set_project_horizon(self, new_horizon):
        """Метод для динамического обновления лимита из MainWindow"""
        try:
            self.PROJECT_HORIZON = int(new_horizon)
            # Принудительно проверяем текущие значения в таблице под новый горизонт
            self.table.blockSignals(True)
            for r in range(self.table.rowCount()):
                self._check_and_fix_row_limits(r)
            self.table.blockSignals(False)
        except ValueError:
            pass

    def _check_and_fix_row_limits(self, row):
        """Вспомогательный метод для проверки строки при смене общего горизонта"""
        for col in [2, 3]:
            item = self.table.item(row, col)
            if item:
                val = float(item.text().replace(',', '.'))
                # Если текущее значение больше нового горизонта — ставим дефолт
                if col == 2 and val > self.PROJECT_HORIZON:
                    item.setText(self.format_val(self.default_data_list[row][col]))
                elif col == 3:
                    m_val = float(self.table.item(row, 2).text().replace(',', '.'))
                    if (m_val + val - 1) > self.PROJECT_HORIZON:
                        item.setText(self.format_val(self.default_data_list[row][col]))

    def format_as_money(self, val):
        """Форматирует число в строку вида '1 000,00'"""
        try:
            # Превращаем в float, если пришла строка
            f_val = float(str(val).replace(',', '.').replace(' ', ''))
            # f"{...:,.2f}" делает 1,000.00, затем меняем запятую на пробел, а точку на запятую
            formatted = f"{f_val:,.2f}".replace(',', ' ').replace('.', ',')
            return formatted
        except:
            return str(val)

    def get_capex_full_data(self):
        """Возвращает список активов с их стоимостью и месяцем покупки"""
        capex_list = []
        # Проходим по всем строкам таблицы
        for r in range(self.table.rowCount()):
            try:
                name = self.table.item(r, 0).text()
                # Индексы: 1 - Итоговая цена, 2 - Месяц покупки
                total_price = float(self.table.item(r, 1).text().replace(' ', '').replace(',', '.'))
                buy_month = int(float(self.table.item(r, 2).text().replace(',', '.')))

                capex_list.append({
                    'name': name,
                    'cost': total_price,
                    'month': buy_month
                })
            except Exception as e:
                print(f"Ошибка парсинга CapEx в строке {r}: {e}")
        return capex_list

    def get_capex_full_data(self):
        capex_list = []
        for r in range(self.table.rowCount()):
            try:
                total_price = float(self.table.item(r, 1).text().replace(' ', '').replace(',', '.'))
                buy_month = int(float(self.table.item(r, 2).text().replace(',', '.')))
                term = int(float(self.table.item(r, 3).text().replace(',', '.')))  # Срок службы
                capex_list.append({'cost': total_price, 'month': buy_month, 'term': term})
            except:
                continue
        return capex_list