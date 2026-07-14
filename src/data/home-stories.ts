export interface HomeMetric {
  label: string;
  value: string;
  width: number;
}

export interface HomeStoryDetail {
  kicker: string;
  summary: string;
  question: string;
  tool: string;
  outcome: string;
  artifact: string;
  command: string;
  color: string;
  tone: string;
  dataset?: string;
  claim?: string;
  diagnostic?: 'scatter' | 'leakage' | 'threshold' | 'map' | 'digits' | 'groups';
  metrics?: HomeMetric[];
}

export const homeStoryDetails: Record<string, HomeStoryDetail> = {
  'I-01': {
    kicker: 'Текстовый отпечаток',
    summary:
      'В общей папке появляется anonymous.txt: кто-то предупреждаёт, что хронологию могут тихо поправить до открытия витрины.',
    question: 'Кто оставил предупреждение и что он знает о ночной правке?',
    tool: 'Слова, пунктуация, частоты и сравнение привычек письма.',
    outcome: 'Таблица кандидатов с объяснимыми признаками текста.',
    artifact: 'anonymous.txt',
    command: 'python anonymous_letter.py',
    color: '#20d3bd',
    tone: '#f3e1b8',
  },
  'I-02': {
    kicker: 'Утечки и подмены',
    summary:
      'В черновике экскурсии появляются фрагменты закрытой описи. Похожесть еще не доказывает утечку — ее нужно измерить.',
    question: 'Какие пары документов подозрительно похожи, а где совпадение объяснимо?',
    tool: 'N-граммы, множества и сортировка пар по силе совпадения.',
    outcome: 'Рейтинг пар с примером общей фразы.',
    artifact: 'report_*.txt',
    command: 'python copy_paste_detector.py',
    color: '#f2b84b',
    tone: '#f7e7c7',
  },
  'I-03': {
    kicker: 'Разбор писем',
    summary:
      'В почте появляются сообщения о блокировке архива и отчётах с камеры. Ссылки и вложения открывать нельзя.',
    question: 'Что можно установить о письме, не запуская потенциально опасное содержимое?',
    tool: 'Заголовки, URL, домены, IP, вложения и понятные правила риска.',
    outcome: 'Отчёт: вердикт, баллы и причины для каждого письма.',
    artifact: 'message_*.eml',
    command: 'python phishing_email.py',
    color: '#ee6f5e',
    tone: '#f4d8ce',
  },
  'I-04': {
    kicker: 'Файлы и хеши',
    summary:
      'После ночного сигнала в рабочей папке лежат похожие копии фотоиндекса, журнал доступа и две версии хронологии.',
    question: 'Какие файлы совпадают полностью и что действительно изменилось?',
    tool: 'pathlib, SHA-256, временные метки и JSON-манифест.',
    outcome: 'Группы дублей и проверяемый список изменений.',
    artifact: 'secret_folder/',
    command: 'python secret_folder_archive.py',
    color: '#a7d56f',
    tone: '#e4edca',
  },
  'I-05': {
    kicker: 'Модель расследования',
    summary:
      'Создайте классы для людей, файлов, писем и заметок, объедините объекты в Investigation и сохраните данные дела в JSON.',
    question: 'Как загрузить case_seed.json, выполнить поиск, добавить заметку и сохранить результат?',
    tool: 'Классы, dataclass, композиция и сохранение в JSON.',
    outcome: 'case_report.json с участниками, уликами и заметками.',
    artifact: 'case_seed.json',
    command: 'python investigation_system.py',
    color: '#9fb7ff',
    tone: '#dce4f8',
  },
  'I-06': {
    kicker: 'Гипотезы и решение',
    summary:
      'Программа загрузит evidence_bundle.json, построит хронологию, вычислит score каждой гипотезы и сформирует итоговый отчёт.',
    question: 'Какие улики поддерживают или опровергают каждую гипотезу и какой score она получает?',
    tool: 'Хронология, поддержка, противоречия и явные ограничения вывода.',
    outcome: 'verdict.json с хронологией, рейтингом гипотез, решением и планом действий.',
    artifact: 'evidence_bundle.json',
    command: 'python final_verdict.py',
    color: '#d49cff',
    tone: '#eadcf4',
  },
  'II-01': {
    kicker: 'Проверка обобщения',
    summary:
      'Iris становится вступительным экзаменом: воспроизводим заявленные 100% и проверяем, относятся ли они к новым данным.',
    question: 'Что именно измеряет демонстрационная цифра поставщика?',
    tool: 'Стратифицированное разбиение, DummyClassifier, масштабирование и k-NN.',
    outcome: '100% на обучающей выборке не подтверждают качество на новых цветках.',
    artifact: 'case-01.ipynb',
    command: 'стратифицированная проверка → k-NN с масштабированием',
    color: '#8da2ff',
    tone: '#17234d',
    dataset: 'Iris · 150 строк',
    claim: '«Точность модели — 100%»',
    diagnostic: 'scatter',
    metrics: [
      { label: 'обучение', value: '100%', width: 100 },
      { label: 'тест', value: '< 100%', width: 90 },
      { label: 'базовая модель', value: 'ниже', width: 44 },
    ],
  },
  'II-02': {
    kicker: 'Аудит утечки',
    summary:
      'В Titanic-модели обнаруживаются признаки boat и body — сведения, появившиеся только после исхода события.',
    question: 'Какие признаки реально доступны в момент прогноза?',
    tool: 'Аудит доступности, SimpleImputer, OneHotEncoder и конвейер без утечки.',
    outcome: 'Заявленная точность зависит от информации из будущего.',
    artifact: 'case-02.ipynb',
    command: 'без утечки ↔ с утечкой',
    color: '#91b8ff',
    tone: '#16264e',
    dataset: 'Titanic · замороженный снимок',
    claim: '«Модель знает, кто выживет»',
    diagnostic: 'leakage',
    metrics: [
      { label: 'с утечкой', value: 'выше', width: 96 },
      { label: 'без утечки', value: 'ниже', width: 73 },
      { label: 'boat/body', value: 'после', width: 100 },
    ],
  },
  'II-03': {
    kicker: 'Цена ошибок',
    summary:
      'На данных Titanic вы получите OOF-прогнозы, сравните precision, recall и F1, а затем выберете порог с recall ≥ 0.85 и долей отмеченных строк не выше 55%.',
    question: 'Как выбрать порог до оценки на внешней тестовой выборке?',
    tool: 'Кросс-валидация, OOF-прогнозы, precision, recall, F1 и срезы.',
    outcome: 'Таблица сравнения моделей, выбранный порог и метрики по группам.',
    artifact: 'case-03.ipynb',
    command: 'recall ≥ .85 · flagged ≤ 55%',
    color: '#7fb4ff',
    tone: '#14264a',
    dataset: 'Titanic · конвейер без утечки',
    claim: '«Высокой доли правильных ответов достаточно»',
    diagnostic: 'threshold',
    metrics: [
      { label: 'recall', value: '≥ .85', width: 85 },
      { label: 'flagged', value: '≤ 55%', width: 55 },
      { label: 'precision', value: 'max', width: 72 },
    ],
  },
  'II-04': {
    kicker: 'География оценки',
    summary:
      'California Housing переносит аудит в регрессию: случайное разбиение и проверка на новых регионах оказываются разными задачами.',
    question: 'Соответствует ли разбиение обещанию оценки в незнакомом регионе?',
    tool: 'MAE, RMSE, R², остатки и географическая отложенная выборка.',
    outcome: 'Случайное разбиение проверяет интерполяцию, но не подтверждаёт качество в новых регионах.',
    artifact: 'case-04.ipynb',
    command: 'случайное разбиение ↔ новый регион',
    color: '#6f9dff',
    tone: '#17254a',
    dataset: 'California Housing',
    claim: '«Оценивает жильё в новых регионах»',
    diagnostic: 'map',
    metrics: [
      { label: 'случайно', value: 'лучше', width: 88 },
      { label: 'по регионам', value: 'хуже', width: 60 },
      { label: 'ошибки', value: 'не случайны', width: 76 },
    ],
  },
  'II-05': {
    kicker: 'Ошибки по классам',
    summary:
      'На Digits вы сравните k-NN и RBF SVM, посчитаете recall для каждой цифры и покажете ошибочно классифицированные изображения.',
    question: 'У каких цифр recall ниже и какие пары классов модель путает чаще всего?',
    tool: 'k-NN, RBF SVM, GridSearchCV, macro-F1 и галерея ошибок.',
    outcome: 'Метрики по классам, матрица ошибок и галерея неверных предсказаний.',
    artifact: 'case-05.ipynb',
    command: 'k-NN ↔ RBF SVM · macro-F1',
    color: '#9d8cff',
    tone: '#1d214c',
    dataset: 'Digits · изображения 8×8',
    claim: '«Почти все цифры распознаны»',
    diagnostic: 'digits',
    metrics: [
      { label: 'accuracy', value: 'high', width: 94 },
      { label: 'macro-F1', value: 'check', width: 87 },
      { label: 'class recall', value: 'uneven', width: 66 },
    ],
  },
  'II-06': {
    kicker: 'Независимый экзамен',
    summary:
      'Поставщик разделил варианты одного source_id между обучающей и тестовой выборками. Вы повторите оценку с StratifiedGroupKFold и проверите зафиксированную модель на партии C.',
    question: 'Как меняется macro-F1 после группировки по source_id и проверки на партии C?',
    tool: 'StratifiedGroupKFold, партия C, бутстреп-интервал и карточка модели.',
    outcome: 'Закупка приостановлена до независимой проверки на целевой задаче.',
    artifact: 'case-06.ipynb',
    command: 'поставщик → группы → партия C',
    color: '#b38cff',
    tone: '#24204f',
    dataset: 'Digits · синтетический стресс-тест',
    claim: '«Контрольный тест доказывает готовность»',
    diagnostic: 'groups',
    metrics: [
      { label: 'поставщик', value: '≈ 1.00', width: 100 },
      { label: 'по группам', value: '≈ .89', width: 89 },
      { label: 'партия C', value: '≈ .65', width: 65 },
    ],
  },
};
