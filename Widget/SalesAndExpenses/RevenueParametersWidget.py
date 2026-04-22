import sys
import math
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QRegularExpressionValidator, QColor, QBrush
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
QSizePolicy
)
from PyQt6.QtGui import QFont, QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFrame, QLabel,
    QAbstractItemView, QHeaderView ,QPushButton
)


class RevenueParametersWidget(QFrame):
    products_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("RevenueParamsContainer")
        self.current_data = []

        # Обновленный список дефолтных данных (7 колонок)
        # Наим(0), Цена(1), Объем(2), Нач_цена(3), Баз_об(4), Пар_цены%(5), Пар_об%(6)
        self.default_data_list = [
            ["Продукт 1", 100, 100, 100, 100, 0, 0],
            ["Продукт 2", 150, 80, 150, 80, 0, 0],
            ["Продукт 3", 80, 110, 80, 110, 0, 0],
            ["Продукт 4", 75, 140, 75, 140, 0, 0],
            ["Продукт 5", 110, 55, 110, 55, 0, 0],
            ["Продукт 6", 114, 75, 114, 75, 0, 0],
            ["Продукт 7", 115, 70, 115, 70, 0, 0],
            ["Продукт 8", 180, 85, 180, 85, 0, 0],
            ["Продукт 9", 200, 95, 200, 95, 0, 0],
            ["Продукт 10", 71, 600, 71, 600, 0, 0],
            ["Продукт 11", 40, 50, 40, 50, 0, 0],
            ["Продукт 12", 250, 65, 250, 65, 0, 0],
            ["Продукт 13", 10, 230, 10, 230, 0, 0],
            ["Продукт 14", 78, 92, 78, 92, 0, 0],
            ["Продукт 15", 95, 96, 95, 96, 0, 0],
            ["Продукт 16", 62, 130, 62, 130, 0, 0],
            ["Продукт 17", 35, 98, 35, 98, 0, 0],
            ["Продукт 18", 77, 450, 77, 450, 0, 0],
            ["Продукт 19", 55, 78, 55, 78, 0, 0],
            ["Продукт 20", 52, 90, 52, 90, 0, 0]
        ]

        self.setStyleSheet("""
            QFrame#RevenueParamsContainer { 
                background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; 
            }
        """)

        self.layout = QVBoxLayout(self)
        title = QLabel("Товары")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background: transparent; border: none;")
        self.layout.addWidget(title)

        # Таблица: 20 строк, 7 колонок
        self.table = QTableWidget(20, 7)
        headers = [
            "Наименование", "Цена, руб", "Объем, ед/мес",
            "Начальная\nцена, руб", "Начальный\nобъем, ед/мес",
            "Параметр изм.\nцены, %", "Параметр изм.\nобъема, %"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(75)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)

        self.setFixedWidth(900) # Уменьшили ширину виджета, так как колонок меньше
        self.table.setFixedWidth(850)

        self.table.setColumnWidth(0, 200)
        for i in range(1, 7):
            self.table.setColumnWidth(i, 105)

        # Применяем стили скроллбара и таблицы
        self.apply_table_styles()

        self.fill_default_data()
        self.table.cellChanged.connect(self.validate_cell)

        self.table.setFixedHeight(35 * 7)
        self.layout.addWidget(self.table)

        self.apply_btn = QPushButton("Принять данные")
        self.apply_btn.setFixedSize(200, 35)
        self.set_apply_btn_style("default")
        self.apply_btn.clicked.connect(self.accept_data)
        self.layout.addWidget(self.apply_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.accept_data()

    def apply_table_styles(self):
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #D0E6F5; border-radius: 15px; 
                gridline-color: #E1EFF8; font-family: 'Times New Roman'; 
                font-size: 12pt; background-color: white;
            }
            QHeaderView::section { 
                background-color: #B9D9EB; font-family: 'Times New Roman'; 
                font-size: 11pt; font-weight: bold; border: 1px solid #D0E6F5; padding: 2px; 
            }
            QScrollBar:vertical { border: none; background: #F0F8FF; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background-color: #B9D9EB; min-height: 20px; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background-color: #A1C9DE; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

    def fill_default_data(self):
        self.table.blockSignals(True)
        for r in range(20):
            data = self.default_data_list[r]
            for c in range(7):
                item = QTableWidgetItem(str(data[c]).replace('.', ','))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Вычисляемые колонки (Цена и Объем) - теперь индексы 1 и 2
                if c in [1, 2]:
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    item.setBackground(QBrush(QColor("#F9F9F9")))
                else:
                    item.setBackground(QBrush(QColor("#E0F7FF")))

                self.table.setItem(r, c, item)
            self.table.setRowHeight(r, 35)
        self.table.blockSignals(False)

    def validate_cell(self, row, col):
        if self.table.signalsBlocked(): return
        if col == 0:
            self.emit_products()
            return

        item = self.table.item(row, col)
        if not item: return

        raw_text = item.text().replace(',', '.').strip()
        default_val = str(self.default_data_list[row][col]).replace('.', ',')

        headers_names = [
            "Наименование", "Цена", "Объем", "Начальная цена",
            "Начальный объем", "Параметр изм. цены", "Параметр изм. объема"
        ]
        param_name = headers_names[col]
        is_percent = col in [5, 6]

        self.apply_btn.setText("Принять изменения *")
        self.set_apply_btn_style("warning")

        try:
            if not raw_text: raise ValueError
            value = float(raw_text.replace(' руб.', ''))
            if value < 0: raise ValueError

            self.table.blockSignals(True)
            if col == 3: # Начальная цена
                formatted = f"{value:,.2f}".replace(',', ' ').replace('.', ',')
                item.setText(formatted)
            else:
                item.setText(str(value).replace('.', ','))
            self.table.blockSignals(False)

            # Пересчет
            if col in [3, 5]: self.recalculate_row_value(row, "price")
            if col in [4, 6]: self.recalculate_row_value(row, "volume")

        except ValueError:
            self.show_error_message(param_name, is_percent, default_val)
            self.table.blockSignals(True)
            item.setText(default_val)
            self.table.blockSignals(False)

    def recalculate_row_value(self, row, mode):
        self.table.blockSignals(True)
        try:
            if mode == "price":
                # Нач. цена (3), Параметр (5) -> Итоговая Цена (1)
                base = float(self.table.item(row, 3).text().replace(' ', '').replace(',', '.'))
                param = float(self.table.item(row, 5).text().replace(',', '.'))
                result = base * (1 + param / 100)
                self.table.item(row, 1).setText(f"{result:,.2f}".replace(',', ' ').replace('.', ','))
            elif mode == "volume":
                # Нач. объем (4), Параметр (6) -> Итоговый Объем (2)
                base = float(self.table.item(row, 4).text().replace(' ', '').replace(',', '.'))
                param = float(self.table.item(row, 6).text().replace(',', '.'))
                result = base * (1 + param / 100)
                self.table.item(row, 2).setText(f"{result:.2f}".replace('.', ','))
        except: pass
        self.table.blockSignals(False)

    def accept_data(self):
        new_data = []
        for r in range(self.table.rowCount()):
            row_data = []
            for c in range(7):
                item = self.table.item(r, c)
                text = item.text() if item else ""
                if c == 0:
                    row_data.append(text)
                else:
                    val = text.replace(' ', '').replace(',', '.')
                    try: row_data.append(float(val))
                    except: row_data.append(0.0)
            new_data.append(row_data)

        self.current_data = new_data
        self.apply_btn.setText("Данные приняты ✓")
        self.set_apply_btn_style("success")
        QTimer.singleShot(2000, self.reset_button)

    def get_products_full_data(self):
        """Возвращает данные для расчета. Учитываем, что индексы изменились!"""
        products = []
        source = self.current_data if self.current_data else self.get_raw_table_data()
        for row in source:
            products.append({
                'name': row[0],
                'base_price': row[1],
                'base_vol': row[2],
                # Так как темпы роста удалены из таблицы, возвращаем 0
                # (они теперь берутся из других виджетов)
                'p_growth': 0.0,
                'v_growth': 0.0
            })
        return products

    def get_raw_table_data(self):
        data = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(7):
                item = self.table.item(r, c)
                val = item.text().replace(' ', '').replace(',', '.') if item else "0"
                row.append(float(val) if c > 0 else val)
            data.append(row)
        return data

    def get_products_data(self):
        return self.get_products_full_data()

    def emit_products(self):
        names = [self.table.item(r, 0).text() if self.table.item(r, 0) else f"Продукт {r+1}" for r in range(20)]
        self.products_changed.emit(names)

    def set_apply_btn_style(self, state):
        styles = {
            "default": "background-color: #E0F7FF; color: #2C3E50; border-radius: 8px; font-weight: bold;",
            "success": "background-color: #C8E6C9; color: #2E7D32; border-radius: 8px; font-weight: bold;",
            "warning": "background-color: #FFF9C4; color: #827717; border-radius: 8px; font-weight: bold;"
        }
        self.apply_btn.setStyleSheet(styles.get(state, styles["default"]))

    def reset_button(self):
        self.apply_btn.setText("Принять данные")
        self.set_apply_btn_style("default")

    def show_error_message(self, param_name, is_percent, default_val):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setText(f"Параметр: <b>{param_name}</b><br>Введите корректное число.<br>Восстановлено: {default_val}")
        msg.setStyleSheet("QMessageBox QLabel { min-width: 400px; }")
        msg.exec()