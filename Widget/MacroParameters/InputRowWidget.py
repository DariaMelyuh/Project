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


class InputRowWidget(QWidget):
    # Создаем сигнал для передачи количества месяцев другим виджетам
    horizon_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # Предварительная настройка шрифтов
        self.label_font = QFont("Times New Roman", 12)
        self.input_font = QFont("Times New Roman", 12, QFont.Weight.Bold)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(25)

        # 1. Пружина слева (центрирует блок)
        self.main_layout.addStretch(1)

        self.field_width, self.field_height = 140, 35

        # 2. Создание элементов
        self.year_f, self.year_cb = self.create_combo([str(y) for y in range(2026, 2032)], "Год начала")

        self.month_f, self.month_cb = self.create_combo(
            ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
             "Декабрь"],
            "Месяц начала"
        )

        self.dur_f, self.dur_cb = self.create_combo([str(i) for i in range(1, 6)], "Длительность (лет)")

        self.hor_f, self.hor_le = self.create_lineedit("Горизонт расчета (мес)", editable=False, value="12")

        self.unit_f, _ = self.create_lineedit("Единица измерения", editable=False, value="руб")

        # --- НОВАЯ ЯЧЕЙКА: Желаемый срок окупаемости ---
        self.payback_f, self.payback_le = self.create_lineedit("Срок окупаемости (мес)", editable=True, value="12")
        self.payback_le.setStyleSheet("""
            QLineEdit { 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                padding: 5px; 
                background-color: #E0F7FF; 
                color: #0066CC; 
            }
            QLineEdit:focus { 
                border: 2px solid #0066CC; 
                background-color: white; 
            }
            /* Эффект при наведении курсора */
                            QLineEdit:hover {
                                border: 2px solid #0066CC; /* Чуть темнее основного голубого */
                                
                            }
        """)
        # Устанавливаем валидатор (только цифры)
        self.payback_le.setValidator(QIntValidator(0, 999))
        self.payback_le.editingFinished.connect(self._validate_payback)

        self.legend = self.create_legend()

        # 3. Подключение логики обновления
        self.dur_cb.currentTextChanged.connect(self._on_duration_changed)

        # 4. Добавляем виджеты в слой (включая payback_f перед легендой)
        widgets_to_add = [
            self.year_f, self.month_f, self.dur_f,
            self.hor_f, self.unit_f, self.payback_f, self.legend
        ]

        for w in widgets_to_add:
            self.main_layout.addWidget(w)

        # 5. Пружина справа
        self.main_layout.addStretch(1)

    def _validate_payback(self):
        """Проверка ввода: от 1 до 60, но не больше Горизонта расчета"""
        line_edit = self.payback_le
        text = line_edit.text().strip().replace(',', '.')

        # Получаем текущий горизонт расчета
        try:
            current_horizon = int(self.hor_le.text())
        except:
            current_horizon = 60

        min_val = 1
        absolute_max = 60
        # Максимально допустимое — это меньшее из (60 или Горизонт)
        allowed_max = min(absolute_max, current_horizon)
        default = str(allowed_max)

        try:
            if not text:
                raise ValueError

            value = int(float(text))

            # Проверка диапазона
            if value < min_val or value > allowed_max:
                raise ValueError

            # Если всё ок, просто форматируем текст
            line_edit.setText(str(value))

        except ValueError:
            # Создаем окно ошибки
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка ввода")
            msg.setFont(self.label_font)

            error_text = (
                f"Параметр <b>Срок окупаемости</b> указан некорректно.<br><br>"
                f"Допустимый диапазон: от <b>{min_val}</b> до <b>{allowed_max}</b> мес.<br>"
                f"(Срок не может превышать горизонт расчета проекта).<br><br>"
                f"Будет восстановлено значение: <b>{default} мес.</b>"
            )

            msg.setText(error_text)

            # ОБНОВЛЕННАЯ СТИЛИЗАЦИЯ КНОПКИ И ОКНА
            msg.setStyleSheet("""
                QMessageBox QLabel { 
                    color: #333333; 
                    min-width: 450px; 
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

            # Сбрасываем на максимально допустимое
            line_edit.setText(default)
    def _on_duration_changed(self, text):
        """Обработка изменения длительности (лет -> месяцы)"""
        try:
            years = int(text)
            months = years * 12
            self.hor_le.setText(str(months))

            # АВТО-КОРРЕКЦИЯ: если старый срок окупаемости стал больше нового горизонта
            try:
                current_payback = int(self.payback_le.text())
                if current_payback > months:
                    self.payback_le.setText(str(months))
            except ValueError:
                pass

            self.horizon_changed.emit(months)
        except ValueError:
            pass

    def create_combo(self, items, placeholder):
        f = QFrame()
        l = QVBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        f.setStyleSheet("border: none; background: transparent;")

        lbl = QLabel(placeholder)
        lbl.setFont(self.label_font)
        lbl.setStyleSheet("font-style: italic; color: #555555;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cb = QComboBox()
        cb.addItems(items)
        cb.setFont(self.input_font)
        cb.setFixedSize(self.field_width, self.field_height)

        # Устанавливаем количество видимых элементов, чтобы появился скролл
        cb.setMaxVisibleItems(6)

        cb.setStyleSheet("""
            QComboBox { 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                padding: 5px; 
                background-color: #E0F7FF; 
                color: #0066CC;
            } 
            QComboBox::drop-down { border: none; }
            QComboBox:hover {
                border: 2px solid #0066CC;
            }
            /* Контейнер выпадающего списка */
            QComboBox QAbstractItemView {
                border: 2px solid #D0E6F5;
                background-color: white;
                selection-background-color: #B9D9EB;
                outline: 0px;
                border-radius: 8px;
            }

            /* ПОЛОСА ПРОКРУТКИ (Дорожка) */
            QComboBox QAbstractItemView QScrollBar:vertical {
                background: #F0F8FF;
                width: 12px;
                /* Отступы важны, чтобы закругление было видно внутри рамки */
                margin: 4px 2px 4px 2px; 
                border-radius: 6px; /* Закругляем саму дорожку */
            }

            /* ПОЛЗУНОК (Бегунок) */
            QComboBox QAbstractItemView QScrollBar::handle:vertical {
                background-color: #B9D9EB;
                min-height: 20px;
                border-radius: 6px; /* Закругляем бегунок (половина ширины для овала) */
                border: 1px solid #A1C9DE; 
            }

            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {
                background-color: #A1C9DE;
            }

            /* Убираем лишние кнопки и фон */
            QComboBox QAbstractItemView QScrollBar::add-line:vertical, 
            QComboBox QAbstractItemView QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }

            QComboBox QAbstractItemView QScrollBar::add-page:vertical, 
            QComboBox QAbstractItemView QScrollBar::sub-page:vertical {
                background: none;
            }
            
        """)
        l.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(cb, alignment=Qt.AlignmentFlag.AlignCenter)
        return f, cb
    def create_lineedit(self, placeholder, editable=True, value=None):
        f = QFrame()
        l = QVBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        f.setStyleSheet("border: none; background: transparent;")

        lbl = QLabel(placeholder)
        lbl.setFont(self.label_font)
        lbl.setStyleSheet("font-style: italic; color: #555555;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        le = QLineEdit()
        if value: le.setText(value)
        le.setFont(self.input_font)
        le.setReadOnly(not editable)
        le.setFixedSize(self.field_width, self.field_height)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bg = '#E0F7FF' if editable else '#F9F9F9'
        color = '#0066CC' if editable else '#777777'
        le.setStyleSheet(f"""
            QLineEdit {{ 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                padding: 5px; 
                background-color: {bg}; 
                color: {color}; 
            }}
        """)

        l.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(le, alignment=Qt.AlignmentFlag.AlignCenter)
        return f, le

    def create_legend(self):
        f = QFrame()
        l = QVBoxLayout(f)
        l.setContentsMargins(15, 0, 0, 0)
        l.setSpacing(5)
        f.setStyleSheet("border: none; background: transparent;")

        t = QLabel("Справка по цветам")
        t.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        l.addWidget(t)

        for c, txt in [("#E0F7FF", "Входные данные"), ("#FFFFFF", "Расчетные ячейки"), ("#FFDAB9", "Итоговые показатели"), ("#B9D9EB", "Заголовки таблиц")]:
            row = QHBoxLayout()
            row.setSpacing(8)
            cl = QLabel()
            cl.setFixedSize(18, 18)
            cl.setStyleSheet(f"background-color: {c}; border: 1px solid #999; border-radius: 4px;")

            txt_lbl = QLabel(txt)
            txt_lbl.setFont(QFont("Times New Roman", 12))

            row.addWidget(cl)
            row.addWidget(txt_lbl)
            row.addStretch()
            l.addLayout(row)
        return f

