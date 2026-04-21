import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class OperatingExpensesWidget(QFrame):
    data_confirmed = pyqtSignal()
    def __init__(self, input_widget=None):
        super().__init__()
        self.input_widget = input_widget
        self.setObjectName("OpExContainer")

        # Данные по умолчанию
        self.expenses_data = [
            ["Фонд оплаты труда", 145442.32, 0],
            ["Расходные материалы", 10000.0, 0],
            ["Аренда", 5000.0, 0],
            ["Коммунальные услуги", 2500.0, 0],
            ["ИТ услуги / подписки", 4500.0, 0],
            ["Обучение сотрудников", 5000.0, 0],
            ["Транспортные расходы", 1000.0, 0]
        ]

        # Стиль контейнера
        self.setStyleSheet("""
            QFrame#OpExContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)

        # 1. ЗАГОЛОВОК
        title = QLabel("Операционные затраты")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background: transparent; border: none;")
        self.layout.addWidget(title)

        # 2. ТАБЛИЦА
        self.table = QTableWidget(len(self.expenses_data), 4)

        # Текст с переносом
        headers = [
            "Наименование",
            "Итоговая\nстоимость, руб",
            "Стоимость,\nруб",
            "Параметр изм.\nстоимости, %"
        ]

        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)

        # Установка высоты и режима переноса
        self.table.horizontalHeader().setFixedHeight(68)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)

        # Стили (не забудьте про закругления, которые мы добавили ранее)
        self.table.horizontalHeader().setStyleSheet("""
                    QHeaderView::section { 
                        padding: 2px; 
                    }
                """)

        # Размеры
        # --- ИСПРАВЛЕННЫЕ РАЗМЕРЫ ---
        self.setFixedWidth(648)  # Уменьшаем ширину самого контейнера, чтобы не было дырки справа

        # Ширина таблицы должна быть равна сумме колонок + 2-4 пикселя на рамки
        self.table.setFixedWidth(572)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 140)
        self.table.setColumnWidth(3, 80)

        # Стилизация таблицы как в первом примере
        # Стилизация таблицы с закруглением углов
        self.table.setStyleSheet("""
                    QTableWidget { 
                        border: 1px solid #D0E6F5; 
                        border-radius: 15px;      /* Закругление самой таблицы */
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
                    /* Закругление углов для шапки таблицы */
                    QHeaderView::section:horizontal:first {
                        border-top-left-radius: 14px;
                    }
                    QHeaderView::section:horizontal:last {
                        border-top-right-radius: 14px;
                    }
                    QTableWidget::item { color: black; }
                """)
        self.fill_data()
        self.table.cellChanged.connect(self.validate_cell)
        self.table.setFixedHeight(318)

        self.layout.addWidget(self.table)

        # 3. ФУТЕР
        footer_layout = QHBoxLayout()
        self.total_label = QLabel("ИТОГО: 0,00 руб.")
        self.total_label.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet("""
            padding: 10px; 
            background: #FFDAB9; 
            border-radius: 8px; 
            color: black;
            border: 1px solid #D0E6F5;
        """)
        footer_layout.addWidget(self.total_label)
        footer_layout.addStretch()

        self.apply_btn = QPushButton("Принять данные")
        self.apply_btn.setFixedSize(220, 35)
        self.set_apply_btn_style("default")
        self.apply_btn.clicked.connect(self.accept_data)
        footer_layout.addWidget(self.apply_btn)

        self.layout.addLayout(footer_layout)
        self.update_overall_total()

    def fill_data(self):
        self.table.blockSignals(True)
        for r, data in enumerate(self.expenses_data):
            # Наименование
            name_item = QTableWidgetItem(data[0])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # --- ИСПРАВЛЕНИЕ: ЗАПРЕТ РЕДАКТИРОВАНИЯ ПЕРВОГО СТОЛБЦА ---
            # Убираем флаг редактирования, оставляя возможность выделения
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(r, 0, name_item)

            # Итоговая сумма (Колонка 1 - только для чтения)
            total = data[1] + (data[1] * data[2] / 100)
            res_item = QTableWidgetItem(self.format_as_money(total))
            res_item.setFlags(res_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            res_item.setBackground(QBrush(QColor("#F9F9F9")))
            res_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, res_item)

            # База (Колонка 2)
            base_item = QTableWidgetItem(self.format_as_money(data[1]))
            base_item.setBackground(QBrush(QColor("#E0F7FF")))
            base_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, base_item)

            # % (Колонка 3)
            perc_item = QTableWidgetItem(str(data[2]))
            perc_item.setBackground(QBrush(QColor("#E0F7FF")))
            perc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, perc_item)

            self.table.setRowHeight(r, 35)
        self.table.blockSignals(False)
    def format_as_money(self, val):
        return f"{val:,.2f}".replace(',', ' ').replace('.', ',')

    def show_error_msg(self, field_name, rules, default_val, unit):
        """Вызов всплывающего окна в стиле вашего примера"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")


        error_text = f"Параметр: <b>{field_name}</b><br><br>"
        error_text += f"Допустимые значения: <b>{rules}</b>.<br>"
        error_text += "Символы, буквы и некорректные значения не допускаются.<br><br>"
        error_text += f"Будет восстановлено значение по умолчанию: <b>{default_val} {unit}</b>"

        msg.setText(error_text)
        msg.setStyleSheet("""
            QMessageBox QLabel { 
                color: #333333; 
                min-width: 400px; 
                font-family: 'Times New Roman'; 
                font-size: 16px;
            }
            QPushButton { 
                font-family: 'Times New Roman'; 
                font-size: 14px; 
                min-width: 100px; 
                padding: 8px; 
                background-color: #E0F7FF;
                border: 1px solid #87CEFA;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #B9D9EB; }
        """)
        msg.exec()

    # --- ОБНОВЛЕННЫЙ МЕТОД ВАЛИДАЦИИ ---
    def validate_cell(self, row, col):
        if col == 0 or col == 1: return  # Не трогаем имя и итог

        self.table.blockSignals(True)
        item = self.table.item(row, col)
        raw_text = item.text().strip().replace(' ', '').replace(',', '.')

        # Убираем точку в конце, если пользователь случайно её поставил
        if raw_text.endswith('.'): raw_text = raw_text[:-1]

        try:
            if not raw_text: raise ValueError
            val = float(raw_text)

            # Проверка для СТОИМОСТИ (Колонка 2)
            if col == 2:
                if not (0 <= val <= 3000000):
                    default_val = self.expenses_data[row][1]
                    self.show_error_msg("Стоимость (база)", "от 0 до 3 000 000", self.format_as_money(default_val),
                                        "руб.")
                    raise ValueError

                # Если всё ок, форматируем ввод
                item.setText(self.format_as_money(val))

            # Проверка для ПАРАМЕТРА ИЗМЕНЕНИЯ (Колонка 3)
            elif col == 3:
                if not (0 <= val <= 100):
                    default_val = self.expenses_data[row][2]
                    self.show_error_msg("Параметр изменения", "от 0 до 100%", default_val, "%")
                    raise ValueError

                # Форматируем ввод (убираем лишние нули после запятой если целое)
                item.setText(str(val).replace('.', ','))

            # Общий пересчет если ошибок нет
            self.recalculate_row(row)
            self.set_apply_btn_style("warning")
            self.update_overall_total()

        except ValueError:
            # Возврат к значениям по умолчанию из исходных данных
            if col == 2:
                item.setText(self.format_as_money(self.expenses_data[row][1]))
            else:
                item.setText(str(self.expenses_data[row][2]).replace('.', ','))

            self.recalculate_row(row)
            self.update_overall_total()

        self.table.blockSignals(False)

    def recalculate_row(self, row):
        """Вспомогательный метод для пересчета итогов в строке"""
        try:
            base = float(self.table.item(row, 2).text().replace(' ', '').replace(',', '.'))
            perc = float(self.table.item(row, 3).text().replace(' ', '').replace(',', '.'))
            total = base + (base * perc / 100)
            self.table.item(row, 1).setText(self.format_as_money(total))
        except:
            pass
    def update_overall_total(self):
        total_sum = 0
        for r in range(self.table.rowCount()):
            val = float(self.table.item(r, 1).text().replace(' ', '').replace(',', '.'))
            total_sum += val
        self.total_label.setText(f"ИТОГО: {total_sum:,.2f} руб.".replace(',', ' ').replace('.', ','))

    def set_apply_btn_style(self, state):
        styles = {
            "default": "background-color: #E0F7FF; color: #2C3E50; border-radius: 8px; font-weight: bold; border: 1px solid #B0D4E3;",
            "success": "background-color: #C8E6C9; color: #2E7D32; border-radius: 8px; font-weight: bold; border: 1px solid #A5D6A7;",
            "warning": "background-color: #FFF9C4; color: #827717; border-radius: 8px; font-weight: bold; border: 1px solid #FFF176;"
        }
        self.apply_btn.setStyleSheet(styles.get(state, styles["default"]))
        if state == "warning":
            self.apply_btn.setText("Принять изменения *")
        elif state == "success":
            self.apply_btn.setText("Данные приняты ✓")
        else:
            self.apply_btn.setText("Принять данные")

    def accept_data(self):
        # 1. Сохраняем измененные данные из таблицы в память (self.expenses_data)
        for r in range(self.table.rowCount()):
            try:
                self.expenses_data[r][1] = float(self.table.item(r, 2).text().replace(' ', '').replace(',', '.'))
                self.expenses_data[r][2] = float(self.table.item(r, 3).text().replace(' ', '').replace(',', '.'))
            except:
                continue

        # 2. Визуальный эффект кнопки
        self.set_apply_btn_style("success")
        QTimer.singleShot(2000, lambda: self.set_apply_btn_style("default"))

        # 3. КРИТИЧЕСКИ ВАЖНО: Отправляем сигнал, что данные подтверждены
        # MainWindow поймает этот сигнал и вызовет sync_yearly_table
        self.data_confirmed.emit()

    def handle_apply_click(self):
        # Любая логика сохранения...
        self.data_confirmed.emit()  # БЕЗ ЭТОЙ СТРОКИ НИЧЕГО НЕ ПРОИЗОЙДЕТ

    def get_base_opex_sum(self):
        total_base = 0.0
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 1) # Берем итоговую колонку из виджета затрат
            if item and item.text():
                try:
                    clean_val = item.text().replace(' ', '').replace(',', '.')
                    total_base += float(clean_val)
                except ValueError:
                    continue
        return total_base

# В методе, который привязан к кнопке "Принять данные" в OperatingExpensesWidget

    def get_base_opex(self):
        """
        Возвращает суммарные операционные расходы.
        Этот метод вызывается в main.py для синхронизации таблиц.
        """
        total_opex = 0.0
        for r in range(self.table.rowCount()):
            # Берем значение из колонки "Итоговая стоимость" (индекс 1)
            item = self.table.item(r, 1)
            if item:
                try:
                    # Убираем пробелы и меняем запятую на точку для float
                    val = item.text().replace(' ', '').replace(',', '.')
                    total_opex += float(val)
                except ValueError:
                    continue
        return total_opex