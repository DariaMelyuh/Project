import sys
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)


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

        self.setStyleSheet("""
            QFrame#OpExContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 5)

        # --- 1. ЗАГОЛОВОК И КНОПКИ ---
        header_layout = QHBoxLayout()
        title = QLabel("Операционные затраты")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background: transparent; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.add_row_btn = QPushButton("+ Добавить строку")
        self.del_row_btn = QPushButton("- Удалить строку")
        for btn in [self.add_row_btn, self.del_row_btn]:
            btn.setFixedSize(135, 30)
            btn.setStyleSheet("""
                QPushButton { 
                    background-color: #F0F8FF; border: 1px solid #B9D9EB; 
                    border-radius: 5px; font-family: 'Times New Roman'; font-size: 12pt;
                }
                QPushButton:hover { background-color: #E0F0FF; }
            """)
        header_layout.addWidget(self.add_row_btn)
        header_layout.addWidget(self.del_row_btn)
        self.layout.addLayout(header_layout)

        # --- 2. ТАБЛИЦА ---
        self.table = QTableWidget(0, 4)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        headers = ["Наименование", "Итоговая\nстоимость, руб", "Стоимость,\nруб", "Параметр изм.\nстоимости, %"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setFixedHeight(68)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)

        self.setFixedWidth(860)
        self.table.setFixedWidth(540)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 80)

        self.apply_table_styles()
        self.fill_data()

        self.table.cellChanged.connect(self.validate_cell)
        self.add_row_btn.clicked.connect(self.add_new_row)
        self.del_row_btn.clicked.connect(self.delete_selected_row)

        self.table.setFixedHeight(315)
        self.layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignCenter)
        #self.setFixedWidth(860)
        #self.setFixedHeight(490)
        # Отступ 20 пикселей между таблицей и футером

        # --- 3. ФУТЕР ---
        footer_layout = QHBoxLayout()
        self.total_label = QLabel("ИТОГО: 0,00 руб.")
        self.total_label.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet(
            "padding: 10px; background: #FFDAB9; border-radius: 8px; color: black; border: 1px solid #D0E6F5;")

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

    def apply_table_styles(self):
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #D0E6F5; gridline-color: #E1EFF8; 
                font-family: 'Times New Roman'; font-size: 12pt; background-color: white; outline: 0;
            }
            QHeaderView::section { 
                background-color: #B9D9EB; color: black; font-family: 'Times New Roman'; 
                font-weight: bold; font-size: 11pt; border: 1px solid #D0E6F5; padding: 2px; 
            }
            QHeaderView::section:horizontal:first { border-top-left-radius: 15px; }
            QHeaderView::section:horizontal:last { border-top-right-radius: 15px; }
            QTableWidget::item:selected { background-color: #E0F0FF; color: black; }
        """)

    def show_error_msg(self, field_name, rules, default_val, unit):
        """Стилизованное окно ошибки с кнопкой как в CapEx"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(QFont("Times New Roman", 12))

        # Содержание текста
        error_text = (
            f"Параметр <b>{field_name}</b> указан некорректно.<br><br>"
            f"Допустимый диапазон: <b>{rules}</b> {unit}.<br>"
            f"Буквы, специальные символы и пустые поля не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию: <b>{default_val} {unit}</b>"
        )

        msg.setText(error_text)

        # Добавляем стандартную кнопку OK, чтобы применить к ней стили
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.button(QMessageBox.StandardButton.Ok).setText("ОК")

        # Применяем стилизацию (шрифт, границы, цвета текста как в CapEx)
        msg.setStyleSheet("""
            QMessageBox { background-color: white; }
            QMessageBox QLabel { 
                color: #333333; 
                min-width: 500px; 
                font-family: 'Times New Roman';
                font-size: 15px;
                background: transparent;
            }
            QPushButton { 
                font-family: 'Times New Roman'; 
                font-size: 14px; 
                min-width: 100px; 
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

    def fill_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.expenses_data))
        for r, data in enumerate(self.expenses_data):
            name_item = QTableWidgetItem(data[0])
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(r, 0, name_item)

            total = data[1] * (1 + data[2] / 100)
            res_item = QTableWidgetItem(self.format_as_money(total))
            res_item.setFlags(res_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            res_item.setBackground(QBrush(QColor("#F9F9F9")))
            res_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, res_item)

            base_item = QTableWidgetItem(self.format_as_money(data[1]))
            base_item.setBackground(QBrush(QColor("#E0F7FF")))
            base_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, base_item)

            perc_val = data[2]
            perc_text = str(int(perc_val)) if perc_val == int(perc_val) else str(perc_val).replace('.', ',')
            perc_item = QTableWidgetItem(perc_text)
            perc_item.setBackground(QBrush(QColor("#E0F7FF")))
            perc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, perc_item)
            self.table.setRowHeight(r, 35)
        self.table.blockSignals(False)

    def validate_cell(self, row, col):
        """Обновленная валидация с вызовом стилизованной ошибки"""
        if col == 1: return  # Итого read-only

        self.table.blockSignals(True)
        item = self.table.item(row, col)
        if not item:
            self.table.blockSignals(False)
            return

        raw_text = item.text().strip().replace(' ', '').replace(',', '.')

        try:
            if col == 0:  # Валидация названия
                if not raw_text: raise ValueError

            elif col == 2:  # Стоимость
                val = float(raw_text)
                if not (0 <= val <= 10_000_000):
                    # Берем старое значение из памяти для текста ошибки
                    old_val = self.expenses_data[row][1] if row < len(self.expenses_data) else 0.0
                    self.show_error_msg("Стоимость", "0 - 10 000 000", self.format_as_money(old_val), "руб.")
                    raise ValueError
                item.setText(self.format_as_money(val))

            elif col == 3:  # Проценты
                val = float(raw_text)
                if not (0 <= val <= 100):
                    old_val = self.expenses_data[row][2] if row < len(self.expenses_data) else 0.0
                    err_text = str(int(old_val)) if old_val == int(old_val) else str(old_val).replace('.', ',')
                    self.show_error_msg("Параметр изменения", "0 - 100", err_text, "%")
                    raise ValueError
                item.setText(str(int(val)) if val == int(val) else str(val).replace('.', ','))

            self.recalculate_row(row)
            self.set_apply_btn_style("warning")
            self.update_overall_total()

        except ValueError:
            # Логика отката к значениям из self.expenses_data
            if col == 2:
                old = self.expenses_data[row][1] if row < len(self.expenses_data) else 0.0
                item.setText(self.format_as_money(old))
            elif col == 3:
                old = self.expenses_data[row][2] if row < len(self.expenses_data) else 0.0
                item.setText(str(int(old)) if old == int(old) else str(old).replace('.', ','))
            elif col == 0:
                item.setText(f"Расход {row + 1}")

            self.recalculate_row(row)
            self.update_overall_total()

        self.table.blockSignals(False)
    def add_new_row(self):
        row_count = self.table.rowCount()
        self.table.blockSignals(True)
        self.table.insertRow(row_count)
        new_row_data = [f"Новый расход {row_count + 1}", "0,00", "0,00", "0"]
        for c, val in enumerate(new_row_data):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if c == 1:
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                item.setBackground(QBrush(QColor("#F9F9F9")))
            else:
                item.setBackground(QBrush(QColor("#E0F7FF")))
            self.table.setItem(row_count, c, item)
        self.table.setRowHeight(row_count, 35)
        self.table.blockSignals(False)
        self.set_apply_btn_style("warning")

    def delete_selected_row(self):
        current_row = self.table.currentRow()

        # Если строка не выбрана явно, берем последнюю
        if current_row == -1:
            current_row = self.table.rowCount() - 1

        if current_row >= 0:
            msg = QMessageBox(self)
            msg.setWindowTitle("Подтверждение удаления")
            msg.setFont(QFont("Times New Roman", 12))

            # Текст в стиле вашего проекта
            msg.setText(f"Вы уверены, что хотите удалить строку <b>№{current_row + 1}</b>?")
            msg.setInformativeText("Это действие нельзя будет отменить.")

            # Создаем кнопки вручную для применения стилей
            yes_button = msg.addButton("Да, удалить", QMessageBox.ButtonRole.YesRole)
            no_button = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_button)

            # Применяем CSS (полная копия стиля окна ошибки и CapEx)
            msg.setStyleSheet("""
                QMessageBox { background-color: white; }
                QMessageBox QLabel { 
                    color: #333333; 
                    min-width: 400px; 
                    font-family: 'Times New Roman';
                    font-size: 16px;
                    background: transparent;
                }
                QPushButton { 
                    font-family: 'Times New Roman'; 
                    font-size: 14px; 
                    min-width: 110px; 
                    padding: 8px; 
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

            if msg.clickedButton() == yes_button:
                self.table.removeRow(current_row)
                self.update_overall_total()
                self.set_apply_btn_style("warning")

    def recalculate_row(self, row):
        try:
            base = float(self.table.item(row, 2).text().replace(' ', '').replace(',', '.'))
            perc = float(self.table.item(row, 3).text().replace(' ', '').replace(',', '.'))
            total = base * (1 + perc / 100)
            self.table.item(row, 1).setText(self.format_as_money(total))
        except:
            pass

    def format_as_money(self, val):
        return f"{val:,.2f}".replace(',', ' ').replace('.', ',')

    def update_overall_total(self):
        total_sum = 0
        for r in range(self.table.rowCount()):
            try:
                val = float(self.table.item(r, 1).text().replace(' ', '').replace(',', '.'))
                total_sum += val
            except:
                continue
        self.total_label.setText(f"ИТОГО: {total_sum:,.2f} руб.".replace(',', ' ').replace('.', ','))

    def set_apply_btn_style(self, state):
        styles = {
            "default": "background-color: #E0F7FF; color: #2C3E50; border-radius: 8px; font-weight: bold; border: 1px solid #B0D4E3;",
            "success": "background-color: #C8E6C9; color: #2E7D32; border-radius: 8px; font-weight: bold; border: 1px solid #A5D6A7;",
            "warning": "background-color: #FFF9C4; color: #827717; border-radius: 8px; font-weight: bold; border: 1px solid #FFF176;"
        }
        self.apply_btn.setStyleSheet(styles.get(state, styles["default"]))
        self.apply_btn.setText("Принять изменения *" if state == "warning" else (
            "Данные приняты ✓" if state == "success" else "Принять данные"))

    def accept_data(self):
        new_data = []
        for r in range(self.table.rowCount()):
            try:
                name = self.table.item(r, 0).text()
                base = float(self.table.item(r, 2).text().replace(' ', '').replace(',', '.'))
                perc = float(self.table.item(r, 3).text().replace(' ', '').replace(',', '.'))
                new_data.append([name, base, perc])
            except:
                continue
        self.expenses_data = new_data
        self.set_apply_btn_style("success")
        QTimer.singleShot(2000, lambda: self.set_apply_btn_style("default"))
        self.data_confirmed.emit()

    def get_base_opex(self):
        total = 0.0
        for r in range(self.table.rowCount()):
            try:
                total += float(self.table.item(r, 1).text().replace(' ', '').replace(',', '.'))
            except:
                continue
        return total