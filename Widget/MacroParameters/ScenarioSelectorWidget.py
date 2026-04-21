
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

class ScenarioSelectorWidget(QFrame):
    def __init__(self, title_text="Сценарий"):
        super().__init__()
        self.setObjectName("SelectorContainer")

        # Габариты: чуть увеличим для солидности
        self.setFixedWidth(300)
        self.setFixedHeight(95)

        # Стилизация контейнера: добавим легкую тень и акцентную линию сверху
        self.setStyleSheet("""
            QFrame#SelectorContainer { 
                background-color: white; 
                border: 2px solid #E1EFF8; 
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(8)

        # Заголовок
        self.title_label = QLabel(title_text)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(5)
        # Заголовок
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #2C3E50; border: none; background: transparent;")
        layout.addWidget(self.title_label)

        # Выпадающий список
        self.combo = QComboBox()
        self.combo.addItems(["Базовый", "Оптимистичный", "Пессимистичный"])
        # Оставляем высоту 35 или можно чуть уменьшить до 32
        self.combo.setFixedHeight(32)

        # Улучшенный стиль выпадающего списка
        self.combo.setStyleSheet("""
           QComboBox { 
                border: 2px solid #87CEFA; 
                border-radius: 8px; 
                font-family: 'Times New Roman'; 
                font-size: 12pt; 
                padding-left: 10px;
                background: #F0F8FF;
                color: #0066CC;
            }
            QComboBox:hover {
                background: #E0F7FF;
                border: 2px solid #0066CC;
            }
            QComboBox::drop-down { 
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #87CEFA;
            }
            QComboBox::down-arrow {
                image: none; /* Можно заменить на иконку стрелочки */
                border: 4px solid transparent;
                border-top: 7px solid #0066CC;
                margin-top: 5px;
            }
            QAbstractItemView {
                border: 1px solid #87CEFA;
                selection-background-color: #87CEFA;
                selection-color: white;
                background-color: white;
                outline: 0;
            }
        """)
        layout.addWidget(self.combo)