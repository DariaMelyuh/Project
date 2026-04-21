import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QRegularExpressionValidator


class AssetSalesWidget(QFrame):
    # Сигнал для MainWindow
    data_confirmed = pyqtSignal(list)

    def __init__(self, input_widget):
        super().__init__()
        self.input_widget = input_widget
        self.cells = []
        self.stored_data = {}
        self.main_font = QFont("Times New Roman", 12)
        self.bold_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        self.validator = QRegularExpressionValidator(
            QRegularExpression(r"^\d+([.,]\d{0,2})?$")
        )

        self.setObjectName("AssetSalesContainer")
        self.setStyleSheet("""
            QFrame#AssetSalesContainer { 
                background-color: white; 
                border: 1px solid #D0E6F5; 
                border-radius: 15px; 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- ВЕРХНЯЯ ПАНЕЛЬ ---
        header_layout = QHBoxLayout()
        title = QLabel("Продажа активов")
        title.setFont(QFont("Times New Roman", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333333; border: none; background: transparent;")

        self.apply_btn = QPushButton("Принять данные")
        self.apply_btn.setFixedSize(200, 35)
        self.set_apply_btn_style("default")  # Начальный стиль
        self.apply_btn.clicked.connect(self.confirm_data)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.apply_btn)
        layout.addLayout(header_layout)

        # --- ОБЛАСТЬ ПРОКРУТКИ ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setMinimumHeight(180)
        self.scroll_area.setMaximumHeight(220)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_area.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal { border: none; background: #F0F8FF; height: 10px; }
            QScrollBar::handle:horizontal { background: #87CEFA; min-width: 20px; border-radius: 5px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self.refresh_table()

    def set_apply_btn_style(self, state):
        """Визуальные стили кнопки из вашего примера с товарами"""
        styles = {
            "default": "background-color: #E0F7FF; color: #2C3E50; border: 1px solid #87CEFA; border-radius: 8px; font-weight: bold;",
            "success": "background-color: #C8E6C9; color: #2E7D32; border: 1px solid #A5D6A7; border-radius: 8px; font-weight: bold;",
            "warning": "background-color: #FFF9C4; color: #827717; border: 1px solid #FFF176; border-radius: 8px; font-weight: bold;"
        }
        self.apply_btn.setStyleSheet(styles.get(state, styles["default"]))

    def refresh_table(self):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w: w.setParent(None)
        self.cells.clear()

        try:
            horizon_text = self.input_widget.hor_le.text()
            horizon = int(horizon_text) if horizon_text and horizon_text.isdigit() else 12
            start_month_idx = self.input_widget.month_cb.currentIndex()
            start_year = int(self.input_widget.year_cb.currentText())
            months_list = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

            # --- ПОДПИСИ СЛЕВА (СТОЛБЕЦ 0) ---

            # 1. Подпись для номеров месяцев
            label_n = QLabel("№ месяца")
            label_n.setFont(self.main_font)
            label_n.setStyleSheet("color: #7F8C8D; font-style: italic; border: none;")
            self.grid_layout.addWidget(label_n, 0, 0)

            # 2. Подпись для дат
            label_d = QLabel("Период")
            label_d.setFont(self.main_font)
            label_d.setStyleSheet("color: #7F8C8D; font-style: italic; border: none;")
            self.grid_layout.addWidget(label_d, 1, 0)

            # 3. Подпись для ввода (Стоимость) — ТЕПЕРЬ В ТАКОМ ЖЕ СТИЛЕ
            label_v = QLabel("Стоимость")
            label_v.setFont(self.main_font)
            # Установили цвет #7F8C8D и font-style: italic, убрали bold
            label_v.setStyleSheet("color: #7F8C8D; font-style: italic; border: none; background: transparent;")
            self.grid_layout.addWidget(label_v, 2, 0)

            # --- ЦИКЛ ОТРИСОВКИ ДАННЫХ ---
            for i in range(horizon):
                # Строка 0: Номера
                num_lbl = QLabel(str(i + 1))
                num_lbl.setFont(self.main_font)
                num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                num_lbl.setFixedSize(95, 25)
                num_lbl.setStyleSheet("background-color: #D0E6F5; border-radius: 4px; font-weight: bold;")
                self.grid_layout.addWidget(num_lbl, 0, i + 1)

                # Строка 1: Месяц и Год
                m_text = f"{months_list[(start_month_idx + i) % 12]}\n{start_year + (start_month_idx + i) // 12}"
                m_lbl = QLabel(m_text)
                m_lbl.setFont(self.main_font)
                m_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                m_lbl.setFixedSize(95, 45)
                m_lbl.setStyleSheet("background-color: #D0E6F5; border-radius: 8px; font-weight: bold;")
                self.grid_layout.addWidget(m_lbl, 1, i + 1)

                # Строка 2: Поля ввода (Стоимость)
                month_number = i + 1
                saved_val = self.stored_data.get(month_number, "0")

                # Логика форматирования текста (оставляем вашу текущую)
                display_text = str(saved_val).replace('.', ',')
                if saved_val != "0":
                    try:
                        f_val = float(saved_val)
                        display_text = f"{f_val:,.2f}".replace(',', ' ').replace('.', ',')
                    except:
                        pass

                le = QLineEdit(display_text)
                le.setFixedSize(95, 40)
                le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                le.setFont(self.bold_font)
                le.setValidator(self.validator)
                le.setProperty("month_num", month_number)

                le.setStyleSheet("""
                    QLineEdit {
                        background-color: #E0F7FF; 
                        border: 2px solid #87CEFA; 
                        border-radius: 8px; 
                        color: #0066CC;
                    }
                    QLineEdit:focus { border: 2px solid #0066CC; background-color: white; }
                    QLineEdit:hover { border: 2px solid #0066CC; }
                """)

                le.textChanged.connect(self.on_cell_changed)
                le.editingFinished.connect(lambda field=le: self.format_and_store(field))

                self.grid_layout.addWidget(le, 2, i + 1)
                self.cells.append(le)

            # Распорка в конце для красоты
            self.grid_layout.setColumnStretch(horizon + 1, 1)

        except Exception as e:
            print(f"Ошибка в AssetSalesWidget: {e}")
    def on_cell_changed(self):
        """Вызывается при любом вводе в ячейку"""
        self.apply_btn.setText("Принять изменения *")
        self.set_apply_btn_style("warning")

    def format_and_store(self, line_edit):
        """Форматирование текста и обязательная запись в self.stored_data"""
        raw_text = line_edit.text().strip().replace(' ', '').replace(',', '.')
        month_num = line_edit.property("month_num")

        try:
            val = float(raw_text) if raw_text else 0.0
            # Сохраняем "чистое" число в память
            self.stored_data[month_num] = val

            # Визуальное форматирование для пользователя
            formatted = f"{val:,.2f}".replace(',', ' ').replace('.', ',')
            line_edit.setText(formatted)
        except ValueError:
            self.stored_data[month_num] = 0.0
            line_edit.setText("0,00")

    def format_on_finish(self, line_edit):
        raw_text = line_edit.text().strip().replace(' ', '').replace(',', '.')
        try:
            val = float(raw_text) if raw_text else 0.0
            formatted = f"{val:,.2f}".replace(',', ' ').replace('.', ',')
            line_edit.setText(formatted)
        except ValueError:
            line_edit.setText("0,00")

    def confirm_data(self):
        """Нажатие на кнопку 'Принять'"""
        # 1. Получаем список чистых значений через ваш метод get_values (убедитесь, что он есть в классе)
        try:
            data = self.get_values()
        except:
            # Если get_values не определен, собираем вручную
            data = [float(c.text().replace(' ', '').replace(',', '.')) for c in self.cells]

        # 2. Визуальное подтверждение
        self.apply_btn.setText("Данные приняты ✓")
        self.set_apply_btn_style("success")

        # 3. ГЛАВНОЕ: Испускаем сигнал.
        # MainWindow уже подключен к этому сигналу и сам вызовет расчеты.
        self.data_confirmed.emit(data)

        # 4. Таймер для сброса текста кнопки
        QTimer.singleShot(2000, self.reset_button)

        # УДАЛИТЕ ИЛИ ЗАКОММЕНТИРУЙТЕ ЭТИ СТРОКИ:
        # if hasattr(self.input_widget.window(), 'sync_yearly_table'):
        #     self.input_widget.window().sync_yearly_table()

    def reset_button(self):
        self.apply_btn.setText("Принять данные")
        self.set_apply_btn_style("default")

    def get_data(self):
        """Теперь берет данные напрямую из словаря stored_data"""
        data = []
        # Проходим по всем сохраненным месяцам
        for m_num, val in self.stored_data.items():
            if val > 0:
                data.append({
                    'income': val,
                    'month': m_num
                })
        # Сортируем по месяцу на всякий случай
        data.sort(key=lambda x: x['month'])
        return data