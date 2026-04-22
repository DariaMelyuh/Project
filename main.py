import sys
import traceback
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QMessageBox, QPushButton, QTabWidget)
from PyQt6.QtCore import Qt
from Widget.MacroParameters.InputRowWidget import InputRowWidget
from Widget.MacroParameters.TaxesWidget import TaxesWidget
from Widget.MacroParameters.InflationWidget import InflationWidget
from Widget.MacroParameters.SeasonalityWidget import SeasonalityWidget
from Widget.MacroParameters.ScenarioWidget import ScenarioWidget
from Widget.MacroParameters.ScenarioSelectorWidget import ScenarioSelectorWidget
from Widget.Financing.CreditFundsWidget import CreditFundsWidget
from Widget.Financing.FundingStructureWidget import FundingStructureWidget
from Widget.DiscountRate.CAPMWidget import CAPMWidget
from Widget.DiscountRate.WACCWidget import WACCWidget
from Widget.SalesAndExpenses.PriceGrowthWidget import PriceGrowthWidget
from Widget.SalesAndExpenses.RevenueParametersWidget import RevenueParametersWidget
from Widget.SalesAndExpenses.CapitalExpenditureWidget import CapitalExpenditureWidget
from Widget.SalesAndExpenses.OperatingExpensesWidget import OperatingExpensesWidget
from Widget.FinancialResults.YearlyResultsWidget import YearlyResultsWidget
from Widget.SalesAndExpenses.SalesCapacityWidget import SalesCapacityWidget
from Widget.CashFlow.OperationalCashFlowWidget import OperationalCashFlowWidget
from Widget.CashFlow.InvestmentCashFlowWidget import InvestmentCashFlowWidget
from Widget.CashFlow.FinancialCashFlowWidget import FinancialCashFlowWidget
from Widget.CashFlow.PredictionCashFlowWidget import PredictionCashFlowWidget
from Widget.DiscountRate.MonthlyDiscountRateWidget import MonthlyDiscountRateWidget
from Widget.CashFlow.AccumulatedCashFlowWidget import AccumulatedCashFlowWidget
from Widget.EvaluationOfEffectiveness.EfficiencyMetricsWidget import EfficiencyMetricsWidget
from Widget.SalesAndExpenses.AssetSalesWidget import AssetSalesWidget
from Widget.SalesAndExpenses.VolumeGrowthWidget import VolumeGrowthWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Финансовая модель")
        app_font = QFont("Times New Roman", 12)
        self.setFont(app_font)
        self.setStyleSheet("""
                    * {
                        background-color: #f2f8fc;
                        font-family: "Times New Roman";
                        color: #333333;
                    }
                    QLineEdit, QComboBox, QTableWidget {
                        background-color: white;
                        border: 1px solid #A0A0A0;
                        border-radius: 4px;
                    }
                """)
        self.main_layout = QVBoxLayout(self)
        self.setup_header()
        # Настройка вкладок
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
                    QTabWidget::pane { 
                        border: 1px solid #C4C4C4; 
                        background: white; 
                    }
                    QTabBar::tab { 
                        background: #E1E1E1; 
                        padding: 12px 25px; 
                        margin: 2px; 
                        border-radius: 6px;
                        font-family: "Times New Roman";
                        font-size: 16px;
                        font-weight: bold;  /* ЖИРНЫЙ ТОЛЬКО ЗДЕСЬ */
                        color: #555555;
                    }
                    QTabBar::tab:selected { 
                        background: #87CEFA; 
                        color: white; 
                    }""")
        self.main_layout.addWidget(self.tabs)
        # Создаем все виджеты заранее (чтобы сигналы работали между вкладками)
        self.init_all_widgets()
        self.create_tab_macro()
        self.create_tab_discounting()
        self.create_tab_financing()
        self.create_tab_sales_costs()
        self.create_tab_results()
        self.create_tab_efficiency()
        #СИГНАЛЫ И ИНИЦИАЛИЗАЦИЯ
        self.setup_signals()
        self.run_initial_calculations()

    def setup_header(self):
        header = QHBoxLayout()
        title = QLabel("Финансовая модель инвестиционного проекта")
        title.setStyleSheet("""
                font-family: 'Times New Roman';
                font-size: 27px; 
                font-weight: bold;
                background: transparent;
            """)
        self.info_btn = QPushButton("Справка")
        self.info_btn.setFixedSize(120, 40)
        font = QFont("Times New Roman", 12)
        font.setBold(True)
        self.info_btn.setFont(font)
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: #87CEFA;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #B9D9EB;
                color: #333333;
            }

            QPushButton:pressed {
                background-color: #B9D9EB;
            }
        """)

        self.info_btn.clicked.connect(self.show_app_info)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.info_btn)
        self.main_layout.addLayout(header)

    def init_all_widgets(self):
        """Создание всех объектов виджетов (только инициализация)"""
        self.input_widget = InputRowWidget()
        self.taxes_widget = TaxesWidget()
        self.inflation_widget = InflationWidget()
        self.seasonality_widget = SeasonalityWidget()
        self.scenario_widget = ScenarioWidget()
        self.inv_cf_widget = InvestmentCashFlowWidget()
        self.fin_cf_widget = FinancialCashFlowWidget()
        self.prediction_cf_widget = PredictionCashFlowWidget()
        self.accumulated_cf_widget = AccumulatedCashFlowWidget()
        self.efficiency_widget = EfficiencyMetricsWidget()
        self.capm_widget = CAPMWidget(main_window=self)
        self.wacc_widget = WACCWidget(main_window=self)
        self.credit_widget = CreditFundsWidget(self.input_widget)
        self.funding_widget = FundingStructureWidget(self.credit_widget)
        self.revenue_params = RevenueParametersWidget()
        self.sales_capacity = SalesCapacityWidget()
        self.volume_growth = VolumeGrowthWidget()
        self.price_growth = PriceGrowthWidget()
        self.capex_params = CapitalExpenditureWidget()
        self.monthly_rate_widget = MonthlyDiscountRateWidget(self.wacc_widget)
        self.opex_widget = OperatingExpensesWidget()
        self.opex_widget.setMinimumWidth(610)
        self.opex_widget.setFixedHeight(420)
        self.asset_sales_widget = AssetSalesWidget(self.input_widget)
        self.op_cf_widget = OperationalCashFlowWidget()
        self.yearly_results = YearlyResultsWidget()
        self.income_selector = ScenarioSelectorWidget("Сценарий доходов")
        self.expense_selector = ScenarioSelectorWidget("Сценарий расходов")

    def create_tab_macro(self):
        """Вкладка 1: Макро-параметры + Выбор сценариев"""
        scroll, container = self.get_scroll_wrapper()
        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)
        # 1. Глобальные параметры (верхняя строка)
        layout.addWidget(self.input_widget)
        # Главный горизонтальный контейнер
        main_content_hbox = QHBoxLayout()
        main_content_hbox.setSpacing(40)
        # --- ЛЕВАЯ КОЛОНКА (Налоги и Макро) ---
        left_column = QVBoxLayout()
        left_column.setSpacing(30)
        left_column.addWidget(self.taxes_widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        left_column.addWidget(self.inflation_widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        left_column.addStretch()
        # --- ПРАВАЯ КОЛОНКА (Сезонность и блок Сценариев) ---
        right_main_hbox = QHBoxLayout()
        right_main_hbox.setSpacing(30)
        # 1. Виджет сезонности
        right_main_hbox.addWidget(self.seasonality_widget, alignment=Qt.AlignmentFlag.AlignTop)
        # 2. Вертикальный блок для Сценариев
        scenario_vertical_block = QVBoxLayout()
        scenario_vertical_block.setSpacing(10)
        # Добавляем таблицу коэффициентов
        scenario_vertical_block.addWidget(self.scenario_widget, alignment=Qt.AlignmentFlag.AlignTop)
        selectors_v_layout = QVBoxLayout()
        selectors_v_layout.setSpacing(8)  # Отступ между селектором доходов и расходов
        # Чтобы они не растягивались на всю ширину, если не нужно,
        # добавим их с выравниванием по центру или левому краю
        selectors_v_layout.addWidget(self.income_selector, alignment=Qt.AlignmentFlag.AlignLeft)
        selectors_v_layout.addWidget(self.expense_selector, alignment=Qt.AlignmentFlag.AlignLeft)
        # Добавляем вертикальную стопку селекторов под таблицу
        scenario_vertical_block.addLayout(selectors_v_layout)
        scenario_vertical_block.addStretch()
        # Добавляем блок в правую часть
        right_main_hbox.addLayout(scenario_vertical_block)
        # Собираем окно
        main_content_hbox.addLayout(left_column)
        main_content_hbox.addLayout(right_main_hbox)
        main_content_hbox.addStretch()
        layout.addLayout(main_content_hbox)
        layout.addStretch()
        self.tabs.addTab(scroll, "1. Макро-параметры")
    def create_tab_discounting(self):
        """Вкладка 2: Ставка дисконтирования — Без принудительного сжатия"""
        scroll, container = self.get_scroll_wrapper()
        # --- СТИЛИЗАЦИЯ СКРОЛЛА ---
        # ПРИМЕНЯЕМ ФУНКЦИЮ
        self.apply_custom_scroll_style(scroll)
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        # Виджеты снова занимают всё доступное горизонтальное пространство
        layout.addWidget(self.capm_widget)
        layout.addWidget(self.wacc_widget)
        layout.addWidget(self.monthly_rate_widget)
        layout.addStretch()
        self.tabs.addTab(scroll, "2. Ставка дисконтирования")
    def create_tab_financing(self):
        """Вкладка 3: Финансирование (Кредит и Структура капитала) — Возврат к стандартному растягиванию"""
        scroll, container = self.get_scroll_wrapper()
        self.apply_custom_scroll_style(scroll)
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Убрали выравнивание AlignLeft, теперь виджеты растягиваются по ширине слоя
        layout.addWidget(self.credit_widget)
        layout.addWidget(self.funding_widget)

        layout.addStretch()
        self.tabs.addTab(scroll, "3. Финансирование")

    def create_tab_sales_costs(self):
        """Вкладка 4: Выручка и Затраты (Таблицы роста в одну строку)"""
        scroll, container = self.get_scroll_wrapper()
        # Отключаем горизонтальный скролл на самой вкладке
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.apply_custom_scroll_style(scroll)

        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        layout.setContentsMargins(15, 20, 20, 20)

        # 1. Основные параметры выручки
        layout.addWidget(self.revenue_params)

        # --- НОВЫЙ БЛОК: Темпы роста в одну строку ---
        growth_row = QHBoxLayout()
        growth_row.setSpacing(10)  # Отступ между таблицами

        # Немного уменьшаем ширину каждого виджета (было 400, ставим 385 или 390)
        # Это предотвратит появление горизонтальной полосы прокрутки
        self.volume_growth.setFixedWidth(735)
        self.price_growth.setFixedWidth(735)

        growth_row.addWidget(self.volume_growth, alignment=Qt.AlignmentFlag.AlignLeft)
        growth_row.addWidget(self.price_growth, alignment=Qt.AlignmentFlag.AlignLeft)
        growth_row.addStretch()  # Чтобы они прижимались влево, если экран очень широкий

        layout.addLayout(growth_row)
        # --------------------------------------------

        # 2. Параметры мощности
        layout.addWidget(self.sales_capacity)

        # 3. Ряд затрат (CAPEX и OPEX)
        costs_row = QHBoxLayout()
        costs_row.setSpacing(10)
        costs_row.addWidget(self.capex_params, alignment=Qt.AlignmentFlag.AlignTop)
        costs_row.addWidget(self.opex_widget, alignment=Qt.AlignmentFlag.AlignTop)
        costs_row.addStretch()
        layout.addLayout(costs_row)

        # 4. Таблица продажи активов
        layout.addWidget(self.asset_sales_widget)

        layout.addStretch()
        self.tabs.addTab(scroll, "4. Продажи и затраты")
    def create_tab_results(self):
        """Вкладка 5: Итоговые результаты (Объединение двух таблиц)"""
        scroll, container = self.get_scroll_wrapper()
        self.apply_custom_scroll_style(scroll)
        layout = QVBoxLayout(container)
        # Настраиваем отступы, чтобы таблицы не прилипали к краям
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)
        # 1. Добавляем основную таблицу (Выручка, Прибыль и т.д.)
        layout.addWidget(self.yearly_results)
        # 2. Добавляем таблицу Денежного потока (НДС, Налоги к уплате, Опер. ДП)
        layout.addWidget(self.op_cf_widget)
        layout.addWidget(self.inv_cf_widget)
        layout.addWidget(self.fin_cf_widget)
        layout.addWidget(self.prediction_cf_widget)
        layout.addWidget(self.accumulated_cf_widget)
        # "Пружина" внизу, чтобы таблицы сохраняли компактный вид
        layout.addStretch()
        self.tabs.addTab(scroll, "5. Финансовые результаты")

    def create_tab_efficiency(self):
        scroll, container = self.get_scroll_wrapper()
        self.apply_custom_scroll_style(scroll)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.efficiency_widget)
        layout.addStretch()
        self.tabs.addTab(scroll, "6. Оценка эффективности проекта")

    def get_scroll_wrapper(self):
        """Создает область прокрутки, чтобы контент не наезжал друг на друга"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        scroll.setWidget(container)
        return scroll, container

    # Добавьте self первым аргументом
    def apply_custom_scroll_style(self, widget):
        """
        Применяет фирменный голубой закругленный стиль к QScrollBar или QScrollArea.
        """
        style = """
            QScrollArea {
                border: none;
                background-color: transparent;
            }

            /* Область вертикального скроллбара */
            QScrollBar:vertical {
                border: none;
                background: #F0F8FF;
                width: 12px;
                margin: 5px 2px 5px 2px;
                border-radius: 6px;
            }

            /* Ползунок (бегунок) */
            QScrollBar::handle:vertical {
                background-color: #B9D9EB; 
                min-height: 30px;
                border-radius: 6px;
                border: 1px solid #A1C9DE;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #A1C9DE;
            }

            /* Убираем стрелочки */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }

            /* Убираем фон при клике */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            /* Аналогично для горизонтального */
            QScrollBar:horizontal {
                border: none;
                background: #F0F8FF;
                height: 12px;
                margin: 2px 5px 2px 5px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #B9D9EB;
                min-width: 30px;
                border-radius: 6px;
                border: 1px solid #A1C9DE;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: none;
            }
        """
        widget.setStyleSheet(style)
    def setup_signals(self):
        """Все твои связи данных (без изменений логики)"""
        # Горизонт и даты
        self.capex_params.data_confirmed.connect(self.sync_yearly_table)
        self.opex_widget.data_confirmed.connect(self.sync_yearly_table)

        # Рефреш колонок при изменении дат
        for signal in [self.input_widget.year_cb.currentTextChanged,
                       self.input_widget.month_cb.currentIndexChanged,
                       self.input_widget.hor_le.textChanged]:  # Важно добавить hor_le
            signal.connect(self._on_project_timing_changed)

        self.taxes_widget.data_changed.connect(self.update_wacc_values)
        self.taxes_widget.data_changed.connect(self.sync_yearly_table)

        self.inflation_widget.data_changed.connect(self.sync_yearly_table)
        # WACC расчеты
        for le in self.funding_widget.inputs.values():
            le.editingFinished.connect(self.update_wacc_values)
        for key in ['equity', 'investments']:
            self.funding_widget.inputs[key].editingFinished.connect(self.sync_yearly_table)
        self.credit_widget.inputs["amount"].editingFinished.connect(self.sync_yearly_table)
        self.credit_widget.inputs["rate"].editingFinished.connect(self.sync_yearly_table)
        self.credit_widget.inputs["term"].editingFinished.connect(self.sync_yearly_table)
        if hasattr(self.credit_widget, 'rate_le'):
            self.credit_widget.rate_le.editingFinished.connect(self.update_wacc_values)
        # for le in self.taxes_widget.inputs.values():
        #     le.editingFinished.connect(self.update_wacc_values)
        # ЭТО ДОБАВИТЬ
        self.taxes_widget.data_changed.connect(self.update_wacc_values)
        self.taxes_widget.data_changed.connect(self.sync_yearly_table)
        for attr in ['rf_input', 'beta_input', 'rm_input']:
            if hasattr(self.capm_widget, attr):
                getattr(self.capm_widget, attr).editingFinished.connect(self.update_wacc_values)

        # Прочее
        self.income_selector.combo.currentTextChanged.connect(self.update_model_from_scenarios)
        self.expense_selector.combo.currentTextChanged.connect(self.update_model_from_scenarios)
        self.revenue_params.apply_btn.clicked.connect(self.sync_yearly_table)
        # Чтобы названия товаров передавались в новую таблицу
        self.revenue_params.products_changed.connect(self.volume_growth.update_product_names)
        self.revenue_params.products_changed.connect(self.price_growth.update_product_names)
        self.revenue_params.products_changed.connect(self.sales_capacity.update_product_names)

        # В MainWindow.__init__ или там, где создаются виджеты:
        self.price_growth.data_changed.connect(self.sync_yearly_table)
        self.volume_growth.data_changed.connect(self.sync_yearly_table)
        self.sales_capacity.data_changed.connect(self.sync_yearly_table)

        for le in self.seasonality_widget.inputs:
            le.editingFinished.connect(self.sync_yearly_table)
        # В MainWindow.setup_signals
        for le in self.monthly_rate_widget.cells.values():
            le.editingFinished.connect(self.sync_yearly_table)
        self.monthly_rate_widget.data_confirmed.connect(self.sync_yearly_table)
        # Связываем нажатие кнопки в виджете продаж активов с общим расчетом
        self.asset_sales_widget.data_confirmed.connect(self.sync_yearly_table)
        self.monthly_rate_widget.data_confirmed.connect(self.sync_yearly_table)
        for le in self.monthly_rate_widget.cells.values():
            le.editingFinished.connect(self.sync_yearly_table)
    def _on_project_timing_changed(self, *_args):
        # Блокируем главный расчет, чтобы не считать 5 раз подряд
        self.blockSignals(True)
        try:
            self.update_capex_horizon_limit(self.input_widget.hor_le.text())
            self.asset_sales_widget.refresh_table()
            self.refresh_taxes_columns()
            self.refresh_capm_columns()
            self.refresh_macro_columns()
            self.refresh_sales_capacity_columns()
            self.refresh_volume_growth_columns()
            self.refresh_price_growth_columns()
            self.credit_widget.calculate_loan()
        finally:
            self.blockSignals(False)
            # Вызываем расчет ОДИН раз после всех обновлений
            self.sync_yearly_table()

    def run_initial_calculations(self):
        # Блокируем сигналы, чтобы промежуточные изменения не вызывали sync_yearly_table 10 раз
        self.blockSignals(True)
        try:
            self.revenue_params.accept_data()
            self.opex_widget.accept_data()
            self.refresh_macro_columns()
            self.refresh_taxes_columns()
            self.refresh_capm_columns()
            self.update_wacc_values()
        finally:
            # Разблокируем и вызываем ОДИН финальный расчет
            self.blockSignals(False)
            self.sync_yearly_table()
    def update_capex_horizon_limit(self, text):
        try:
            if text and text.isdigit():
                if hasattr(self, 'capex_params'):
                    self.capex_params.set_project_horizon(int(text))
        except:
            pass

    def refresh_sales_capacity_columns(self):
        try:
            self.sales_capacity.update_years(self.input_widget.year_cb.currentText(),
                                             self.input_widget.month_cb.currentIndex(),
                                             self.input_widget.dur_cb.currentText() or "1")
        except:
            pass

    def refresh_volume_growth_columns(self):
        try:
            # Передаем напрямую 60 (или сколько введено в поле горизонта)
            horizon = self.input_widget.hor_le.text() or "12"
            self.volume_growth.update_years(
                self.input_widget.year_cb.currentText(),
                self.input_widget.month_cb.currentIndex(),
                horizon
            )
        except Exception as e:
            print(f"Ошибка обновления лет объема: {e}")

    def refresh_price_growth_columns(self):
        try:
            # Аналогично для цены
            horizon = self.input_widget.hor_le.text() or "12"
            self.price_growth.update_years(
                self.input_widget.year_cb.currentText(),
                self.input_widget.month_cb.currentIndex(),
                horizon
            )
        except Exception as e:
            print(f"Ошибка обновления лет цены: {e}")
    def refresh_capm_columns(self):
        try:
            y, m = self.input_widget.year_cb.currentText(), self.input_widget.month_cb.currentIndex()
            d = self.input_widget.dur_cb.currentText() or "1"
            self.capm_widget.update_years(y, m, d)
            self.wacc_widget.update_years(y, m, d)
        except:
            pass

    def refresh_macro_columns(self):
        try:
            y, m = int(self.input_widget.year_cb.currentText()), self.input_widget.month_cb.currentIndex()
            dt = self.input_widget.dur_cb.currentText()
            d = int(''.join(filter(str.isdigit, dt)))
            self.inflation_widget.update_years(y, m, d)
        except:
            pass

    def refresh_taxes_columns(self):
        try:
            self.taxes_widget.update_years(self.input_widget.year_cb.currentText(),
                                           self.input_widget.month_cb.currentIndex(),
                                           self.input_widget.dur_cb.currentText() or "1")
        except:
            pass

    def _get_loan_body_schedule(self):
        schedule = {}
        try:
            loan_amount = float(self.credit_widget.inputs["amount"].text().replace(' ', '').replace(',', '.'))
            loan_rate = float(self.credit_widget.inputs["rate"].text().replace(',', '.'))
            loan_term = int(self.credit_widget.inputs["term"].text())
            monthly_rate = (loan_rate / 100) / 12

            for month in range(1, loan_term + 1):
                principal = abs(self.credit_widget.numpy_equivalent_ppmt(monthly_rate, month, loan_term, loan_amount))
                schedule[month] = principal
        except:
            pass
        return schedule

    def _build_monthly_cashflow_data(self, months_per_year, start_month):
        total_months = sum(months_per_year.values())
        calendar_years = list(months_per_year.keys())

        m_rev = [0.0] * total_months
        m_opex = [0.0] * total_months
        m_amort = [0.0] * total_months
        m_interest = [self.credit_widget.get_interest_schedule().get(m, 0.0) for m in range(1, total_months + 1)]
        m_capex = [0.0] * total_months
        m_asset_sales = [0.0] * total_months
        m_net_profit = [0.0] * total_months
        m_op_cf = [0.0] * total_months
        m_inv_cf = [0.0] * total_months
        products_data = self.revenue_params.get_products_data()
        k_scenario = self.scenario_widget.get_income_multiplier()
        k_scenario_exp = self.scenario_widget.get_expense_multiplier()
        inflation_map = self.inflation_widget.get_inflation_map()
        base_opex = self.opex_widget.get_base_opex()
        seasonal_factors = self.seasonality_widget.get_factors()
        sales_capacity_data = self.sales_capacity.get_data()
        volume_growth_data = self.volume_growth.get_data()
        price_growth_data = self.price_growth.get_data()
        capex_data = self.capex_params.get_capex_full_data()
        tax_rates_map = self.taxes_widget.get_tax_rates_by_year()
        vat_map = self.taxes_widget.get_vat_rates_by_year()
        asset_sales_data = self.asset_sales_widget.get_data()

        for asset in capex_data:
            month = int(asset.get('month', 0))
            # Защита от выхода за пределы горизонта
            if 1 <= month <= total_months:
                m_capex[month - 1] += asset.get('cost', 0.0)

            term = int(asset.get('term', 0))
            if term > 0 and 1 <= month <= total_months:
                monthly_amort = asset.get('cost', 0.0) / term
                for amort_month in range(month, min(month + term, total_months + 1)):
                    # Защита индекса амортизации
                    if 1 <= amort_month <= total_months:
                        m_amort[amort_month - 1] += monthly_amort

        for sale in asset_sales_data:
            month = int(sale.get('month', 0))
            if 1 <= month <= total_months:
                m_asset_sales[month - 1] += sale.get('income', 0.0)

        abs_m = 0
        curr_m_idx = start_month
        for year in calendar_years:
            year_str = str(year)
            inf_m = inflation_map.get(year_str, 0.0) / 12
            raw_tax = tax_rates_map.get(year_str, 15)
            tax_rate = float(str(raw_tax).replace(',', '.'))
            if tax_rate > 1: tax_rate /= 100
            vat_rate = vat_map.get(year_str, 0.0)
            
            # БЕЗОПАСНОЕ ПОЛУЧЕНИЕ КОЭФФИЦИЕНТОВ МОЩНОСТИ
            raw_cap = sales_capacity_data.get(year_str, [])
            num_prods = len(products_data)
            cap_ks = raw_cap + [1.0] * (num_prods - len(raw_cap))

            raw_v_growth = volume_growth_data.get(year_str, [])
            # Заполняем нулями, если для какого-то продукта данные не введены
            v_growth_ks = raw_v_growth + [0.0] * (num_prods - len(raw_v_growth))

            raw_p_growth = price_growth_data.get(year_str, [])
            p_growth_ks = raw_p_growth + [0.0] * (num_prods - len(raw_p_growth))

            for _ in range(months_per_year[year]):
                seasonal_k = seasonal_factors[(curr_m_idx - 1) % len(seasonal_factors)]
                revenue = 0.0

                for p_idx, prod in enumerate(products_data):
                    v_growth = (v_growth_ks[p_idx] / 100) / 12

                    p_growth = (p_growth_ks[p_idx] / 100) / 12

                    volume = prod['base_vol'] * (1 + v_growth) ** abs_m * cap_ks[p_idx] * seasonal_k
                    price = prod['base_price'] * (1 + p_growth) ** abs_m
                    revenue += volume * price

                m_rev[abs_m] = revenue * k_scenario
                m_opex[abs_m] = base_opex * (1 + inf_m) ** abs_m * k_scenario_exp

                ebitda = m_rev[abs_m] - m_opex[abs_m]
                ebit = ebitda - m_amort[abs_m]
                ebt = ebit - m_interest[abs_m]

                # Налог (УСН/Прибыль) — в Excel он всегда округлен
                tax = round(ebitda * tax_rate, 2) if ebitda > 0 else 0.0
                m_net_profit[abs_m] = ebt - tax

                vat_sales = m_rev[abs_m] * vat_rate
                vat_deduction = (m_capex[abs_m] + m_opex[abs_m]) * vat_rate
                raw_vat = vat_sales - vat_deduction

                vat_to_pay = max(0.0, raw_vat)
                overpayment = abs(min(0.0, raw_vat))
                total_taxes = tax + vat_to_pay

                m_op_cf[abs_m] = m_rev[abs_m] - m_opex[abs_m] - total_taxes
                m_inv_cf[abs_m] = m_asset_sales[abs_m] - m_capex[abs_m]

                abs_m += 1
                curr_m_idx = 1 if curr_m_idx == 12 else curr_m_idx + 1

        return {
            'rev': m_rev,
            'net_profit': m_net_profit,
            'op_cf': m_op_cf,
            'inv_cf': m_inv_cf,
        }

    def sync_yearly_table(self):
        try:
            if not hasattr(self, 'op_cf_widget') or not hasattr(self, 'yearly_results'):
                return

            # 1. Получаем базовые параметры
            try:
                start_month = self.input_widget.month_cb.currentIndex() + 1
                start_year = int(self.input_widget.year_cb.currentText())
                horizon = int(self.input_widget.hor_le.text())
            except:
                start_month, start_year, horizon = 1, 2026, 60

                # --- ВОТ ЭТО НУЖНО ДОБАВИТЬ ПЕРЕД ВЫЗОВОМ ---
                # Вытаскиваем данные из ваших виджетов роста
            volume_growth_data = self.volume_growth.get_data()
            price_growth_data = self.price_growth.get_data()

            months_struct = self.yearly_results.generate_columns(start_month, start_year, horizon)

            revenue_by_years = self.yearly_results.update_data(
                months_per_year=months_struct,
                products_data=self.revenue_params.get_products_data(),
                k_scenario=self.scenario_widget.get_income_multiplier(),
                k_scenario_exp=self.scenario_widget.get_expense_multiplier(),
                inflation_map=self.inflation_widget.get_inflation_map(),
                base_opex=self.opex_widget.get_base_opex(),
                seasonal_factors=self.seasonality_widget.get_factors(),
                start_month=start_month,
                sales_capacity_data=self.sales_capacity.get_data(),
                volume_growth_data=volume_growth_data,  # ДОБАВИТЬ ЭТО
                price_growth_data=price_growth_data,  # ДОБАВИТЬ ЭТО
                capex_data=self.capex_params.get_capex_full_data(),
                loan_schedule=self.credit_widget.get_interest_schedule(),
                tax_rates_map=self.taxes_widget.get_tax_rates_by_year()
            )

            monthly_cf = self._build_monthly_cashflow_data(months_struct, start_month)
            monthly_op = monthly_cf['op_cf']
            monthly_inv = monthly_cf['inv_cf']
            free_cf_monthly = [op + inv for op, inv in zip(monthly_op, monthly_inv)]

            # 3. Сбор данных из основной таблицы
            rev_list, opex_list, tax_list, net_profit = [], [], [], []

            # Проверяем, что в таблице достаточно строк (минимум 9 для индекса 8)
            if self.yearly_results.table.rowCount() >= 9:
                num_years = len(months_struct)
                for c in range(num_years):
                    col_idx = c + 2
                    # Проверяем наличие элемента перед парсингом, чтобы избежать ошибки
                    item_rev = self.yearly_results.table.item(0, col_idx)
                    item_opex = self.yearly_results.table.item(1, col_idx)
                    item_tax = self.yearly_results.table.item(7, col_idx)
                    item_np = self.yearly_results.table.item(8, col_idx)

                    rev_list.append(self._parse_table_val(item_rev))
                    opex_list.append(self._parse_table_val(item_opex))
                    tax_list.append(self._parse_table_val(item_tax))
                    net_profit.append(self._parse_table_val(item_np))
            else:
                # Если строк мало, заполняем нулями, чтобы не падать
                rev_list = [0.0] * len(months_struct)
                opex_list = [0.0] * len(months_struct)
                tax_list = [0.0] * len(months_struct)
                net_profit = [0.0] * len(months_struct)

            # 4. Обновление Операционного ДП
            self.op_cf_widget.update_data(
                months_per_year=months_struct,
                yearly_basic_data={'rev': rev_list, 'opex': opex_list, 'tax': tax_list},
                capex_data=self.capex_params.get_capex_full_data(),
                vat_map=self.taxes_widget.get_vat_rates_by_year()
            )

            # Обновление Инвестиционного ДП
            if hasattr(self, 'inv_cf_widget'):
                self.inv_cf_widget.update_data(
                    months_per_year=months_struct,
                    capex_data=self.capex_params.get_capex_full_data(),
                    asset_sales_data=self.asset_sales_widget.get_data()
                )

            if hasattr(self, 'fin_cf_widget'):
                self.fin_cf_widget.update_data(
                    months_per_year=months_struct,
                    funding_data=self.funding_widget.get_funding_data(),
                    net_profit_monthly=monthly_cf['net_profit'],
                    op_cf_monthly=monthly_cf['op_cf'],
                    inv_cf_monthly=monthly_cf['inv_cf'],
                    interest_schedule=self.credit_widget.get_interest_schedule(),
                    body_schedule=self._get_loan_body_schedule(),
                )

            if hasattr(self, 'prediction_cf_widget'):
                self.prediction_cf_widget.update_data(
                    months_per_year=months_struct,
                    op_cf_monthly=monthly_cf['op_cf'],
                    inv_cf_monthly=monthly_cf['inv_cf'],
                    funding_data=self.funding_widget.get_funding_data(),
                    net_profit_monthly=monthly_cf['net_profit'],
                    interest_schedule=self.credit_widget.get_interest_schedule(),
                    body_schedule=self._get_loan_body_schedule(),
                    monthly_rate_widget=self.monthly_rate_widget
                )

            # Обновление показателей эффективности
            if hasattr(self, 'efficiency_widget'):
                funding = self.funding_widget.get_funding_data()
                only_inv = funding.get("investments", 0.0)

                # Получаем ставку дисконтирования из WACC (переводим из % в доли)
                try:
                    current_wacc = float(self.wacc_widget.wacc_label.text().replace('%', '')) / 100
                except:
                    current_wacc = 0.15  # Значение по умолчанию

                # Получаем желаемый срок окупаемости
                try:
                    target_pp = int(self.input_widget.hor_le.text())
                except:
                    target_pp = 36

                disc_cf_monthly = getattr(self.prediction_cf_widget, 'discounted_flows', [])
                rev_data = monthly_cf.get('rev', [])

                # Внутри sync_yearly_table (MainWindow)
                self.efficiency_widget.update_metrics(
                    net_profit_monthly=monthly_cf['net_profit'],
                    free_cf_monthly=free_cf_monthly,
                    discounted_cf_monthly=disc_cf_monthly,
                    investments=only_inv,
                    discount_rate=current_wacc,
                    target_pp_months=target_pp,
                    revenue_monthly=rev_data,
                    start_month=start_month,  # Передаем месяц
                    months_struct=months_struct  # Передаем структуру (важно!)
                )

            # Обновление накопленного ДП
            if hasattr(self, 'accumulated_cf_widget'):
                funding = self.funding_widget.get_funding_data()
                only_inv = funding.get("investments", 0.0)
                disc_cf_monthly = getattr(self.prediction_cf_widget, 'discounted_flows', [])

                self.accumulated_cf_widget.update_data(
                    months_struct,
                    free_cf_monthly,
                    disc_cf_monthly,
                    only_inv
                )
        except Exception as e:
            print(f"ОШИБКА В РАСЧЕТАХ: {e}\n{traceback.format_exc()}")
    def _parse_table_val(self, item):
        """Вспомогательный метод для очистки текста из ячеек"""
        if not item: return 0.0
        try:
            return float(item.text().replace(' ', '').replace(',', '.'))
        except:
            return 0.0
    def update_model_from_scenarios(self):
        self.sync_yearly_table()

    def update_wacc_values(self):
        # 1. Сначала пересчитываем годовой WACC
        if hasattr(self, 'wacc_widget'):
            self.wacc_widget.refresh_calculations()

        # 2. Затем обновляем структуру и считаем месячную ставку на базе нового WACC
        if hasattr(self, 'monthly_rate_widget'):
            # Обновляем года (если сменился горизонт)
            self.monthly_rate_widget.update_data()
            # Принудительно запускаем математический расчет
            self.monthly_rate_widget.refresh_calculations()

    def show_app_info(self):
        QMessageBox.information(self, "Информация", "Финансовая модель проекта.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    sys.exit(app.exec())
