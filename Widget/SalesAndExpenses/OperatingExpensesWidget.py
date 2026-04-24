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
        self.table.setFrameShape(QFrame.Shape.NoFrame)
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
        # --- ИСПРАВЛЕННЫЕ РАЗМЕРЫ (БЕЗ СКРОЛЛА) ---
        # Уменьшаем общую карточку (контейнер), чтобы она плотно облегала таблицу
        self.setFixedWidth(600)

        # Сумма колонок: 180 + 130 + 130 + 80 = 520
        # Добавляем 2 пикселя на внешние границы таблицы = 522
        self.table.setFixedWidth(540)

        self.table.setColumnWidth(0, 180)  # Наименование
        self.table.setColumnWidth(1, 130)  # Итоговая стоимость
        self.table.setColumnWidth(2, 130)  # Стоимость, руб
        self.table.setColumnWidth(3, 80)  # %

        # Стилизация таблицы как в первом примере
        # Стилизация таблицы с закруглением углов
        # Замените старый стиль таблицы на этот:
        # Стилизация таблицы: полная синхронизация с левым виджетом
        self.table.setStyleSheet("""
                    QTableWidget { 
                        border: 1px solid #D0E6F5; 
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
                        /* Важно: border должен быть таким же, как слева */
                        border: 1px solid #D0E6F5; 
                        padding: 2px; 
                    }

                    /* Закругления первой и последней ячейки шапки */
                    QHeaderView::section:horizontal:first { 
                        border-top-left-radius: 15px; 
                    }
                    QHeaderView::section:horizontal:last { 
                        border-top-right-radius: 15px; 
                    }

                  QTableWidget::item:selected {
        background-color: transparent;
        color: black;
    }
                """)
        self.fill_data()
        self.table.cellChanged.connect(self.validate_cell)
        self.table.setFixedHeight(313)

        # Находим строку, где добавляется таблица, и меняем на:
        self.layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self.apply_btn.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        self.set_apply_btn_style("default")
        self.apply_btn.clicked.connect(self.accept_data)
        footer_layout.addWidget(self.apply_btn)

        self.layout.addLayout(footer_layout)
        self.update_overall_total()

    def fill_data(self):
        self.table.blockSignals(True)
        for r, data in enumerate(self.expenses_data):
            # 0. Наименование
            name_item = QTableWidgetItem(data[0])
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(r, 0, name_item)

            # 1. Итоговая сумма (Всегда с копейками, так как это деньги)
            total = data[1] + (data[1] * data[2] / 100)
            res_item = QTableWidgetItem(self.format_as_money(total))
            res_item.setFlags(res_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            res_item.setBackground(QBrush(QColor("#F9F9F9")))
            res_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, res_item)

            # 2. База (Деньги - всегда с копейками)
            base_item = QTableWidgetItem(self.format_as_money(data[1]))
            base_item.setBackground(QBrush(QColor("#E0F7FF")))
            base_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, base_item)

            # 3. % (ИСПРАВЛЕНО: убираем ,0 если число целое)
            perc_val = data[2]
            # Если число равно своему целому значению, пишем как int
            perc_text = str(int(perc_val)) if perc_val == int(perc_val) else str(perc_val).replace('.', ',')
            perc_item = QTableWidgetItem(perc_text)
            perc_item.setBackground(QBrush(QColor("#E0F7FF")))
            perc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, perc_item)

            self.table.setRowHeight(r, 35)
        self.table.blockSignals(False)
    def format_as_money(self, val):
        return f"{val:,.2f}".replace(',', ' ').replace('.', ',')

    def show_error_msg(self, field_name, rules, default_val, unit):
        """Обновленное стилизованное окно ошибки в стиле проекта"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(QFont("Times New Roman", 12))

        # Содержание текста с выделением параметров
        error_text = (
            f"Параметр <b>{field_name}</b> указан некорректно.<br><br>"
            f"Допустимый диапазон: <b>{rules}</b> {unit}.<br>"
            f"Буквы, специальные символы и пустые поля не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию: <b>{default_val} {unit}</b>"
        )

        msg.setText(error_text)

        # Применяем фирменную стилизацию кнопок и меток
        msg.setStyleSheet("""
            QMessageBox QLabel { 
                color: #333333; 
                min-width: 500px; 
                font-family: 'Times New Roman';
                font-size: 15px;
            }
            QPushButton { 
                font-family: 'Times New Roman'; 
                font-size: 14px; 
                min-width: 110px; 
                padding: 7px; 
                background-color: #E0F7FF;
                border: 2px solid #87CEFA;
                border-radius: 8px;
                color: #0066CC;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #B9D9EB; 
                border: 2px solid #0066CC;
            }
        """)
        msg.exec()
    # --- ОБНОВЛЕННЫЙ МЕТОД ВАЛИДАЦИИ ---
    def validate_cell(self, row, col):
        if col == 0 or col == 1: return

        self.table.blockSignals(True)
        item = self.table.item(row, col)
        raw_text = item.text().strip().replace(' ', '').replace(',', '.')

        if raw_text.endswith('.'): raw_text = raw_text[:-1]

        try:
            if not raw_text: raise ValueError
            val = float(raw_text)

            if col == 2:  # Стоимость
                if not (0 <= val <= 3000000):
                    self.show_error_msg("Стоимость", "0 - 3 000 000", self.format_as_money(self.expenses_data[row][1]),
                                        "руб.")
                    raise ValueError
                item.setText(self.format_as_money(val))

            elif col == 3:  # Проценты (ИСПРАВЛЕНО)
                if not (0 <= val <= 100):
                    default_perc = self.expenses_data[row][2]
                    # Красивый вывод дефолтного значения в ошибке
                    err_val = str(int(default_perc)) if default_perc == int(default_perc) else str(
                        default_perc).replace('.', ',')
                    self.show_error_msg("Параметр изменения", "0 - 100", err_val, "%")
                    raise ValueError

                # ИСПРАВЛЕНО: сохраняем ввод как целое, если нет дробной части
                if val == int(val):
                    item.setText(str(int(val)))
                else:
                    item.setText(str(val).replace('.', ','))

            self.recalculate_row(row)
            self.set_apply_btn_style("warning")
            self.update_overall_total()

        except ValueError:
            # Откат (ИСПРАВЛЕНО)
            if col == 2:
                item.setText(self.format_as_money(self.expenses_data[row][1]))
            else:
                default_val = self.expenses_data[row][2]
                text = str(int(default_val)) if default_val == int(default_val) else str(default_val).replace('.', ',')
                item.setText(text)

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