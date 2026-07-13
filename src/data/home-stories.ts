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
      'В общей папке появляется anonymous.txt: кто-то предупреждает, что хронологию могут тихо поправить до открытия витрины.',
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
      'В почте появляются сообщения о блокировке архива и отчетах с камеры. Ссылки и вложения открывать нельзя.',
    question: 'Что можно установить о письме, не запуская потенциально опасное содержимое?',
    tool: 'Заголовки, URL, домены, IP, вложения и понятные правила риска.',
    outcome: 'Отчет: вердикт, баллы и причины для каждого письма.',
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
      'Отдельные следы нужно собрать в одну доску: люди, файлы, письма, заметки и уверенность в каждой улике.',
    question: 'Как сохранить целостное состояние дела и продолжить работу позже?',
    tool: 'Классы, dataclass, композиция и сохранение в JSON.',
    outcome: 'Доска расследования с поиском и заметками.',
    artifact: 'case_seed.json',
    command: 'python investigation_system.py',
    color: '#9fb7ff',
    tone: '#dce4f8',
  },
  'I-06': {
    kicker: 'Гипотезы и решение',
    summary:
      'До открытия остается меньше двух часов. Результаты пяти дел нужно превратить в осторожный и объяснимый вердикт.',
    question: 'Какая версия лучше объясняет следы и какое действие безопасно?',
    tool: 'Хронология, поддержка, противоречия и явные ограничения вывода.',
    outcome: 'Рейтинг гипотез, вердикт и план действий.',
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
    tool: 'Стратифицированный split, DummyClassifier, масштабирование и k-NN.',
    outcome: '100% на train не подтверждают качество на новых цветках.',
    artifact: 'case-01.ipynb',
    command: 'stratified holdout → scaled k-NN',
    color: '#8da2ff',
    tone: '#17234d',
    dataset: 'Iris · 150 строк',
    claim: '«Точность модели — 100%»',
    diagnostic: 'scatter',
    metrics: [
      { label: 'train', value: '100%', width: 100 },
      { label: 'holdout', value: '< 100%', width: 90 },
      { label: 'baseline', value: 'ниже', width: 44 },
    ],
  },
  'II-02': {
    kicker: 'Аудит утечки',
    summary:
      'В Titanic-модели обнаруживаются признаки boat и body — сведения, появившиеся только после исхода события.',
    question: 'Какие признаки реально доступны в момент прогноза?',
    tool: 'Аудит доступности, imputer, OneHotEncoder и честный pipeline.',
    outcome: 'Заголовочный результат зависит от информации из будущего.',
    artifact: 'case-02.ipynb',
    command: 'honest pipeline ↔ leaky pipeline',
    color: '#91b8ff',
    tone: '#16264e',
    dataset: 'Titanic · замороженный снимок',
    claim: '«Модель знает, кто выживет»',
    diagnostic: 'leakage',
    metrics: [
      { label: 'leaky', value: 'выше', width: 96 },
      { label: 'honest', value: 'ниже', width: 73 },
      { label: 'boat/body', value: 'после', width: 100 },
    ],
  },
  'II-03': {
    kicker: 'Цена ошибок',
    summary:
      'Тот же Titanic отвечает уже не на вопрос «кто точнее», а на вопрос «какую ошибку мы можем себе позволить».',
    question: 'Как выбрать порог до открытия внешнего holdout?',
    tool: 'Cross-validation, OOF-прогнозы, precision, recall, F1 и срезы.',
    outcome: 'Accuracy скрывала цену ошибок и неравномерность по группам.',
    artifact: 'case-03.ipynb',
    command: 'recall ≥ .85 · flagged ≤ 55%',
    color: '#7fb4ff',
    tone: '#14264a',
    dataset: 'Titanic · честный pipeline',
    claim: '«Высокая accuracy достаточна»',
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
      'California Housing переносит аудит в регрессию: случайный split и новые регионы оказываются разными задачами.',
    question: 'Соответствует ли разбиение обещанию оценки в незнакомом регионе?',
    tool: 'MAE, RMSE, R², остатки и группировка holdout по территории.',
    outcome: 'Случайный split поддерживает интерполяцию, но не обещание новых регионов.',
    artifact: 'case-04.ipynb',
    command: 'random split ↔ region holdout',
    color: '#6f9dff',
    tone: '#17254a',
    dataset: 'California Housing',
    claim: '«Оценивает жилье в новых регионах»',
    diagnostic: 'map',
    metrics: [
      { label: 'random', value: 'optimistic', width: 88 },
      { label: 'region', value: 'harder', width: 60 },
      { label: 'errors', value: 'structured', width: 76 },
    ],
  },
  'II-05': {
    kicker: 'Ошибки по классам',
    summary:
      'На Digits высокая общая accuracy уступает место вопросу: какие цифры модель путает снова и снова?',
    question: 'Какие классы проваливаются за красивой средней метрикой?',
    tool: 'k-NN, RBF SVM, GridSearchCV, macro-F1 и галерея ошибок.',
    outcome: 'Монтаж успехов скрывал повторяемые ошибки отдельных классов.',
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
      'В финале у каждого изображения есть источник, вариант и партия сканера. Связанные снимки пересекают границы vendor split.',
    question: 'Что останется от результата после группировки и новой партии C?',
    tool: 'StratifiedGroupKFold, batch C, bootstrap-интервал и model card.',
    outcome: 'Закупка приостановлена до независимой проверки на целевой задаче.',
    artifact: 'case-06.ipynb',
    command: 'vendor → grouped CV → batch C',
    color: '#b38cff',
    tone: '#24204f',
    dataset: 'Synthetic Digits stress test',
    claim: '«Benchmark доказывает готовность»',
    diagnostic: 'groups',
    metrics: [
      { label: 'vendor', value: '≈ 1.00', width: 100 },
      { label: 'grouped', value: '≈ .89', width: 89 },
      { label: 'batch C', value: '≈ .65', width: 65 },
    ],
  },
};
