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

        # Базовые данные (используются как эталон для восстановления при ошибках)
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

        # --- 1. ЗАГОЛОВОК И КНОПКИ ---
        header_layout = QHBoxLayout()
        title = QLabel("Капитальные затраты")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background: transparent; border: none;")
        header_layout.addWidget(title)

        self.add_row_btn = QPushButton("+ Добавить актив")
        self.del_row_btn = QPushButton("- Удалить актив")
        for btn in [self.add_row_btn, self.del_row_btn]:
            btn.setFixedSize(160, 30)
            btn.setStyleSheet("""
                QPushButton { 
                    background-color: #F0F8FF; border: 1px solid #B9D9EB; 
                    border-radius: 5px; font-family: 'Times New Roman'; font-size: 11pt;
                }
                QPushButton:hover { background-color: #E0F0FF; }
            """)

        header_layout.addStretch()
        header_layout.addWidget(self.add_row_btn)
        header_layout.addWidget(self.del_row_btn)
        self.layout.addLayout(header_layout)

        # --- 2. ТАБЛИЦА ---
        self.table = QTableWidget(0, 6) # Начинаем с 0, заполним в fill_default_data
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        headers = [
            "Наименование актива", "Итоговая\nстоимость, руб", "Месяц\nпокупки",
            "Срок службы\n(мес)", "Базовая\nстоимость, руб", "Параметр изм.\nцены, %"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(True) # Включаем индексы для удобства
        self.table.horizontalHeader().setFixedHeight(65)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)

        self.setFixedWidth(860)
        self.setFixedHeight(460) # Немного увеличим высоту для кнопок
        self.table.setFixedWidth(810)

        # Применяем стили таблицы (скроллбары и заголовки)
        self.apply_table_styles()

        self.fill_default_data()

        # --- 3. СИГНАЛЫ ---
        self.table.cellChanged.connect(self.validate_cell)
        self.add_row_btn.clicked.connect(self.add_new_row)
        self.del_row_btn.clicked.connect(self.delete_selected_row)

        self.table.setFixedHeight(350)
        self.layout.addWidget(self.table)
        self.layout.addSpacing(10)
        self.apply_btn = QPushButton("Принять данные")
        self.apply_btn.setFixedSize(220, 35)
        self.apply_btn.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        self.set_apply_btn_style("default")
        self.apply_btn.clicked.connect(self.accept_data)
        self.layout.addWidget(self.apply_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.accept_data()

    def apply_table_styles(self):
        self.table.setStyleSheet("""
                   QTableWidget { 
                       border: 1px solid #D0E6F5; 
                       gridline-color: #E1EFF8; font-family: 'Times New Roman'; 
                       font-size: 12pt; background-color: white;
                   }
                   QHeaderView::section { 
                       background-color: #B9D9EB; font-family: 'Times New Roman'; 
                       font-size: 11pt; font-weight: bold; border: 1px solid #D0E6F5; padding: 2px; 
                   }
                  QHeaderView::section:horizontal:first { border-top-left-radius: 15px; }
                   QHeaderView::section:horizontal:last { border-top-right-radius: 15px; }
                   QScrollBar:vertical { border: none; background: #F0F8FF; width: 12px; border-radius: 6px; }
                   QScrollBar::handle:vertical { background-color: #B9D9EB; min-height: 20px; border-radius: 6px; }
                   QScrollBar::handle:vertical:hover { background-color: #A1C9DE; }
                   QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
               """)

    def add_new_row(self):
        """Добавляет новый пустой актив"""
        row_count = self.table.rowCount()
        self.table.blockSignals(True)
        self.table.insertRow(row_count)

        # Дефолтные значения для новой строки
        # Наим(0), Итого(1), Месяц(2), Срок(3), База(4), %(5)
        new_row_data = [f"Новый актив {row_count + 1}", "0,00", "1", "1", "0,00", "0"]

        for c, val in enumerate(new_row_data):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # ВАЖНО: сохраняем начальное значение в UserRole
            item.setData(Qt.ItemDataRole.UserRole, val)

            if c == 1:
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                item.setBackground(QBrush(QColor("#F9F9F9")))
            else:
                item.setBackground(QBrush(QColor("#E0F7FF")))
            self.table.setItem(row_count, c, item)

        self.table.setRowHeight(row_count, 35)
        self.table.blockSignals(False)
        self.mark_as_changed()
        self.table.scrollToBottom()

    def delete_selected_row(self):
        """Удаляет текущую выбранную строку, но не фиксирует данные окончательно"""
        current_row = self.table.currentRow()

        if current_row == -1:
            current_row = self.table.rowCount() - 1

        if current_row >= 0:
            msg = QMessageBox(self)
            msg.setWindowTitle("Подтверждение удаления")
            msg.setFont(QFont("Times New Roman", 12))
            msg.setText(f"Вы уверены, что хотите удалить строку <b>№{current_row + 1}</b>?")
            msg.setInformativeText("Это действие нельзя будет отменить.")

            yes_button = msg.addButton("Да, удалить", QMessageBox.ButtonRole.YesRole)
            no_button = msg.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(no_button)

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
                    font-family: 'Times New Roman'; font-size: 14px; 
                    min-width: 100px; padding: 8px; 
                    background-color: #E0F7FF; border: 2px solid #87CEFA;
                    border-radius: 8px; color: #0066CC; font-weight: bold;
                }
                QPushButton:hover { background-color: #B9D9EB; border: 2px solid #0066CC; }
            """)

            msg.exec()

            if msg.clickedButton() == yes_button:
                self.table.removeRow(current_row)

                # ВАЖНО: Только переводим кнопку в режим "изменения не приняты"
                self.mark_as_changed()

    def mark_as_changed(self):
        self.apply_btn.setText("Принять изменения*")
        self.set_apply_btn_style("warning")

    def validate_cell(self, row, col):
        # Игнорируем заблокированные сигналы и колонку с названием
        if self.table.signalsBlocked() or col == 0:
            return

        item = self.table.item(row, col)
        if not item: return

        # Сохраняем "старое" значение в памяти перед обработкой (UserRole)
        # Если его там нет (новая строка), берем текущий текст
        old_val_raw = item.data(Qt.ItemDataRole.UserRole)
        if old_val_raw is None:
            old_val_raw = item.text()

        raw_text = item.text().strip()
        clean_text = raw_text.replace(' ', '').replace(',', '.')

        name_item = self.table.item(row, 0)
        asset_name = name_item.text() if name_item else f"Строка {row + 1}"

        try:
            val = float(clean_text)
            if val < 0: raise ValueError("Отрицательное значение")

            # Проверка лимитов
            if col == 2:  # Месяц
                if not val.is_integer() or not (1 <= val <= self.PROJECT_HORIZON):
                    raise ValueError(f"Месяц должен быть от 1 до {self.PROJECT_HORIZON}")

            elif col == 3:  # Срок службы
                m_item = self.table.item(row, 2)
                # Извлекаем месяц покупки для проверки горизонта
                try:
                    m_val = int(float(m_item.text().replace(' ', '').replace(',', '.')))
                except:
                    m_val = 1

                if (m_val + val - 1) > self.PROJECT_HORIZON:
                    raise ValueError(f"Срок выходит за горизонт планирования ({self.PROJECT_HORIZON} мес.)")

            elif col == 4:  # Стоимость
                if val > 1_000_000_000:
                    raise ValueError("Сумма не может превышать 1 000 000 000 руб.")

            # Если всё прошло успешно:
            self.table.blockSignals(True)
            # Сохраняем это значение как "последнее успешное"
            item.setData(Qt.ItemDataRole.UserRole, item.text())

            if col == 4:
                item.setText(self.format_as_money(val))

            self.table.blockSignals(False)
            self.mark_as_changed()

            if col in [4, 5]:
                self.recalculate_row(row)


        except ValueError as e:
            self.table.blockSignals(True)
            self.show_error(str(e), asset_name, col)
            # 1. Сначала пытаемся взять "последнее удачное" из памяти ячейки
            orig = item.data(Qt.ItemDataRole.UserRole)
            # 2. Есл памяти нет (совсем новая ячейка), берем из эталона или ставим 0
            if orig is None:
                if row < len(self.default_data_list):
                    orig = self.default_data_list[row][col]
                else:
                    # Дефолты для абсолютно новых строк без истории
                    orig = 1 if col in [2, 3] else 0

            # Устанавливаем текст обратно
            if col == 4:
                item.setText(self.format_as_money(orig))
            else:
                item.setText(self.format_val(orig))
            self.recalculate_row(row)
            self.table.blockSignals(False)
    def show_error(self, message, asset_name, col):
        """Обновленное стилизованное окно ошибки для CapEx"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(QFont("Times New Roman", 12))

        # 1. Формируем заголовок колонки для понятности
        headers = ["Наименование", "Итоговая стоимость", "Месяц покупки", "Срок службы", "Базовая стоимость", "Изменение цены"]
        col_name = headers[col] if col < len(headers) else "Параметр"

        # 2. Динамическая подсказка (уже была в вашем коде, адаптируем под стиль)
        if col == 2:
            limit_hint = f"целое число от <b>1</b> до <b>{self.PROJECT_HORIZON}</b>"
        elif col == 3:
            limit_hint = f"целое число и срок не более <b>{self.PROJECT_HORIZON}</b>)"
        elif col == 4:
            limit_hint = "число от <b>0</b> до <b>1 000 000 000</b>"
        elif col == 5:
            limit_hint = "процент от <b>0</b> до <b>100%</b>"
        else:
            limit_hint = "положительное число"

        # 3. Содержание текста
        error_text = (
            f"Параметр <b>{col_name}</b> для актива <b>{asset_name}</b> указан некорректно.<br><br>"
            f"Требование: {limit_hint}.<br><br>"
            f"Будет восстановлено исходное значение."
        )

        msg.setText(error_text)

        # 4. Стилизация в стиле проекта
        msg.setStyleSheet("""
            QMessageBox QLabel { 
                color: #333333; 
                min-width: 500px; 
            }
            QPushButton { 
                font-family: 'Times New Roman'; 
                font-size: 14px; 
                min-width: 100px; 
                padding: 6px; 
                background-color: #E0F7FF;
                border: 2px solid #87CEFA;
                border-radius: 8px;
                color: #0066CC;
            }
            QPushButton:hover { 
                background-color: #B9D9EB; 
                border: 2px solid #0066CC;
            }
        """)
        msg.exec()

    def format_val(self, val):
        """Вспомогательная функция для форматирования чисел в таблицу"""
        return str(val).replace('.', ',')

    def fill_default_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.default_data_list))
        for r, data in enumerate(self.default_data_list):
            total_val = data[4] + (data[4] * data[5] / 100)
            formatted_row = [data[0], total_val, data[2], data[3], data[4], data[5]]

            for c, val in enumerate(formatted_row):
                text = self.format_as_money(val) if c in [1, 4] else self.format_val(val)
                item = QTableWidgetItem(text)
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
        was_blocked = self.table.signalsBlocked()
        if not was_blocked: self.table.blockSignals(True)

        try:
            base_item = self.table.item(row, 4)
            param_item = self.table.item(row, 5)
            if base_item and param_item:
                # ДОБАВЬТЕ .replace(' ', '') чтобы убрать пробелы из форматирования
                base_str = base_item.text().replace(' ', '').replace(',', '.')
                param_str = param_item.text().replace(' ', '').replace(',', '.')

                base = float(base_str)
                param = float(param_str)

                total = base + (base * (param / 100))
                self.table.item(row, 1).setText(self.format_as_money(total))
        except Exception as e:
            print(f"Ошибка пересчета: {e}")  # Поможет увидеть ошибку в консоли

        if not was_blocked: self.table.blockSignals(False)



    def set_apply_btn_style(self, state):

        styles = {
            "default": "background-color: #E0F7FF; color: #2C3E50; border-radius: 8px; font-weight: bold; border: 1px solid #B0D4E3;",
            "success": "background-color: #C8E6C9; color: #2E7D32; border-radius: 8px; font-weight: bold; border: 1px solid #A5D6A7;",
            "warning": "background-color: #FFF9C4; color: #827717; border-radius: 8px; font-weight: bold; border: 1px solid #FFF176;"
        }
        self.apply_btn.setStyleSheet(styles.get(state, styles["default"]))

    def accept_data(self):
        self.current_data = [] # Здесь логика сбора данных в список
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
        capex_list = []
        for r in range(self.table.rowCount()):
            try:
                name_item = self.table.item(r, 0)
                cost_item = self.table.item(r, 1)
                month_item = self.table.item(r, 2)
                term_item = self.table.item(r, 3)

                if all([name_item, cost_item, month_item, term_item]):
                    capex_list.append({
                        'name': name_item.text(),
                        'cost': float(cost_item.text().replace(' ', '').replace(',', '.')),
                        'month': int(float(month_item.text().replace(',', '.'))),
                        'term': int(float(term_item.text().replace(',', '.')))
                    })
            except:
                continue
        return capex_list
