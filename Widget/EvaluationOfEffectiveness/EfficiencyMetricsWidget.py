import numpy as np
import numpy_financial as npf
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QWidget, QFrame,
    QSizePolicy, QPushButton
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

# Импорты для графиков
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class EfficiencyMetricsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.last_free_cf = []
        self.last_dist_cf = []
        self.last_revenue = []
        self.last_investments = 0
        self.last_discount_rate = 0.15
        self.last_months_struct = {}

        # Основной лейаут
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(25)

        # 1. Заголовок
        self.title = QLabel("Показатели эффективности инвестиционного проекта")
        self.title.setFont(QFont("Times New Roman", 18, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title)

        # 2. Таблица
        self.table = QTableWidget(8, 3)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["Наименование показателя", "Значение", "Заключение"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.table.setFixedHeight(340)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.table.setStyleSheet("""
            QTableWidget { 
                background-color: white; 
                border: 2px solid #D0E6F5; 
                gridline-color: #E0E0E0;
                font-family: 'Times New Roman'; 
                font-size: 13pt; 
            }
            QHeaderView::section { 
                background-color: #D0E6F5; font-weight: bold; font-size: 13pt;
                border: 1px solid #ADC5D5; padding: 8px;
            }
        """)
        self.main_layout.addWidget(self.table)
        self._setup_static_names()

        # 3. Кнопка
        btn_layout = QHBoxLayout()
        self.draw_btn = QPushButton("Графики")
        self.draw_btn.setMinimumSize(450, 50)
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
        self.figure = Figure(figsize=(12, 18), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(1600)
        self.canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.canvas.setVisible(False)
        self.main_layout.addWidget(self.canvas)

        self.main_layout.addStretch()

        self.color_cf = '#ADD8E6'
        self.color_dcf = '#808000'

    def _setup_static_names(self):
        names = [
            "Учётная норма доходности (ARR)",
            "Чистая приведенная стоимость (NPV), руб",
            "Внутренняя ставка доходности (IRR), %",
            "Срок окупаемости (PP), мес",
            "Дисконтированный срок окупаемости (DPP), мес",
            "Эффективность проекта (PI), ед",
            "Срок окупаемости (PP), год",
            "Дисконтированный срок окупаемости (DPP), год"
        ]
        for i, name in enumerate(names):
            item = QTableWidgetItem(name)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setFont(QFont("Times New Roman", 12))
            self.table.setItem(i, 0, item)

    def _fill_row(self, row, val, comment, is_good):
        bg_color = QColor("#E8F5E9") if is_good else QColor("#FFEBEE")

        val_item = QTableWidgetItem(str(val))
        val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        val_item.setBackground(bg_color)
        val_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        com_item = QTableWidgetItem(comment)
        com_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

        self.table.setItem(row, 1, val_item)
        self.table.setItem(row, 2, com_item)

    def update_metrics(self, net_profit_monthly, free_cf_monthly, discounted_cf_monthly, investments,
                       discount_rate=0.15, target_pp_months=36, revenue_monthly=None,
                       start_month=1, months_struct=None):  # Добавили параметры здесь
        # СОХРАНЯЕМ МЕСЯЦ ЗДЕСЬ
        self.last_start_month = start_month
        self.last_free_cf = free_cf_monthly

        self.last_dist_cf = discounted_cf_monthly
        self.last_revenue = revenue_monthly if revenue_monthly else []
        self.last_investments = investments
        self.last_discount_rate = discount_rate
        self.last_months_struct = months_struct

        if investments <= 0: return

        # ARR
        avg_annual_np = (sum(net_profit_monthly) / (len(net_profit_monthly) / 12)) if len(net_profit_monthly) > 0 else 0
        arr = avg_annual_np / investments
        self._fill_row(0, f"{arr:.1%}", "ОК" if arr >= discount_rate else "Ниже нормы", arr >= discount_rate)

        # NPV
        npv = sum(discounted_cf_monthly) - investments
        self._fill_row(1, f"{npv:,.0f}".replace(",", " "), "Окупился" if npv >= 0 else "Не окупился", npv >= 0)

        # IRR
        irr_stream = [-investments] + free_cf_monthly
        irr_annual = 0
        try:
            m_irr = npf.irr(irr_stream)
            if not np.isnan(m_irr):
                irr_annual = (1 + m_irr) ** 12 - 1
        except:
            pass
        self._fill_row(2, f"{irr_annual:.1%}", "Выше WACC" if irr_annual >= discount_rate else "Низкая",
                       irr_annual >= discount_rate)

        # Payback
        pp = self._calc_payback(free_cf_monthly, investments)
        dpp = self._calc_payback(discounted_cf_monthly, investments)
        self._fill_row(3, f"{pp:.1f}" if pp else "—", "В норме" if pp and pp <= target_pp_months else "Долго",
                       pp and pp <= target_pp_months)
        self._fill_row(4, f"{dpp:.1f}" if dpp else "—", "В норме" if dpp and dpp <= target_pp_months else "Долго",
                       dpp and dpp <= target_pp_months)

        # PI
        pi = sum(discounted_cf_monthly) / investments if investments > 0 else 0
        self._fill_row(5, f"{pi:.2f}", "Прибыльный" if pi >= 1 else "Убыточный", pi >= 1)
        self._fill_row(6, f"{pp / 12:.1f}" if pp else "—", "", True)
        self._fill_row(7, f"{dpp / 12:.1f}" if dpp else "—", "", True)

    def on_draw_clicked(self):
        """Метод без обращения к несуществующему self.scroll"""
        if not hasattr(self, 'last_free_cf') or not self.last_free_cf:
            return

        self.canvas.setVisible(True)
        self._draw_charts(self.last_free_cf, self.last_dist_cf, self.last_revenue)

    def _draw_charts(self, cf, dcf, revenue_monthly):
        self.figure.clear()
        print(f"DEBUG DRAW: Месяц начала = {getattr(self, 'last_start_month', 'НЕ НАЙДЕН')}")
        investments = getattr(self, 'last_investments', 0)
        start_month = getattr(self, 'last_start_month', 1)

        # --- КОРРЕКТНАЯ АГРЕГАЦИЯ С УЧЕТОМ СМЕЩЕНИЯ ---
        cf_yearly = []
        dcf_yearly = []

        # Считаем первый год (от start_month до конца календарного года)
        first_year_end = 13 - start_month

        # Данные для первого столбца
        cf_yearly.append(sum(cf[:first_year_end]))
        dcf_yearly.append(sum(dcf[:first_year_end]))

        # Данные для последующих лет
        remaining_cf = cf[first_year_end:]
        remaining_dcf = dcf[first_year_end:]

        for i in range(0, len(remaining_cf), 12):
            chunk_cf = remaining_cf[i:i + 12]
            chunk_dcf = remaining_dcf[i:i + 12]
            if chunk_cf:
                cf_yearly.append(sum(chunk_cf))
                dcf_yearly.append(sum(chunk_dcf))

        num_years = len(cf_yearly)
        years_range = np.arange(1, num_years + 1)
        # ----------------------------------------------

        # Накопленный итог
        cum_cf_yearly = [-investments]
        cum_dcf_yearly = [-investments]
        c_cf, c_dcf = -investments, -investments

        for i in range(num_years):
            c_cf += cf_yearly[i]
            c_dcf += dcf_yearly[i]
            cum_cf_yearly.append(c_cf)
            cum_dcf_yearly.append(c_dcf)

        years_with_zero = np.arange(0, num_years + 1)

        # --- ОТРИСОВКА (без изменений в логике, но с обновленными данными) ---
        ax1 = self.figure.add_subplot(411)
        ax2 = self.figure.add_subplot(412)
        ax4 = self.figure.add_subplot(413)
        ax3 = self.figure.add_subplot(414)

        width = 0.35
        ax1.bar(years_range - width / 2, cf_yearly, width, label='Свободный ДП', color=self.color_cf)
        ax1.bar(years_range + width / 2, dcf_yearly, width, label='Дисконт. ДП', color=self.color_dcf)
        ax1.set_title("1. Чистый денежный поток (по календарным годам)", fontsize=11, fontweight='bold')
        ax1.set_xticks(years_range)
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.5)
        self._add_bar_labels(ax1)

        # Линейный график накопленного итога
        ax2.plot(years_with_zero, cum_cf_yearly, 'o-', color=self.color_cf, label='Накопленный СДП')
        ax2.plot(years_with_zero, cum_dcf_yearly, 's-', color=self.color_dcf, label='Накопленный ДДП')
        ax2.axhline(0, color='red', linestyle='--', alpha=0.6)
        ax2.set_xticks(years_with_zero)
        ax2.set_title("2. Кумулятивный денежный поток", fontsize=11, fontweight='bold')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.5)

        # Гистограмма накопленного итога
        ax4.bar(years_with_zero - width / 2, cum_cf_yearly, width, color=self.color_cf, alpha=0.7)
        ax4.bar(years_with_zero + width / 2, cum_dcf_yearly, width, color=self.color_dcf, alpha=0.7)
        ax4.set_xticks(years_with_zero)
        ax4.set_title("3. Кумулятивный денежный поток (бары)", fontsize=11, fontweight='bold')
        ax4.grid(True, linestyle='--', alpha=0.5)
        self._add_bar_labels(ax4)

        # NPV Profile
        self._draw_npv_profile(ax3, cf, investments)

        self.figure.tight_layout()
        self.canvas.draw()

    def _add_line_labels(self, ax, x_data, y_data, color):
        for x, y in zip(x_data, y_data):
            ax.annotate(f'{y:,.0f}'.replace(',', ' '), (x, y),
                         textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color=color, fontweight='bold')

    def _draw_npv_profile(self, ax, cf, investments):
        rates = np.linspace(0, 0.5, 20)
        npvs = []
        for r in rates:
            m_r = (1 + r)**(1/12) - 1
            if m_r == 0:
                npv = sum(cf) - investments
            else:
                d_factors = [(1 + m_r)**(t + 1) for t in range(len(cf))]
                npv = sum(c / d for c, d in zip(cf, d_factors)) - investments
            npvs.append(npv)

        ax.plot(rates * 100, npvs, color='#2E8B57', linewidth=2, marker='.')
        ax.axhline(0, color='black', linewidth=1)
        
        current_wacc = getattr(self, 'last_discount_rate', 0.15)
        m_wacc = (1 + current_wacc)**(1/12) - 1
        d_factors_wacc = [(1 + m_wacc)**(t + 1) for t in range(len(cf))]
        current_npv = sum(c / d for c, d in zip(cf, d_factors_wacc)) - investments
        ax.plot(current_wacc * 100, current_npv, 'ro', label=f'Текущая WACC ({current_wacc:.1%})')

        ax.set_title("График NPV (Чувствительность к ставке дисконтирования)", fontsize=11, fontweight='bold')
        ax.set_xlabel("Ставка дисконтирования, %", fontsize=9)
        ax.set_ylabel("NPV, руб", fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(fontsize=9)

    def _add_bar_labels(self, ax):
        for rect in ax.patches:
            height = rect.get_height()
            if height == 0: continue
            ax.annotate(f'{height:,.0f}'.replace(',', ' '),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    def _calc_payback(self, cash_flows, investment):
        cumulative = -investment
        for i, cf in enumerate(cash_flows):
            prev_cum = cumulative
            cumulative += cf
            if cumulative >= 0:
                return i + (abs(prev_cum) / cf) if cf != 0 else i
        return None
