from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка: Руководство по финансовой модели")
        self.setMinimumSize(850, 600)

        layout = QVBoxLayout(self)

        # Используем QTextBrowser для поддержки HTML и прокрутки
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)  # Чтобы можно было кликать по ссылкам, если добавите

        # Стилизация текста через HTML/CSS
        help_html = """
        <style>
            body { font-family: 'Times New Roman'; line-height: 1.5; color: #333; }
            h1 { color: #2E86C1; border-bottom: 2px solid #2E86C1; }
            h2 { color: #2874A6; margin-top: 20px; }
            .section { margin-bottom: 15px; }
            .highlight { font-weight: bold; color: #D35400; }
            ul { margin-left: 20px; }
            li { margin-bottom: 8px; }
            .note { background-color: #EBF5FB; padding: 10px; border-left: 5px solid #5DADE2; }
        </style>

        <h1>Инструкция по работе с финансовой моделью</h1>

        <div class='section'>
            <p>Данная модель предназначена для комплексного моделирования инвестиционного проекта, 
            начиная с <b>декабря 2026 года</b>. Она позволяет оценить целесообразность вложений через 
            ключевые финансовые метрики.</p>
        </div>

        <h2>1. Лист «Входные данные»</h2>
        <p>На данном листе задаются основные параметры, используемые в расчётах модели:</p>
        <ul>
            <li><span class='highlight'>Налоги</span> — настройка ставок налога на прибыль/УСН и НДС для каждого года проекта.</li>
            <li><span class='highlight'>Ставка дисконтирования</span> — процентная ставка, используемая для приведения будущих денежных потоков к текущей стоимости (WACC).</li>
            <li><span class='highlight'>Параметры инфляции</span> — учитывают изменение цен на операционные расходы во времени.</li>
            <li><span class='highlight'>Параметры кредитования</span> — расчет графиков погашения (тело + проценты).</li>
            <li><span class='highlight'>База товаров</span> — ввод цен, объемов и темпов их роста.</li>
            <li><span class='highlight'>Капитальные затраты (CAPEX)</span> — инвестиции в основные средства и их амортизация.</li>
        </ul>

        <div class='note'>
            <b>Важно:</b> Модель автоматически пересчитывает все показатели при изменении любого из параметров в реальном времени.
        </div>

        <h2>2. Методы и подходы</h2>
        <p>Финансовая модель учитывает следующие инструменты анализа:</p>
        <ol>
            <li><b>Влияние инфляции:</b> автоматическая корректировка затрат по годам.</li>
            <li><b>Сценарный анализ:</b> возможность выбора "Базового", "Оптимистичного" или "Пессимистичного" сценариев, которые применяют коэффициенты к выручке и расходам.</li>
            <li><b>Коэффициент сезонности:</b> позволяет задать неравномерность продаж по месяцам (например, пик в декабре).</li>
            <li><b>Анализ чувствительности:</b> оценка того, как изменение одной переменной влияет на итоговый NPV проекта.</li>
        </ol>

        <h2>3. Порядок заполнения</h2>
        <p>Для корректного расчета рекомендуется следовать порядку вкладок (1 -> 2 -> 3...). 
        Убедитесь, что в разделе <i>«Финансирование»</i> сумма долей собственного и заемного капитала составляет 100%.</p>
        """

        self.browser.setHtml(help_html)
        layout.addWidget(self.browser)

        # Кнопка закрытия
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)