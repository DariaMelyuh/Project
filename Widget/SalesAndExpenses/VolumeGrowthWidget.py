import sys
from PyQt6.QtCore import Qt, QRegularExpression,pyqtSignal
from PyQt6.QtGui import QFont, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QPushButton
)


class VolumeGrowthWidget(QFrame):
    data_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        # 1. Настройка шрифтов
        self.title_font = QFont("Times New Roman", 14, QFont.Weight.Bold)
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)
        self.msg_font = QFont("Times New Roman", 12)

        self.product_labels = {}
        self.last_known_names = [f"Продукт {i}" for i in range(1, 21)]
        self.stored_data = {}
        self.years = ["2026"]
        self.inputs = {}

        # Общий валидатор (разрешает ввод цифр, точек и запятых)
        self.num_validator = QRegularExpressionValidator(QRegularExpression(r"^\d*[.,]?\d*$"))

        # Стиль контейнера
        self.setStyleSheet(
            "QFrame#GrowthContainer { background-color: white; border: 1px solid #D0E6F5; border-radius: 15px; }")
        self.setObjectName("GrowthContainer")
        self.setFixedWidth(800)
        self.setFixedHeight(400)  # Увеличили высоту под панель

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 15, 20, 20)
        self.main_layout.setSpacing(10)

        # Заголовок
        title = QLabel("Годовой темп роста объема продаж, %")
        title.setFont(self.title_font)
        title.setStyleSheet("background-color: transparent; border: none; color: #333333;")
        self.main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- НОВАЯ ПАНЕЛЬ МАССОВОГО ЗАПОЛНЕНИЯ ---
        self.setup_bulk_fill_panel()

        # Скролл
        self.setup_scroll_area()

        # Первичная инициализация
        self.update_years("2026", 0, "12")

    def setup_bulk_fill_panel(self):
        """Создает строку с вводом и кнопкой 'Применить ко всем'"""
        panel_layout = QHBoxLayout()
        panel_layout.setSpacing(10)

        lbl = QLabel("Установить для всех:")
        lbl.setFont(self.label_font)
        lbl.setStyleSheet("border: none; background: transparent;")

        self.bulk_input = QLineEdit()
        self.bulk_input.setPlaceholderText("0")

        # Ограничение от 0 до 500 для поля массового ввода
        # Регулярное выражение для диапазона от 0 до 100 (с поддержкой , и .)
        range_re = QRegularExpression(r"^(100([.,]0+)?|[0-9]?\d([.,]\d+)?)$")
        self.bulk_input.setValidator(QRegularExpressionValidator(range_re))

        self.bulk_input.setFixedSize(60, 30)
        self.bulk_input.setFont(self.input_font)
        self.bulk_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bulk_input.setStyleSheet(
            "QLineEdit { border: 1px solid #87CEFA; border-radius: 5px; background: #F2F8FC; }")

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedSize(100, 30)
        apply_btn.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        apply_btn.setStyleSheet("""
            QPushButton { background-color: #87CEFA; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #A1C9DE; }
        """)
        apply_btn.clicked.connect(self.apply_to_all_cells)

        panel_layout.addStretch()
        panel_layout.addWidget(lbl)
        panel_layout.addWidget(self.bulk_input)
        panel_layout.addWidget(apply_btn)
        panel_layout.addStretch()
        self.main_layout.addLayout(panel_layout)

    def apply_to_all_cells(self):
        """Метод для массового заполнения всех ячеек"""
        val_text = self.bulk_input.text().replace(',', '.')
        if not val_text: val_text = "0"

        # Превращаем в строку для вставки
        final_text = val_text.replace('.', ',')

        for key, le in self.inputs.items():
            le.setText(final_text)
            self.validate_input(le)

    def setup_scroll_area(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border: none; background: #F0F8FF; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #B9D9EB; min-height: 30px; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background: #A1C9DE; }
        """)
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: white;")
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(10, 10, 20, 10)
        self.grid.setColumnMinimumWidth(0, 150)
        scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(scroll)

    def update_product_names(self, names_list):
        """
        Обновляет список продуктов. Если добавлены новые продукты,
        они отрисовываются в таблице со значениями 0.
        """
        print(f"Обновление списка: {len(names_list)} товаров")  # Для отладки

        # Сохраняем новый список имен
        self.last_known_names = names_list

        # Очищаем сетку (кроме заголовков лет, которые в 0-й строке)
        # Удаляем все виджеты со строки 1 и ниже
        for i in reversed(range(self.grid.count())):
            pos = self.grid.getItemPosition(i)
            row = pos[0]
            if row > 0:  # Строка 0 — это заголовки лет, их не трогаем
                item = self.grid.takeAt(i)
                if item.widget():
                    item.widget().deleteLater()

        # Сбрасываем словари ссылок на виджеты (но stored_data сохраняется)
        self.product_labels = {}
        self.inputs = {}

        # Заново отрисовываем строки для каждого продукта
        for row_idx, prod_name in enumerate(self.last_known_names, 1):
            # Создаем метку продукта
            p_lbl = QLabel(prod_name)
            p_lbl.setFont(self.label_font)
            p_lbl.setStyleSheet("font-style: italic; color: #555555; border: none;")
            self.grid.addWidget(p_lbl, row_idx, 0)
            self.product_labels[row_idx] = p_lbl

            # Создаем поля ввода для каждого года
            for col_idx, year in enumerate(self.years):
                # _create_edit автоматически подтянет значение из stored_data,
                # если оно там есть, иначе поставит "0"
                le = self._create_edit("0", f"{prod_name} ({year})", row_idx, str(year))
                self.grid.addWidget(le, row_idx, col_idx + 1)
                self.inputs[f"growth_{row_idx}_{year}"] = le

    def _create_edit(self, default_val, name, product_row, year):
        current_val = self.stored_data.get((product_row, year), default_val)
        le = QLineEdit(str(current_val).replace('.', ','))
        le.setValidator(self.num_validator)
        le.setFont(self.input_font)
        le.setFixedSize(73, 35)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setStyleSheet("""
            QLineEdit { border: 2px solid #87CEFA; border-radius: 8px; background-color: #E0F7FF; color: #0066CC; }
            QLineEdit:focus { border: 2px solid #0066CC; background-color: white; }
            QLineEdit:hover { border: 2px solid #0066CC; }
        """)
        le.setProperty("default", default_val)
        le.setProperty("name", name)
        le.setProperty("product_row", product_row)
        le.setProperty("year", year)
        le.editingFinished.connect(lambda field=le: self.validate_input(field))
        return le

    def validate_input(self, le):
        text_raw = le.text().strip()

        # Убираем лишние разделители в конце
        if text_raw.endswith(',') or text_raw.endswith('.'):
            text_raw = text_raw[:-1]

        text = text_raw.replace(',', '.')
        product_row = le.property("product_row")
        year = le.property("year")
        name = le.property("name")
        default = le.property("default")

        max_val = 100.0
        min_val = 0.0

        try:
            if not text: raise ValueError
            val = float(text)

            if not (min_val <= val <= max_val):
                raise ValueError

            # Форматирование: убираем .0 если число целое
            clean_val = str(int(val)) if val == int(val) else f"{val:.2f}".replace('.', ',').rstrip('0').rstrip(',')

            self.stored_data[(product_row, year)] = clean_val
            le.setText(clean_val.replace('.', ','))
            self.data_changed.emit()

        except ValueError:
            # Вызов обновленного окна ошибки с передачей параметров
            self.show_error(name, year, default, max_val)

            # Восстановление значения
            le.setText(default.replace('.', ','))
            self.stored_data[(product_row, year)] = default
            self.data_changed.emit()

    def show_error(self, name, year, default, max_val):
        """Обновленное окно ошибки в стиле проекта"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка ввода")
        msg.setFont(self.label_font)

        # Формируем текст по шаблону: Название параметра + Год + Диапазон
        error_text = (
            f"Параметр <b>Темп роста объема</b> для <b>{name}</b> указан некорректно.<br><br>"
            f"Допустимый диапазон: от <b>0</b> до <b>{int(max_val)}%</b>.<br>"
            f"Буквы и символы не допускаются.<br><br>"
            f"Будет восстановлено значение по умолчанию: <b>{default}</b>"
        )

        msg.setText(error_text)

        # Стилизация кнопок и меток (копия из вашего примера)
        msg.setStyleSheet("""
            QMessageBox QLabel { 
                color: #333333; 
                min-width: 520px; 
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

    def update_years(self, start_year, start_month_idx, total_horizon_months):
        try:
            y, m = int(start_year), int(start_month_idx) + 1
            total_m = int(total_horizon_months)
            unique_years = []
            curr_y, curr_m = y, m
            for _ in range(total_m):
                if str(curr_y) not in unique_years: unique_years.append(str(curr_y))
                curr_m += 1
                if curr_m > 12: curr_m = 1; curr_y += 1
            self.years = unique_years

            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w: w.setParent(None)

            self.product_labels, self.inputs = {}, {}
            for col, year in enumerate(self.years):
                lbl = QLabel(str(year));
                lbl.setFont(self.label_font);
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("font-weight: bold; background: #D0E6F5; border-radius: 5px; padding: 5px;")
                self.grid.addWidget(lbl, 0, col + 1)

            for row in range(1, len(self.last_known_names) + 1):
                prod_name = self.last_known_names[row - 1]
                p_lbl = QLabel(prod_name);
                p_lbl.setFont(self.label_font)
                p_lbl.setStyleSheet("font-style: italic; color: #555555; border: none;")
                self.grid.addWidget(p_lbl, row, 0)
                self.product_labels[row] = p_lbl
                for col, year in enumerate(self.years):
                    le = self._create_edit("0", f"{prod_name} ({year})", row, str(year))
                    self.grid.addWidget(le, row, col + 1)
                    self.inputs[f"growth_{row}_{year}"] = le
            self.grid.setColumnStretch(len(self.years) + 1, 10)
        except Exception as e:
            print(f"Ошибка VolumeGrowthWidget: {e}")

    def get_data(self):
        result = {}
        for year in self.years:
            year_vals = []
            for row in range(1, len(self.last_known_names) + 1):
                key = f"growth_{row}_{year}"
                val = float(self.inputs[key].text().replace(',', '.')) if key in self.inputs else 0.0
                year_vals.append(val)
            result[str(year)] = year_vals
        return result