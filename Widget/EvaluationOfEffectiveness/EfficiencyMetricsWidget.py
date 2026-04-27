import numpy as np
import numpy_financial as npf
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QWidget, QFrame,
    QSizePolicy, QPushButton, QGridLayout  # <--- ДОБАВЬТЕ ЭТОТ КЛАСС
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer

# Импорты для графиков
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class EfficiencyMetricsWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.last_free_cf = []
        self.last_dist_cf = []
        self.last_revenue = []
        self.last_investments = 0
        self.last_discount_rate = 0.15
        self.last_months_struct = {}
        self.charts_drawn_once = False
        # Основной лейаут
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(15)

        # 1. Заголовок
        self.title = QLabel("Показатели эффективности инвестиционного проекта")
        self.title.setFont(QFont("Times New Roman", 16, QFont.Weight.Bold))  # Было 18
        self.main_layout.addWidget(self.title)

        # 2. Таблица
        # 2. Таблица
        # --- ТАБЛИЦА ---
        # --- ТАБЛИЦА С СОВРЕМЕННЫМ ДИЗАЙНОМ ---
        # --- ТАБЛИЦА С СОВРЕМЕННЫМ ДИЗАЙНОМ ---
        # --- ТАБЛИЦА С СОВРЕМЕННЫМ ДИЗАЙНОМ ---
        self.table_container_frame = QFrame()
        self.table_container_frame.setObjectName("modernTableFrame")

        self.table = QTableWidget(8, 3)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["Наименование показателя", "Значение", "Заключение"])
        self.table.setShowGrid(False)

        # Настройка заголовков
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Чтобы не обрезалось заключение

        # Фиксируем высоту, но даем ширине подстроиться
        self.table.setFixedHeight(290)  # Немного увеличим, чтобы влезли все 8 строк без скролла

        # --- ВАЖНЫЙ МОМЕНТ: Расчет точной ширины ---
        # Вычисляем сумму ширин всех колонок + небольшой запас на рамки
        self.table.setMinimumWidth(
            header.length() + self.table.verticalHeader().width() + 399
        )

        # Позволяем контейнеру сжиматься до размеров таблицы
        self.table_container_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # Размещаем таблицу внутри фрейма
        frame_layout = QVBoxLayout(self.table_container_frame)
        frame_layout.setContentsMargins(2, 2, 2, 2)
        frame_layout.addWidget(self.table)

        # СТИЛИ CSS
        # СТИЛИ CSS
        # СТИЛИ CSS
        self.setStyleSheet("""
                    #modernTableFrame {
                        background-color: white;
                        border: 1px solid #D0E6F5;
                        border-radius: 12px;
                    }

                    QTableWidget {
                        outline: none;
                        background-color: white;
                        border: none;
                        font-family: 'Times New Roman';
                        font-size: 12pt;
                        border-radius: 11px;
                        /* Убираем выбор цвета фона здесь, чтобы работал программный код */
                    }
                   

                    QHeaderView::section {
                        background-color: #D0E6F5;
                        color: #002B5B;
                        font-weight: bold;
                        font-size: 12pt;
                        padding: 12px;
                        border: none;
                        border-right: 1px solid #ADC5D5;
                    }

                    QHeaderView::section:horizontal:first {
                        border-top-left-radius: 11px;
                    }
                    QHeaderView::section:horizontal:last {
                        border-top-right-radius: 11px;
                        border-right: none;
                    }

                    /* ВАЖНО: Убран background-color и color, чтобы работал setBackground/setForeground в коде */
                   QTableWidget::item {
                        padding: 10px;
                        border-bottom: 1px solid #F1F5F9;
                        /* background-color: white; <--- ЭТУ СТРОКУ НУЖНО УДАЛИТЬ ИЛИ ЗАКОММЕНТИРОВАТЬ */
                    }

                    QTableWidget::item:hover {
                        background-color: #F8FAFC;
                    }
                """)
        # Оборачиваем всё в горизонтальный лейаут для выравнивания
        # --- НОВЫЙ ГОРИЗОНТАЛЬНЫЙ КОНТЕЙНЕР ДЛЯ ТАБЛИЦЫ И СПРАВКИ ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Добавляем таблицу (фрейм, который вы уже создали)
        content_layout.addWidget(self.table_container_frame)

        # Добавляем панель справки
        self.info_panel = self._create_info_panel()
        content_layout.addWidget(self.info_panel)

        content_layout.addStretch()  # Чтобы все не разъезжалось

        # Вместо старого table_outer_layout добавляем новый content_layout в main_layout
        self.main_layout.addLayout(content_layout)
        self._setup_static_names()
        # 3. Кнопка
        btn_layout = QHBoxLayout()
        self.draw_btn = QPushButton("Графики")

        self.charts_need_update = False
        self.set_draw_btn_style("default")
        self.draw_btn.setMinimumSize(200, 50)
        self.draw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.draw_btn.setStyleSheet("""
            QPushButton {
                background-color: #87CEFA; color: #002B5B; font-weight: bold;
                font-size: 16px; border-radius: 10px; border: 2px solid #5F9EA0;
            }
            QPushButton:hover { background-color: #00BFFF; color: white; }
            QPushButton:pressed { background-color: #1E90FF; }
        """)
        self.draw_btn.clicked.connect(self.on_draw_clicked)
        btn_layout.addStretch()
        btn_layout.addWidget(self.draw_btn)
        btn_layout.addStretch()
        self.main_layout.addLayout(btn_layout)

        # 4. Область графиков
        self.figure = Figure(figsize=(12, 14), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(1200)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.canvas.setVisible(False)
        self.main_layout.addWidget(self.canvas)

        self.main_layout.addStretch()

        self.color_cf = '#AED6F1'  # Нежно-голубой
        self.color_dcf = '#BDC3C7'  # Мягкий серый

    def _setup_static_names(self):
        names = [
            "Учётная норма доходности (ARR),%",
            "Чистая приведенная стоимость (NPV), руб",
            "Внутренняя ставка доходности (IRR), %",
            "Срок окупаемости (PP), мес",
            "Дисконтированный срок окупаемости (DPP), мес",
            "Индекс доходности (PI), ед",
            "Срок окупаемости (PP), год",
            "Дисконтированный срок окупаемости (DPP), год"
        ]
        for i, name in enumerate(names):
            item = QTableWidgetItem(name)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setFont(QFont("Times New Roman", 12))
            item.setForeground(QColor("#1E293B"))
            self.table.setItem(i, 0, item)

    def set_draw_btn_style(self, state):
        font_style = "font-size: 12pt; font-family: 'Times New Roman';"

        styles = {
            # Синяя (обычное состояние)
            "default": f"{font_style} background-color: #E0F7FF; color: #002B5B; border-radius: 10px; font-weight: bold; border: 2px solid #87CEFA;",
            # Зеленая (графики только что отрисованы)
            "success": f"{font_style} background-color: #C8E6C9; color: #2E7D32; border-radius: 10px; font-weight: bold; border: 2px solid #A5D6A7;",
            # Желтая (данные изменились, нужно нажать для обновления графика)
            "warning": f"{font_style} background-color: #FFF9C4; color: #827717; border-radius: 10px; font-weight: bold; border: 2px solid #FFF176;"
        }
        self.draw_btn.setStyleSheet(styles.get(state, styles["default"]))
    def _fill_row(self, row, val, comment, is_good):
        """
        Финальная настройка: максимально светлый и свежий зеленый,
        сохраняющий читаемость при жирном начертании.
        """
        # Сверхсветлый фон для всей строки
        bg_color = QColor("#F7FFF7") if is_good else QColor("#FFF9F9")

        # --- ЦВЕТА ТЕКСТА ---
        # Светлый, но насыщенный зеленый (Leafy Green)
        # Он ярче предыдущего, но за счет жирности шрифта будет отлично виден
        green_text = QColor("#43A047")

        # Насыщенный красный (Light Coral Red)
        red_text = QColor("#E53935")

        val_text_color = green_text if is_good else red_text
        comm_text_color = QColor("#546E7A")  # Спокойный серо-голубой для комментов

        # Шрифты
        font_regular = QFont("Times New Roman", 12)
        font_status = QFont("Times New Roman", 13, QFont.Weight.Bold)

        # 1. Значение (Второй столбец)
        val_item = QTableWidgetItem(str(val))
        val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        val_item.setFont(font_status)
        val_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 1, val_item)

        # 2. Заключение (Третий столбец)
        com_item = QTableWidgetItem(f"  {comment}")
        com_item.setFont(font_regular)
        com_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 2, com_item)

        # Применяем заливку и цвет ко всем ячейкам строки
        for col in range(3):
            item = self.table.item(row, col)
            if item:
                # Фон ячейки
                item.setData(Qt.ItemDataRole.BackgroundRole, bg_color)

                if col == 1:
                    # Жирное значение в цвете
                    item.setForeground(val_text_color)
                elif col == 2:
                    # Текст комментария
                    item.setForeground(comm_text_color)
                else:
                    # Название (первая колонка) - оставляем строгим
                    item.setForeground(QColor("#2C3E50")) # Название показателя
    def _setup_ui_additional(self):
        # Вспомогательный метод для кнопки и холста, чтобы не загромождать init
        btn_layout = QHBoxLayout()
        self.draw_btn = QPushButton("Графики")
        self.draw_btn.setMinimumSize(200, 50)
        self.draw_btn.clicked.connect(self.on_draw_clicked)
        self.draw_btn.setStyleSheet(
            "QPushButton { background-color: #87CEFA; border-radius: 10px; font-weight: bold; }")

        btn_layout.addStretch()
        btn_layout.addWidget(self.draw_btn)
        btn_layout.addStretch()
        self.main_layout.addLayout(btn_layout)

        self.figure = Figure(figsize=(12, 20), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setVisible(False)
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addStretch()

        self.color_cf = '#ADD8E6'
        self.color_dcf = '#808000'

    def update_metrics(self, net_profit_monthly, free_cf_monthly, discounted_cf_monthly, investments,
                       discount_rate=0.15, target_pp_months=36, revenue_monthly=None,
                       start_month=1, months_struct=None):

        self.last_start_month = start_month
        self.last_free_cf = free_cf_monthly
        self.last_dist_cf = discounted_cf_monthly
        self.last_revenue = revenue_monthly if revenue_monthly else []
        self.last_investments = investments
        self.last_discount_rate = discount_rate

        if investments <= 0: return

        # Определяем эффективную ставку (максимальную из представленных)
        # --- НОВЫЙ БЛОК: ПОЛУЧЕНИЕ ДИНАМИЧЕСКОЙ СТАВКИ ИЗ CAPM ---
        effective_rate = discount_rate  # Значение по умолчанию (0.15)

        # Проверяем, есть ли связь с главным окном и виджетом CAPM
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'capm_widget'):
            capm = self.main_window.capm_widget
            re_values = []

            # Собираем все ставки Re за 5 лет из CAPMWidget
            for year_str in capm.years:
                val = capm.get_re_for_year(year_str)
                if val:
                    re_values.append(val / 100)  # из % в доли (например, 0.21)

            if re_values:
                # Берем максимальную ставку (самый консервативный сценарий)
                effective_rate = max(re_values)
                print(f"DEBUG: Найдена динамическая ставка в CAPM: {effective_rate:.2%}")
        else:
            print("DEBUG: Связь с CAPMWidget не найдена, используем 15%")

        # --- 1. ARR ---
        avg_annual_np = (sum(net_profit_monthly) / (len(net_profit_monthly) / 12)) if len(net_profit_monthly) > 0 else 0
        arr = avg_annual_np / investments
        is_arr_ok = arr >= effective_rate

        # ВЫВОД В КОНСОЛЬ:
        print("-" * 30)
        print(f"DEBUG ARR: Средняя год. прибыль = {avg_annual_np:,.2f}")
        print(f"DEBUG ARR: Инвестиции = {investments:,.2f}")
        print(f"DEBUG ARR: Результат ARR = {arr:.2%}")
        print(f"DEBUG ARR: Сравнение с эффективной ставкой = {effective_rate:.2%}")
        print(f"DEBUG ARR: Статус = {'OK' if is_arr_ok else 'LOW'}")
        print("-" * 30)

        status_text = "выше нормы" if is_arr_ok else "ниже нормы"
        comment = f"Доходность {status_text} ({effective_rate:.1%})"
        self._fill_row(0, f"{arr:.1%}", comment, is_arr_ok)

        # --- 2. NPV ---
        npv = sum(discounted_cf_monthly) - investments
        is_npv_ok = npv >= 0
        self._fill_row(1, f"{npv:,.0f}".replace(",", " "), "Проект окупаем" if is_npv_ok else "Проект убыточен",
                       is_npv_ok)

        # --- 3. IRR ---
        irr_stream = [-investments] + free_cf_monthly
        irr_annual = 0
        try:
            m_irr = npf.irr(irr_stream)
            if not np.isnan(m_irr):
                irr_annual = (1 + m_irr) ** 12 - 1
        except:
            pass
        is_irr_ok = irr_annual >= effective_rate
        self._fill_row(2, f"{irr_annual:.1%}", f"Выше {effective_rate:.1%}" if is_irr_ok else f"Ниже {effective_rate:.1%}",
                       is_irr_ok)

        # --- 4 & 6. PP (Месяцы и Годы) ---
        pp = self._calc_payback(free_cf_monthly, investments)
        is_pp_ok = pp is not None and pp <= target_pp_months
        pp_text = f"{pp:.1f}" if pp else "—"
        pp_comm = "В рамках лимита" if is_pp_ok else "Слишком долгий срок"
        self._fill_row(3, pp_text, pp_comm, is_pp_ok)
        self._fill_row(6, f"{pp / 12:.1f}" if pp else "—", "", is_pp_ok)

        # --- 5 & 7. DPP (Дисконтированный) ---
        dpp = self._calc_payback(discounted_cf_monthly, investments)
        is_dpp_ok = dpp is not None and dpp <= target_pp_months
        dpp_text = f"{dpp:.1f}" if dpp else "—"
        dpp_comm = "В рамках лимита" if is_dpp_ok else "Не окупается с учетом дисконта"
        self._fill_row(4, dpp_text, dpp_comm, is_dpp_ok)
        self._fill_row(7, f"{dpp / 12:.1f}" if dpp else "—", "", is_dpp_ok)

        # --- 8. PI ---
        pi = sum(discounted_cf_monthly) / investments if investments > 0 else 0
        is_pi_ok = pi >= 1.0
        self._fill_row(5, f"{pi:.2f}", "Эффективен" if is_pi_ok else "Неэффективен", is_pi_ok)
        # В самом конце метода:
        if self.charts_drawn_once:
            self.charts_need_update = True
            self.draw_btn.setText("Обновить графики *")
            self.set_draw_btn_style("warning")
        else:
            self.charts_need_update = False
            self.draw_btn.setText("Графики")
            self.set_draw_btn_style("default")
    def _create_info_panel(self):
        panel = QFrame()
        panel.setObjectName("infoPanel")
        panel.setFixedWidth(710)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)

        header = QLabel("Описание")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "font-family: 'Times New Roman'; font-size: 14pt; font-weight: bold; color: #002B5B; background: transparent;")
        layout.addWidget(header)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        def create_item_widget(title, pos_text, neg_text):
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            item_layout = QVBoxLayout(container)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(5)

            base_style = "font-family: 'Times New Roman'; font-size: 11pt; background: transparent; border: none; padding: 0px;"

            t_label = QLabel(title)
            t_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_label.setStyleSheet(base_style + "font-weight: bold; color: #002B5B;")

            pos_label = QLabel(f"• {pos_text}")
            pos_label.setWordWrap(True)
            pos_label.setStyleSheet(base_style + "color: #2E7D32;")

            neg_label = QLabel(f"• {neg_text}")
            neg_label.setWordWrap(True)
            neg_label.setStyleSheet(base_style + "color: #C62828;")

            item_layout.addWidget(t_label)
            item_layout.addWidget(pos_label)
            item_layout.addWidget(neg_label)
            return container

        # --- Наполнение сетки (3 строки, 2 колонки) ---

        # Строка 0
        grid_layout.addWidget(create_item_widget(
            "ARR",
            "ARR > WACC ➡  Доходность выше требуемой нормы",
            "ARR < WACC ➡  Прибыль не покрывает объем вложений"
        ), 0, 0)

        grid_layout.addWidget(create_item_widget(
            "NPV",
            "NPV > 0 ➡ Средства покрывают инвестиции и риски",
            "NPV < 0 ➡ Доходы ниже суммы затрат"
        ), 0, 1)

        # Строка 1
        grid_layout.addWidget(create_item_widget(
            "IRR",
            "IRR > WACC ➡ Проект устойчив к стоимости капитала",
            "IRR < WACC ➡ Риск превышает внутреннюю доходность"
        ), 1, 0)

        grid_layout.addWidget(create_item_widget(
            "PI",
            "PI > 1 ➡ Каждый рубль приносит чистую прибыль",
            "PI < 1 ➡ На каждый рубль зафиксирован убыток"
        ), 1, 1)

        # Строка 2 (НОВЫЕ ПОКАЗАТЕЛИ)
        grid_layout.addWidget(create_item_widget(
            "PP",
            "PP < цели ➡ Инвестиции возвращаются в срок",
            "PP > цели ➡ Слишком медленный возврат капитала"
        ), 2, 0)

        grid_layout.addWidget(create_item_widget(
            "DPP",
            "DPP < срока ➡ Окупаемость с учетом обесценения денег",
            "DPP > срока ➡ Проект не окупается в реальных ценах"
        ), 2, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

        panel.setStyleSheet("""
            #infoPanel {
                background-color: #FFFFFF;
                border: 1px solid #D0E6F5;
                border-radius: 15px;
            }
            #infoPanel QLabel {
                background-color: transparent; 
                border: none;
            }
        """)
        return panel

    def on_draw_clicked(self):
        if not hasattr(self, 'last_free_cf') or not self.last_free_cf:
            return

        self.canvas.setVisible(True)
        self._draw_charts(self.last_free_cf, self.last_dist_cf, self.last_revenue)
        self.charts_drawn_once = True
        # Стилизация после нажатия
        self.charts_need_update = False
        self.draw_btn.setText("Графики построены ✓")

        self.set_draw_btn_style("success")

        # Через 2 секунды возвращаем текст в норму, но оставляем синей
        QTimer.singleShot(2000, self.reset_draw_button)

    def _draw_charts(self, cf, dcf, revenue_monthly):
        self.figure.clear()
        font_style = {'fontname': 'Times New Roman', 'size': 12}
        investments = getattr(self, 'last_investments', 0)
        start_month = getattr(self, 'last_start_month', 1)

        # --- Подготовка данных (без изменений) ---
        cf_yearly, dcf_yearly = [], []
        first_year_end = 13 - start_month
        cf_yearly.append(sum(cf[:first_year_end]))
        dcf_yearly.append(sum(dcf[:first_year_end]))
        remaining_cf, remaining_dcf = cf[first_year_end:], dcf[first_year_end:]
        for i in range(0, len(remaining_cf), 12):
            cf_yearly.append(sum(remaining_cf[i:i + 12]))
            dcf_yearly.append(sum(remaining_dcf[i:i + 12]))

        num_years = len(cf_yearly)
        years_range = np.arange(1, num_years + 1)
        cum_cf_yearly, cum_dcf_yearly = [-investments], [-investments]
        c_cf, c_dcf = -investments, -investments
        for i in range(num_years):
            c_cf += cf_yearly[i];
            c_dcf += dcf_yearly[i]
            cum_cf_yearly.append(c_cf);
            cum_dcf_yearly.append(c_dcf)
        years_with_zero = np.arange(0, num_years + 1)

        # --- ОТРИСОВКА ---
        font_name = 'Times New Roman'
        font_size = 12

        # 1. Чистый денежный поток (Бары)
        ax1 = self.figure.add_subplot(311)
        width = 0.35
        ax1.bar(years_range - width / 2, cf_yearly, width, label='Свободный ДП', color=self.color_cf)
        ax1.bar(years_range + width / 2, dcf_yearly, width, label='Дисконт. ДП', color=self.color_dcf)

        ax1.set_title("1. Чистый денежный поток (по календарным годам)", fontname=font_name, fontsize=13,
                      fontweight='bold', pad=15)
        ax1.set_xlabel("Год проекта", fontname=font_name, fontsize=font_size)
        ax1.set_ylabel("Поток, руб", fontname=font_name, fontsize=font_size)
        ax1.set_xticks(years_range)
        ax1.legend(frameon=False, prop={'family': font_name, 'size': font_size})
        ax1.grid(True, linestyle='--', alpha=0.4, axis='y')  # Сетка

        # 2. Кумулятивный поток (Линии)
        ax2 = self.figure.add_subplot(312)
        ax2.plot(years_with_zero, cum_cf_yearly, 'o-', color=self.color_cf, linewidth=2, label='Накопленный СДП')
        ax2.plot(years_with_zero, cum_dcf_yearly, 's-', color=self.color_dcf, linewidth=2, label='Накопленный ДДП')

        # Умные подписи точек для AX2
        for x, y_cf, y_dcf in zip(years_with_zero, cum_cf_yearly, cum_dcf_yearly):
            offset_cf = 12 if y_cf >= y_dcf else -20
            offset_dcf = -20 if y_cf >= y_dcf else 12

            ax2.annotate(f'{y_cf:,.0f}'.replace(',', ' '), (x, y_cf), textcoords="offset points",
                         xytext=(0, offset_cf), ha='center', fontname=font_name, fontsize=10, color='#2C3E50',
                         fontweight='bold')
            ax2.annotate(f'{y_dcf:,.0f}'.replace(',', ' '), (x, y_dcf), textcoords="offset points",
                         xytext=(0, offset_dcf), ha='center', fontname=font_name, fontsize=10, color='#7F8C8D')

        ax2.axhline(0, color='#E53935', linestyle='--', alpha=0.6)
        ax2.set_title("2. Кумулятивный денежный поток (линейный)", fontname=font_name, fontsize=13, fontweight='bold',
                      pad=15)
        ax2.set_xlabel("Год", fontname=font_name, fontsize=font_size)
        ax2.set_ylabel("Накопленный итог, руб", fontname=font_name, fontsize=font_size)
        ax2.set_xticks(years_with_zero)
        ax2.legend(frameon=False, prop={'family': font_name, 'size': font_size})  # Легенда
        ax2.grid(True, linestyle='--', alpha=0.4)  # Сетка

        # 3. Кумулятивный поток (Бары)
        ax4 = self.figure.add_subplot(313)
        ax4.bar(years_with_zero - width / 2, cum_cf_yearly, width, color=self.color_cf, label='СДП (накопл.)')
        ax4.bar(years_with_zero + width / 2, cum_dcf_yearly, width, color=self.color_dcf, label='ДДП (накопл.)')
        ax4.set_title("3. Сравнение накопленных потоков (гистограмма)", fontname=font_name, fontsize=13,
                      fontweight='bold', pad=15)
        ax4.set_xlabel("Год", fontname=font_name, fontsize=font_size)
        ax4.set_ylabel("Руб", fontname=font_name, fontsize=font_size)
        ax4.set_xticks(years_with_zero)
        ax4.legend(frameon=False, prop={'family': font_name, 'size': font_size})
        ax4.grid(True, linestyle='--', alpha=0.4, axis='y')

        # 4. NPV Profile


        # Финальная настройка всех осей (Шрифты чисел и удаление рамок)
        for ax in [ax1, ax2, ax4]:
            for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontname(font_name)
                label.set_fontsize(font_size)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        self._add_bar_labels(ax1)
        self._add_bar_labels(ax4)

        self.figure.tight_layout(pad=4.0)
        self.canvas.draw()

    def _add_line_labels(self, ax, x_data, y_data, color):
        for x, y in zip(x_data, y_data):
            ax.annotate(f'{y:,.0f}'.replace(',', ' '), (x, y),
                         textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color=color, fontweight='bold')


    def _add_bar_labels(self, ax):
        for rect in ax.patches:
            height = rect.get_height()
            if height == 0: continue
            ax.annotate(f'{height:,.0f}'.replace(',', ' '),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        # Добавляем параметры шрифта здесь:
                        fontname='Times New Roman',
                        fontsize=12)
    def _calc_payback(self, cash_flows, investment):
        cumulative = -investment
        for i, cf in enumerate(cash_flows):
            prev_cum = cumulative
            cumulative += cf
            if cumulative >= 0:
                return i + (abs(prev_cum) / cf) if cf != 0 else i
        return None

    def reset_draw_button(self):
        # Если за эти 2 секунды данные снова не изменились, возвращаем дефолт
        if not self.charts_need_update:
            self.draw_btn.setText("Графики")
            self.set_draw_btn_style("default")
