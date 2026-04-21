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

        # Обновленный список дефолтных значений (9 колонок)
        # Наим(0), Цена(1), Рост%(2), Объем(3), Рост_об%(4), Нач_цена(5), Баз_об(6), Пар_цены%(7), Пар_об%(8)
        self.default_data_list = [
            ["Продукт 1", 100, 3, 100, 2, 100, 100, 0, 0],
            ["Продукт 2", 150, 3, 80, 2, 150, 80, 0, 0],
            ["Продукт 3", 80, 3, 110, 2, 80, 110, 0, 0],
            ["Продукт 4", 75, 3, 140, 2, 75, 140, 0, 0],
            ["Продукт 5", 110, 3, 55, 2, 110, 55, 0, 0],
            ["Продукт 6", 114, 3, 75, 2, 114, 75, 0, 0],
            ["Продукт 7", 115, 3, 70, 2, 115, 70, 0, 0],
            ["Продукт 8", 180, 3, 85, 2, 180, 85, 0, 0],
            ["Продукт 9", 200, 3, 95, 2, 200, 95, 0, 0],
            ["Продукт 10", 71, 3, 600, 2, 71, 600, 0, 0],
            ["Продукт 11", 40, 3, 50, 2, 40, 50, 0, 0],
            ["Продукт 12", 250, 3, 65, 2, 250, 65, 0, 0],
            ["Продукт 13", 10, 3, 230, 2, 10, 230, 0, 0],
            ["Продукт 14", 78, 3, 92, 2, 78, 92, 0, 0],
            ["Продукт 15", 95, 3, 96, 2, 95, 96, 0, 0],
            ["Продукт 16", 62, 3, 130, 2, 62, 130, 0, 0],
            ["Продукт 17", 35, 3, 98, 2, 35, 98, 0, 0],
            ["Продукт 18", 77, 3, 450, 2, 77, 450, 0, 0],
            ["Продукт 19", 55, 3, 78, 2, 55, 78, 0, 0],
            ["Продукт 20", 52, 3, 90, 2, 52, 90, 0, 0]
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

        # 5. Создание и стилизация таблицы
        self.table = QTableWidget(20, 9)
        headers = [
            "Наименование", "Цена, руб", "Годовой темп\nроста цены, %",
            "Объем, ед/мес", "Годовой темп\nроста объема, %",
            "Начальная\nцена, руб", "Начальный\nобъем, ед/мес",
            "Параметр изм.\nцены, %", "Параметр изм.\nобъема, %"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)  # Скрываем номера строк

        # Настройка высоты шапки
        self.table.horizontalHeader().setFixedHeight(75)

        # ПРАВИЛЬНЫЙ ПЕРЕНОС ТЕКСТА
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)

        # Настройка ширины
        self.setFixedWidth(1100)
        self.table.setFixedWidth(1050)

        self.table.setColumnWidth(0, 250)
        for i in range(1, 9):
            self.table.setColumnWidth(i, 98)

            # Стилизация таблицы с закругленными углами
            self.table.setStyleSheet("""
                    QTableWidget { 
                        border: 1px solid #D0E6F5; 
                        border-radius: 15px;      /* Закругление рамки таблицы */
                        gridline-color: #E1EFF8; 
                        font-family: 'Times New Roman'; 
                        font-size: 12pt;
                        background-color: white;
                    }

                    /* Закругляем верхний левый угол шапки */
                    QHeaderView::section:horizontal:first {
                        border-top-left-radius: 15px;
                    }

                    /* Закругляем верхний правый угол шапки */
                    QHeaderView::section:horizontal:last {
                        border-top-right-radius: 15px;
                    }

                    QHeaderView::section { 
                        background-color: #B9D9EB; 
                        font-family: 'Times New Roman'; 
                        font-size: 12pt; 
                        font-weight: bold; 
                        border: 1px solid #D0E6F5; 
                        padding: 2px; 
                    }
                    /* Общий вид полосы прокрутки (вертикальной) */
            QScrollBar:vertical {
                border: none;
                background: #F0F8FF; /* Очень светло-голубой фон дорожки */
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            /* Сама "ручка" (ползунок) */
            QScrollBar::handle:vertical {
                background-color: #B9D9EB; /* Ваш нежно-голубой цвет */
                min-height: 20px;
                border-radius: 6px; /* Закругление */
            }

            /* Цвет при наведении на ползунок */
            QScrollBar::handle:vertical:hover {
                background-color: #A1C9DE;
            }

            /* Убираем стрелочки сверху и снизу */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            
            /* Аналогично для горизонтального скролла, если он появится */
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
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
                """)

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


    def fill_default_data(self):
        self.table.blockSignals(True)
        table_font = QFont("Times New Roman", 12)
        for r in range(20):
            data = self.default_data_list[r]
            for c in range(9):
                item = QTableWidgetItem(str(data[c]).replace('.', ','))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Блокируем ввод для 1 (Цена) и 3 (Объем) колонок
                if c in [1, 3]:
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    item.setBackground(QBrush(QColor("#F9F9F9")))  # Серый фон для вычисляемых
                elif c == 0:
                    # Наименование (обычно белый фон, либо оставьте как есть)
                    item.setBackground(QBrush(QColor("#E0F7FF")))
                else:
                    # Все остальные ячейки (вводимые) — устанавливаем ваш цвет
                    item.setBackground(QBrush(QColor("#E0F7FF")))

                self.table.setItem(r, c, item)
            self.table.setRowHeight(r, 35)
        self.table.blockSignals(False)

    def validate_cell(self, row, col):
        if self.table.signalsBlocked():
            return

        # Если это колонка с названием — отправляем сигнал и выходим
        if col == 0:
            self.emit_products()
            return

        item = self.table.item(row, col)
        if not item: return

        # Очищаем текст от пробелов и заменяем запятую на точку для расчетов
        raw_text = item.text().replace(',', '.').strip()

        # Значение по умолчанию для отката
        default_val = str(self.default_data_list[row][col]).replace('.', ',')

        headers_names = [
            "Наименование", "Цена", "Годовой темп роста цены",
            "Объем", "Годовой темп роста объема", "Начальная цена",
            "Начальный объем", "Параметр изм. цены", "Параметр изм. объема"
        ]
        param_name = headers_names[col]

        # --- НАСТРОЙКА ЛИМИТОВ ---
        is_percent = col in [2, 4, 7, 8]
        is_initial_price = (col == 5)
        is_initial_volume = (col == 6)

        # max_val = 1000000.0  # Общий лимит по умолчанию
        # if is_percent: max_val = 100.0
        # if is_initial_price or is_initial_volume: max_val = 10000.0

        self.apply_btn.setText("Принять изменения *")
        self.set_apply_btn_style("warning")

        try:
            if not raw_text: raise ValueError("Пусто")

            # Убираем " руб." если пользователь случайно его не удалил при редактировании
            clean_text = raw_text.replace(' руб.', '').strip()
            value = float(clean_text)

            # Проверка диапазона
            if value < 0:
                raise ValueError("Отрицательное значение")

            # --- ФОРМАТИРОВАНИЕ ДЕНЕГ ---
            self.table.blockSignals(True)
            if is_initial_price:
                # Устанавливаем красивый денежный формат: "1 234,50 руб."
                formatted_price = f"{value:,.2f}".replace(',', ' ').replace('.', ',')
                item.setText(formatted_price)
            else:
                # Для остальных колонок просто нормализуем число (запятая вместо точки)
                item.setText(str(value).replace('.', ','))
            self.table.blockSignals(False)

            # Пересчет зависимых колонок (1 и 3)
            if col in [5, 7]: self.recalculate_row_value(row, "price")
            if col in [6, 8]: self.recalculate_row_value(row, "volume")

        except ValueError:
            self.show_error_message(param_name, is_percent, default_val)
            self.table.blockSignals(True)
            item.setText(default_val)
            self.table.blockSignals(False)

    def show_error_message(self, param_name, is_percent, default_val):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(QFont("Times New Roman", 12))

        #limit_hint = f"от <b>0</b> до <b>{int(max_val)}%</b>" if is_percent else f"от <b>0</b> до <b>{int(max_val)}</b>"

        error_text = (
            f"Параметр: <b>{param_name}</b><br><br>"
            f"Введите корректное значение.<br>"
            f"Символы, буквы и отрицательные значения не допускаются.<br><br>"
            f"Будет восстановлено: <b>{default_val}</b>"
        )

        msg.setText(error_text)
        # Стилизация окна

        msg.setStyleSheet("""
        QMessageBox QLabel {
        color: #333333;
        min-width: 480px;
        }

        QPushButton {
        font-family: 'Times New Roman';
        font-size: 14px;
        min-width: 90px;
        padding: 5px;
        background-color: #E0F7FF;
        border: 1px solid #87CEFA;
        border-radius: 5px;
        }
        QPushButton:hover { background-color: #B9D9EB; }
        """)
        msg.exec()


    def emit_products(self):
        """Собирает все имена из первой колонки и отправляет их"""
        names = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item:
                text = item.text().strip()
                # Если ячейка пустая, пишем "Продукт №"
                names.append(text if text else f"Продукт {r + 1}")
            else:
                names.append(f"Продукт {r + 1}")

        # Отправляем список имен через сигнал
        self.products_changed.emit(names)

    def recalculate_row_value(self, row, mode):
        self.table.blockSignals(True)
        try:
            if mode == "price":
                # Очищаем строку от всего лишнего, оставляя только цифры и запятую/точку
                item_text = self.table.item(row, 5).text()
                clean_val = "".join(c for c in item_text if c.isdigit() or c in ".,-")
                base = float(clean_val.replace(',', '.'))

                param_text = self.table.item(row, 7).text().replace(',', '.')
                param = float(param_text)

                result = base * (1 + param / 100)
                formatted_res = f"{result:,.2f}".replace(',', ' ').replace('.', ',')
                self.table.item(row, 1).setText(formatted_res)

            elif mode == "volume":
                # Аналогичная чистка для объема
                item_text = self.table.item(row, 6).text()
                clean_val = "".join(c for c in item_text if c.isdigit() or c in ".,-")
                base = float(clean_val.replace(',', '.'))

                param = float(self.table.item(row, 8).text().replace(',', '.'))
                result = base * (1 + param / 100)
                self.table.item(row, 3).setText(f"{result:.2f}".replace('.', ','))
        except Exception as e:
            print(f"Ошибка пересчета в строке {row}: {e}")
        self.table.blockSignals(False)

    def accept_data(self):
        new_data = []
        for r in range(self.table.rowCount()):
            row_data = []
            for c in range(9):
                item = self.table.item(r, c)
                text = item.text() if item else ""
                if c == 0:
                    row_data.append(text)
                else:
                    # Очищаем от пробелов и заменяем запятую для корректного float
                    clean_text = text.replace(' ', '').replace(',', '.')
                    try:
                        row_data.append(float(clean_text))
                    except:
                        row_data.append(0.0)
            new_data.append(row_data)

        self.current_data = new_data
        self.apply_btn.setText("Данные приняты ✓")
        self.set_apply_btn_style("success")
        QTimer.singleShot(2000, self.reset_button)

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

    def get_total_base_revenue(self):
        total = 0
        data_to_use = self.current_data if self.current_data else self.default_data_list
        for row in data_to_use:
            total += (row[1] * row[3])  # Используем вычисленные Цену и Объем
        return total

    def get_growth_rates(self):
        p_growth, v_growth, count = 0, 0, 0
        data_to_use = self.current_data if self.current_data else self.default_data_list
        for row in data_to_use:
            p_growth += row[2]
            v_growth += row[4]
            count += 1
        return (p_growth / count, v_growth / count) if count > 0 else (0, 0)

    # Добавь это внутрь класса RevenueParametersWidget
    def get_products_full_data(self):
        """Возвращает актуальные данные для расчета выручки"""
        products = []
        # Если кнопка "Принять" еще не нажималась, берем дефолтные значения
        source = self.current_data if self.current_data else []

        if not source:
            # Если current_data пуст, парсим таблицу напрямую
            for r in range(self.table.rowCount()):
                row = []
                for c in range(9):
                    item = self.table.item(r, c)
                    val = item.text().replace(' ', '').replace(',', '.') if item else "0"
                    try:
                        row.append(float(val) if c > 0 else val)
                    except:
                        row.append(0.0)
                source.append(row)

        for row in source:
            products.append({
                'name': row[0],
                'base_price': row[1],  # Колонка "Цена"
                'p_growth': row[2],  # % роста цены
                'base_vol': row[3],  # Колонка "Объем"
                'v_growth': row[4]  # % роста объема
            })
        return products


# Добавьте это в конец класса RevenueParametersWidget
    def get_products_data(self):
        """Псевдоним для совместимости с методом sync_yearly_table"""
        return self.get_products_full_data()