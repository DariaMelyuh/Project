from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QScrollArea, QFrame, QWidget, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка — Финансовая модель инвестиционного проекта")
        self.setMinimumSize(1000, 750)
        self.setStyleSheet("background-color: #FFFFFF;")

        # Главный вертикальный слой окна
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 20)
        main_layout.setSpacing(15)

        # ══ ШАПКА ОKНА ══
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #DDEAF6;
                border: 1px solid #C0D5EC;
                border-radius: 12px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 18, 20, 18)
        header_layout.setSpacing(4)

        title_label = QLabel("Финансовая модель инвестиционного проекта")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 20px; font-weight: bold; color: #2463A4; border: none; background: transparent;")

        subtitle_label = QLabel("Руководство пользователя")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(
            "font-family: 'Segoe UI', Arial; font-size: 13px; color: #6A90B4; border: none; background: transparent;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)

        # ══ ОБЛАСТЬ ПРОКРУТКИ ДЛЯ КОНТЕНТА ══
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
            QScrollBar:vertical {
                background: #E4ECF4;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #B0C8DE;
                border-radius: 5px;
                min-height: 28px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7AAAC8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #FFFFFF;")
        content_layout = QVBoxLayout(scroll_widget)
        content_layout.setContentsMargins(0, 10, 10, 10)
        content_layout.setSpacing(25)

        base_text_style = "font-family: 'Segoe UI', Arial; font-size: 14px; color: #3A4A5C;"

        # ── СЕКЦИЯ 1: О ПРОГРАММЕ ──
        sec1_card, sec1_layout = self._create_section_card("О программе")

        desc1 = QLabel(
            "<span style='color: #2463A4; font-weight: bold; font-size: 15px;'>Что это?</span><br>"
            "Инструмент для комплексной оценки экономической целесообразности инвестиционного проекта. "
            "Модель рассчитывает ключевые финансовые показатели — NPV, ARR, IRR, PI, PP и DPP — "
            "и позволяет сравнивать результаты при различных сценариях развития событий."
        )

        desc2 = QLabel(
            "<span style='color: #2463A4; font-weight: bold; font-size: 15px;'>Для кого?</span><br>"
            "Для предпринимателей, аналитиков и всех, кто хочет обоснованно оценить инвестиционный проект "
            "без глубоких навыков финансового моделирования. Все расчёты выполняются автоматически — от вас "
            "требуется только ввести исходные данные."
        )

        desc3 = QLabel(
            "<span style='color: #27855A; font-weight: bold; font-size: 15px;'>✓ Установлены значения по умолчанию для примера, которые можно изменить.</span><br>"
            "При первом открытии все вкладки уже содержат предустановленные параметры типового проекта в сфере "
            "малого бизнеса. Используйте их как отправную точку, постепенно заменяя на собственные данные, "
            "либо сразу перейдите на вкладку результатов, чтобы увидеть логику работы модели."
        )

        for d in [desc1, desc2, desc3]:
            d.setWordWrap(True)
            d.setStyleSheet("font-family: 'Segoe UI', Arial; font-size: 14px; color: #3A4A5C; margin-bottom: 8px;")
            sec1_layout.addWidget(d)

        content_layout.addWidget(sec1_card)

        # ── СЕКЦИЯ 2: ЦВЕТОВАЯ ИНДИКАЦИЯ ──
        sec2_card, sec2_layout = self._create_section_card("Цветовая индикация полей")

        sec2_title = QLabel(
            "Все поля модели разделены по цвету — вы всегда будете знать, что можно изменять, а что рассчитывается автоматически:")
        sec2_title.setStyleSheet(base_text_style)
        sec2_title.setWordWrap(True)
        sec2_layout.addWidget(sec2_title)

        colors_data = [
            ("#AED6F1", "rgba(0,0,0,0.12)",
             "Нежно-голубой — поля для ручного ввода. Здесь задаются исходные параметры проекта."),
            ("#F0F0F0", "#BBBBBB",
             "Белый — расчётные поля. Значения формируются автоматически. Не редактируйте их вручную."),
            ("#FAC898", "rgba(0,0,0,0.12)", "Персиковый — итоговые расчеты.")
        ]

        for bg_color, border_color, text in colors_data:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(10)

            dot = QFrame()
            dot.setFixedSize(16, 16)
            dot.setStyleSheet(f"background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px;")

            lbl = QLabel(text)
            lbl.setStyleSheet(base_text_style)
            lbl.setWordWrap(True)

            row_layout.addWidget(dot)
            row_layout.addWidget(lbl, 1)
            sec2_layout.addWidget(row_widget)

        content_layout.addWidget(sec2_card)

        # ── СЕКЦИЯ 3: КЛЮЧЕВЫЕ КОЭФФИЦИЕНТЫ МОДЕЛИ ──
        coef_card, coef_layout = self._create_section_card("Базовые экономические параметры модели")

        coef_split_layout = QHBoxLayout()
        coef_split_layout.setSpacing(15)

        # Левый прямоугольник — Коэффициент сезонности
        season_frame = QFrame()
        season_frame.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #2463A4; border-radius: 6px;"
        )
        season_box = QVBoxLayout(season_frame)
        season_box.setContentsMargins(15, 12, 15, 12)
        season_box.setSpacing(4)

        lbl_season_title = QLabel("Коэффициент сезонности (k)")
        lbl_season_title.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; font-weight: bold; color: #2463A4; border: none;")

        lbl_season_desc = QLabel(
            "Коэффициент сезонности применяется для корректировки объема продаж "
            "в зависимости от периода относительно среднемесячного планового значения:<br><br>"

            "<b>k = 1</b> — базовый уровень спроса, при котором объем продаж соответствует плановому значению.<br>"
            "<b><span style='color:#2e7d32'>k &gt; 1</span></b> — период повышенного спроса, приводящий к увеличению объема продаж "
            "(например, k = 1.2 означает рост на 20%).<br>"
            "<b><span style='color:#c62828'>k &lt; 1</span></b> — период снижения спроса, при котором объем продаж уменьшается "
            "(например, k = 0.8 означает снижение до 80% от плана, что может влиять на ликвидность)."
        )

        lbl_season_desc.setTextFormat(Qt.TextFormat.RichText)
        lbl_season_desc.setStyleSheet("font-family: 'Segoe UI'; font-size: 13px; color: #3A4A5C; border: none; line-height: 1.4;")
        lbl_season_desc.setWordWrap(True)

        season_box.addWidget(lbl_season_title)
        season_box.addWidget(lbl_season_desc)
        season_box.addStretch()

        # Правый прямоугольник — Коэффициент сценария
        scenario_frame = QFrame()
        scenario_frame.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #4A5D70; border-radius: 6px;"
        )
        scenario_box = QVBoxLayout(scenario_frame)
        scenario_box.setContentsMargins(15, 12, 15, 12)
        scenario_box.setSpacing(4)

        lbl_scenario_title = QLabel("Коэффициент сценария (k)")
        lbl_scenario_title.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; font-weight: bold; color: #4A5D70; border: none;")

        lbl_scenario_desc = QLabel(
            "Инструмент позволяет автоматически пересчитывать финансовую модель "
            "в зависимости от заданных сценарных коэффициентов:<br><br>"

            "<b>Базовый</b> (<b>k = 1.0</b>) — плановые показатели без отклонений, исходная точка расчета.<br><br>"

            "<b>Оптимистичный</b> (<b><span style='color:#2e7d32'>k = 1.3</span></b>) — рост выручки и/или снижение затрат "
            "на 30% относительно базового сценария.<br><br>"

            "<b>Пессимистичный</b> (<b><span style='color:#c62828'>k = 0.7</span></b>) — снижение выручки и/или увеличение затрат "
            "на 30% относительно базового сценария."
        )

        lbl_scenario_desc.setTextFormat(Qt.TextFormat.RichText)

        lbl_scenario_desc.setTextFormat(Qt.TextFormat.RichText)
        lbl_scenario_desc.setStyleSheet("font-family: 'Segoe UI'; font-size: 13px; color: #3A4A5C; border: none; line-height: 1.4;")
        lbl_scenario_desc.setWordWrap(True)

        scenario_box.addWidget(lbl_scenario_title)
        scenario_box.addWidget(lbl_scenario_desc)
        scenario_box.addStretch()

        coef_split_layout.addWidget(season_frame, 1)
        coef_split_layout.addWidget(scenario_frame, 1)
        coef_layout.addLayout(coef_split_layout)

        content_layout.addWidget(coef_card)

        # ── СЕКЦИЯ 4: ПОРЯДОК РАБОТЫ ──
        sec3_card, sec3_layout = self._create_section_card("Порядок работы с моделью")

        sec3_title = QLabel("Рекомендуется заполнять вкладки последовательно слева направо:")
        sec3_title.setStyleSheet(base_text_style)
        sec3_layout.addWidget(sec3_title)

        grid_steps = QGridLayout()
        grid_steps.setSpacing(15)
        for i in range(2): grid_steps.setColumnStretch(i, 1)

        steps_data = [
            ("1", "Макроэкономические параметры",
             "Задайте горизонт планирования, ставки налогов (УСН, НДС), уровень инфляции по годам и коэффициенты сезонности. Эти параметры формируют «внешнюю среду» проекта и влияют на все последующие расчёты."),
            ("2", "Ставка дисконтирования (CAPM / WACC)",
             "Введите безрисковую ставку, бета-коэффициент и ожидаемую доходность рынка. Стоимость собственного капитала рассчитается автоматически по модели CAPM, а итоговая ставка дисконтирования — по методу WACC с учётом структуры финансирования."),
            ("3", "База товаров",
             "Укажите наименования продуктов или услуг, начальные цены и объёмы продаж, а также годовые темпы роста. На основе этих данных формируется прогноз выручки."),
            ("4", "Структура финансирования",
             "Задайте соотношение собственных и заёмных средств, сумму кредита, процентную ставку и срок погашения."),
            ("5", "Денежные потоки",
             "Введите капитальные и операционные затраты. Модель автоматически разделит их на операционный, инвестиционный и финансовый денежные потоки."),
            ("6", "Результаты (последняя вкладка)",
             "Здесь представлены все итоговые показатели: NPV, ARR, IRR, PI, PP и DPP, а также пять графиков — динамика выручки и чистой прибыли, свободный и дисконтированный денежные потоки, накопленные потоки, кумулятивная окупаемость и рентабельность продаж. Переключайте сценарии — все результаты обновятся мгновенно.")
        ]

        for idx, (num, title, text) in enumerate(steps_data):
            step_card = QFrame()
            step_card.setStyleSheet("background-color: #FFFFFF; border: 1px solid #D6E6F5; border-radius: 10px;")
            step_box = QVBoxLayout(step_card)
            step_box.setContentsMargins(15, 12, 15, 12)
            step_box.setSpacing(6)

            step_header_layout = QHBoxLayout()
            step_header_layout.setSpacing(8)

            badge = QLabel(num)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedSize(22, 22)
            badge.setStyleSheet(
                "background-color: #B0C8DE; color: #FFFFFF; font-size: 12px; font-weight: bold; border-radius: 11px; border: none;")

            step_title = QLabel(title)
            step_title.setStyleSheet(
                "font-family: 'Segoe UI'; font-size: 15px; font-weight: bold; color: #2463A4; border: none;")
            step_title.setWordWrap(True)

            step_header_layout.addWidget(badge)
            step_header_layout.addWidget(step_title, 1)
            step_box.addLayout(step_header_layout)

            step_text = QLabel(text)
            step_text.setStyleSheet(
                "font-family: 'Segoe UI'; font-size: 13px; color: #4A5D70; border: none; line-height: 1.4;")
            step_text.setWordWrap(True)
            step_box.addWidget(step_text)
            step_box.addStretch()

            row, col = divmod(idx, 2)
            grid_steps.addWidget(step_card, row, col)

        sec3_layout.addLayout(grid_steps)
        content_layout.addWidget(sec3_card)

        # ── СЕКЦИЯ 5: СЦЕНАРНЫЙ АНАЛИЗ ──
        sec4_card, sec4_layout = self._create_section_card("Сценарный анализ")

        sec4_title = QLabel(
            "Модель поддерживает три сценария. Переключение производится на вкладке макропараметров и мгновенно обновляет все показатели:")
        sec4_title.setStyleSheet(base_text_style)
        sec4_title.setWordWrap(True)
        sec4_layout.addWidget(sec4_title)

        scenarios = [
            ("#7AAAC8", "○  Базовый — плановые показатели без отклонений. Исходная точка для анализа."),
            ("#7FC49A", "▲  Оптимистичный — выручка увеличивается, расходы снижаются на заданный процент. Оценка потенциала роста проекта."),
            ("#E8A09A", "▼  Пессимистичный — выручка сокращается, расходы растут. Позволяет оценить устойчивость проекта в неблагоприятных условиях и определить нижнюю границу эффективности.")
        ]

        for border_clr, sc_text in scenarios:
            sc_frame = QFrame()
            sc_frame.setStyleSheet(
                f"background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid {border_clr}; border-radius: 6px;")
            sc_box = QVBoxLayout(sc_frame)
            sc_box.setContentsMargins(15, 10, 15, 10)

            sc_lbl = QLabel(sc_text)
            sc_lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 14px; color: #3A4A5C; border: none;")
            sc_lbl.setWordWrap(True)

            sc_box.addWidget(sc_lbl)
            sec4_layout.addWidget(sc_frame)

        content_layout.addWidget(sec4_card)

        # ── СЕКЦИЯ 6: ВАЖНОЕ ПРИМЕЧАНИЕ ──
        note_frame = QFrame()
        note_frame.setStyleSheet("background-color: #FFFDF4; border: 1px solid #E2D59A; border-radius: 10px;")
        note_layout = QVBoxLayout(note_frame)
        note_layout.setContentsMargins(20, 15, 20, 15)

        note_lbl = QLabel(
            "⚠️  Обратите внимание:  все расчёты выполняются в годовом представлении. Модель ориентирована на проекты в сфере торговли и услуг с фиксированным ценообразованием и горизонтом планирования до 5 лет. При изменении любого входного параметра все показатели пересчитываются автоматически в режиме реального времени.")
        note_lbl.setStyleSheet(base_text_style)
        note_lbl.setWordWrap(True)
        note_layout.addWidget(note_lbl)

        content_layout.addWidget(note_frame)

        # ── СЕКЦИЯ 7: ВАЛИДАЦИЯ И ОШИБКИ ВВОДА ──
        validation_frame = QFrame()
        validation_frame.setStyleSheet("background-color: #FFF5F5; border: 1px solid #E8A09A; border-radius: 10px;")
        validation_layout = QVBoxLayout(validation_frame)
        validation_layout.setContentsMargins(20, 15, 20, 15)

        validation_lbl = QLabel(
            "🛑  Проверка вводимых данных: В инструмент интегрирована автоматическая проверка (валидация) входящих значений. "
            "При попытке ввести некорректные данные (например, текст вместо цифр, отрицательные ставки или значения, выходящие за допустимые лимиты), "
            "система их не примет. На экране мгновенно появится всплывающая текстовая подсказка или окно с описанием ошибки, "
            "где будет указано, какие именно параметры и в каком формате ожидает программа.")
        validation_lbl.setStyleSheet(base_text_style)
        validation_lbl.setWordWrap(True)
        validation_layout.addWidget(validation_lbl)

        content_layout.addWidget(validation_frame)

        # Интеграция скролла
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # ══ КНОПКА ОК ══
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #B0C8DE;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 36px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7AAAC8;
            }
            QPushButton:pressed {
                background-color: #5B8FA8;
            }
        """)
        main_layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)

    def _create_section_card(self, title_text):
        """Возвращает готовую карточку (QFrame) и внутренний слой (QVBoxLayout) для контента"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #D0E6F5;
                border-radius: 15px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        header_title = QLabel(title_text)
        header_title.setStyleSheet("""
            font-family: 'Segoe UI', Arial; 
            font-size: 16px; 
            font-weight: bold; 
            color: #002B5B; 
            padding: 15px 20px 5px 20px;
            border: none;
            background: transparent;
        """)
        card_layout.addWidget(header_title)

        content_widget = QWidget()
        content_widget.setStyleSheet("border: none; background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 20)
        content_layout.setSpacing(12)

        card_layout.addWidget(content_widget)

        return card, content_layout