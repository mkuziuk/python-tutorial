# Project guidance

This repository contains a Russian-language project tutorial for Python and
classical machine learning. The Astro/Starlight site is in `src/`, Part I uses
four standalone Python projects under `projects/case-*`, and Part II uses six
Jupyter projects under `projects/part-2/case-*`.

Keep lesson pages, solution pages, downloadable projects, and generated assets
consistent. Rebuild downloadable ZIP files and their checksums with
`pnpm build:archives`. Do not change story facts established in `PLOT.md` or
`PLOT_PART_2.md`, and follow `EDITORIAL_GUIDE_RU.md` for Russian terminology
and tone.

Part I solution scripts are canonical for the four generated solution pages;
run `pnpm build:part1-solutions` after changing them. The investigations pass
JSON artifacts from I-01 through I-04. Run `pnpm build:part1-artifacts` after
changing a Part I schema, finding, fixture, or solution that affects the handoff.

## Comments in tutorial code

- Document every meaningful statement either in an adjacent comment/docstring
  or in the lesson prose immediately after its listing. A learner should never
  have to infer a variable's role, the shape of a returned value, or why a
  branch exists. Obvious punctuation and syntax do not need separate comments.
- State the direct effect of the adjacent line or block and name the relevant
  function, variable, class, or value when that makes the comment clearer.
- Prefer a positive statement such as “`urlparse` separates the URL into
  components” over explaining the operation through what it does not do.
- Put broader caveats about security, probability, production limitations, or
  interpretation in the surrounding prose unless they are required to use the
  code correctly.
- Do not restate obvious syntax. Explain a reason, invariant, unit, assumption,
  data boundary, or non-obvious library behavior.
- Keep duplicated comments synchronized across lesson pages, solution pages,
  scripts, and notebooks. Preserve learner/solution boundaries in Part II.

## Объяснение и учебная проза по образцу «Python для хакеров»

Для новых и существенно переработанных уроков используйте повторяющийся цикл
из русского издания книги Ли Вогана:

> конкретная задача → обоснованный этап → небольшой листинг →
> разбор данных и решений → наблюдаемый результат → интерпретация →
> следующий этап.

### До кода

- Сначала назовите практическую задачу, входные материалы, ограничения и
  проверяемый результат. Формулируйте их измеримо: какие файлы будут прочитаны,
  какие объекты найдены, какая таблица или модель получена и куда сохранён
  артефакт.
- После постановки задачи кратко изложите стратегию как цепочку преобразований.
  В главе 1 поиск разбит на исходные вероятности, результат поиска и обновление
  вероятностей; в главе 2 анализ авторства — на загрузку строк, токенизацию и
  пять отдельных сравнений (PDF/печ. с. 29–31, 63).
- Перед каждым листингом объясните один текущий этап: что он принимает, что
  делает и какое значение, структуру данных или побочный эффект создаёт.
- Связывайте технический выбор с ограничением задачи. Например, в главе 7
  стандартное отклонение и перепад высот вводятся потому, что посадочная
  площадка должна быть ровной по двум различным критериям
  (PDF/печ. с. 202–203).

### Листинг и его разбор

- Один листинг должен выполнять один связный этап программы. Большую программу
  делите на именованные части: загрузка, очистка, преобразование, анализ,
  визуализация и сохранение результата.
- Сразу после листинга разбирайте значимые действия в порядке выполнения.
  Называйте функции и переменные и объясняйте:
  - источник и назначение значения;
  - форму и тип данных;
  - условие, константу, единицу измерения или выбранный порог;
  - причину преобразования;
  - значение результата для следующего этапа.
- Показывайте форму контейнера на коротком конкретном примере. В главе 2
  словарь описан как `автор → строка`, а после токенизации — как
  `автор → список слов`; в главе 11 структура для карты показана как словарь,
  где ключ — пара кодов штата и округа, а значение — плотность населения
  (PDF/печ. с. 63–65, 326–329).
- Объясняйте причины и границы данных, а не очевидный синтаксис. Локальные
  построчные комментарии регулирует раздел `Comments in tutorial code`;
  окружающая проза должна связывать строки в этап решения, а не повторять
  комментарии.

### После кода

- После каждого существенного преобразования покажите наблюдаемый результат:
  несколько строк таблицы, `shape`, `info()`, размер массива, пример словаря,
  значение метрики, короткий терминальный вывод, график или сохранённый файл.
- Скажите, что именно подтверждает вывод. В главе 11 сравнение `(3274, 3)` и
  `(3221, 3)` подтверждает удаление 53 служебных строк, `info()` проверяет типы
  новых идентификаторов, а строка 500 — корректность двухзначного кода штата
  (PDF/печ. с. 325–328).
- Интерпретируйте график или метрику словами. Не ограничивайтесь фразой
  «результат показан выше». В главе 2 сходство кривой с Дойлом трактуется как
  промежуточное свидетельство, после чего запускается следующий независимый
  тест (PDF/печ. с. 69–71).
- Если вывод зависит от допущения, назовите его в том же абзаце. Укажите
  ручной порог, усечение выборки, отсутствие калибровки, ограниченный набор
  кандидатов, малый учебный датасет или данные, которых программа не проверяет.
  Книга, например, отдельно оговаривает усечение корпусов и ограниченную
  точность уменьшенной карты MOLA (PDF/печ. с. 65, 224).

### Переход к следующему этапу

- Завершайте этап явной связкой:

  > Мы получили `<промежуточный результат>` и проверили `<свойство>`.
  > Для `<следующая цель>` требуется `<новая форма данных или операция>`,
  > поэтому теперь `<следующий шаг>`.

- Следующий листинг должен вытекать из результата предыдущего. В главе 11
  проверенные столбцы `state_id` и `cid` становятся основанием для перехода
  от датафрейма к словарю `holoviews`; в главе 2 проверенная загрузка строк —
  основанием для токенизации (PDF/печ. с. 64, 328).
- Не используйте пустые переходы «идём дальше» и «теперь самое интересное».

### Тон и терминология

- Сохраняйте сюжет как контекст, но формулируйте задачу, ограничения,
  инструкции и выводы буквально. Читатель должен понимать учебное действие
  без знания сюжета.
- Используйте активные конструкции и конкретные существительные:
  «`dropna` удаляет строки без целевого значения», «модель возвращает прогноз»,
  «мы сравниваем ошибки».
- При первом употреблении дайте короткое практическое определение нового
  термина и сразу свяжите его с текущей задачей.
- Используйте существующие идентификаторы и названия операций вместо
  отвлечённых слов «сигнал», «след», «дисциплина» или «стратегия», если они
  не обозначают конкретный объект урока.
- Формулируйте выводы с силой, которую допускают данные. Не называйте
  промежуточное сходство доказательством и не объявляйте оценку вероятностью
  без калибровки. В итогах перечисляйте конкретные ограничения и возможные
  улучшения, как это сделано для стилометрии на PDF/печ. с. 81.

### Нежелательные шаблоны

- Большой итоговый листинг без предварительно проверенных этапов.
- Пересказ каждой строки без объяснения её роли в задаче.
- Код без примера полученной структуры или вывода.
- График без словесной интерпретации.
- Ограничение без конкретной причины.
- Переход, не связанный с промежуточным результатом.
- Метафора вместо названия операции, данных или результата.

## Explanation and tutorial prose in the style of *Real-World Python*

For new and substantially revised lessons, use the recurring cycle found in
the Russian edition of Lee Vaughan's book:

> concrete problem → justified stage → small code listing →
> explanation of data and decisions → observable result → interpretation →
> next stage.

### Before the code

- Begin by naming the practical problem, the input materials, the constraints,
  and the result that will be checked. Make these measurable: state which files
  will be read, which objects will be found, which table or model will be
  produced, and where the artifact will be saved.
- After stating the problem, briefly describe the strategy as a chain of
  transformations. In Chapter 1, the search is divided into prior
  probabilities, a search result, and an update of those probabilities. In
  Chapter 2, authorship analysis is divided into loading text, tokenization,
  and five separate comparisons (PDF/print pp. 29–31, 63).
- Before each listing, explain one current stage: what it receives, what it
  does, and which value, data structure, or side effect it produces.
- Tie each technical choice to a constraint of the problem. For example,
  Chapter 7 introduces both standard deviation and elevation range because a
  landing site must satisfy two different criteria for flatness
  (PDF/print pp. 202–203).

### The listing and its explanation

- Each listing should perform one coherent stage of the program. Divide a
  larger program into named stages such as loading, cleaning, transformation,
  analysis, visualization, and saving the result.
- Immediately after the listing, explain the meaningful actions in execution
  order. Name the functions and variables, and explain:
  - where a value comes from and what it is used for;
  - the shape and type of the data;
  - any condition, constant, unit, or chosen threshold;
  - why a transformation is needed;
  - how the result is used in the next stage.
- Show the shape of a container with a short, concrete example. In Chapter 2,
  one dictionary is described as `author → string` and, after tokenization, as
  `author → list of words`. In Chapter 11, the map data is shown as a
  dictionary whose key is a state-and-county code pair and whose value is
  population density (PDF/print pp. 63–65, 326–329).
- Explain reasons and data boundaries rather than obvious syntax. Local
  line-by-line comments are governed by `Comments in tutorial code`; the
  surrounding prose should connect individual statements into a stage of the
  solution instead of repeating those comments.

### After the code

- After every substantial transformation, show an observable result: a few
  table rows, `shape`, `info()`, an array size, a sample dictionary, a metric,
  short terminal output, a graph, or a saved file.
- State exactly what the output confirms. In Chapter 11, comparing `(3274, 3)`
  with `(3221, 3)` confirms that 53 metadata rows were removed, `info()` checks
  the types of the new identifiers, and row 500 checks that the state code has
  two digits (PDF/print pp. 325–328).
- Interpret every graph or metric in words. Do not stop at “the result is shown
  above.” In Chapter 2, the similarity of one curve to Doyle's is treated as
  intermediate evidence, after which the program performs another independent
  test (PDF/print pp. 69–71).
- If a conclusion depends on an assumption, name that assumption in the same
  paragraph. Identify a hand-chosen threshold, a truncated sample, missing
  calibration, a limited candidate set, a small teaching dataset, or data that
  the program does not inspect. The book, for example, explicitly notes both
  the truncation of the text corpora and the limited accuracy of the reduced
  MOLA map (PDF/print pp. 65, 224).

### Transition to the next stage

- End each stage with an explicit link:

  > We obtained `<intermediate result>` and checked `<property>`.
  > To achieve `<next goal>`, we need `<new data shape or operation>`,
  > so the next step is to `<next action>`.

- The next listing should follow from the result of the previous one. In
  Chapter 11, the verified `state_id` and `cid` columns justify the transition
  from a dataframe to a `holoviews` dictionary. In Chapter 2, verifying that
  the text loaded correctly justifies moving on to tokenization
  (PDF/print pp. 64, 328).
- Do not use empty transitions such as “let's move on” or “now for the
  interesting part.”

### Tone and terminology

- Keep the story as context, but state the problem, constraints, instructions,
  and conclusions literally. A reader should understand the learning task
  without knowing the plot.
- Use active constructions and concrete nouns: “`dropna` removes rows that
  lack a target value,” “the model returns a prediction,” and “we compare the
  errors.”
- At first use, give a short practical definition of each unfamiliar term and
  connect it immediately to the current task.
- Prefer existing identifiers and names of operations to abstract labels such
  as “signal,” “trace,” “discipline,” or “strategy” when those labels do not
  refer to a concrete object in the lesson.
- Match the strength of each conclusion to what the data supports. Do not call
  an intermediate similarity proof, and do not call a score a probability
  unless it has been calibrated. In the conclusion, name concrete limitations
  and possible improvements (PDF/print p. 81), as the stylometry chapter does.

### Patterns to avoid

- A large final listing that has not been introduced through verified stages.
- A line-by-line paraphrase that does not explain each statement's role in the
  problem.
- Code without an example of the resulting structure or output.
- A graph without a written interpretation.
- A limitation stated without a concrete reason.
- A transition that does not follow from the intermediate result.
- A metaphor in place of the name of an operation, dataset, or result.

## Часть II: семинарский ход анализа данных

Тетрадь Part II — это завершённый воспроизводимый разбор, а не бланк домашнего
задания. Learner-версия должна выполняться сверху вниз без ручного дописывания.
Не оставляйте пустые code cells, `TODO`, заглушки `pass`, фразы «напишите код
здесь», незаполненные словари, фиктивные метрики или ячейки «Твой вывод». Весь
код, таблицы, графики и содержательные выводы уже присутствуют в тетради.

Стройте анализ как явную цепочку решений:

1. **Поставьте вопрос.** Назовите объект наблюдения, целевую переменную, момент
   прогноза или измерения и критерий успешного ответа. Объясните, зачем этот
   вопрос решается до показа кода.
2. **Загрузите и проверьте источник.** Укажите происхождение и версию данных,
   проверьте путь или checksum, покажите размер таблицы, типы, диапазоны,
   пропуски, дубликаты и распределение цели. После таблицы сформулируйте, как
   результат аудита меняет дальнейшую подготовку.
3. **Проведите визуальную разведку.** Один график или одна компактная группа
   графиков должны отвечать на заранее сформулированный вопрос. Перед кодом
   объясните сравнение и ожидаемую форму результата; после графика назовите
   наблюдение, ограничение и следующий аналитический выбор.
4. **Зафиксируйте границы проверки.** Сначала отделите внешнюю тестовую
   выборку. Импьютеры, кодировщики, масштабирование, отбор признаков,
   преобразования цели, подбор гиперпараметров и выбор порога обучайте только
   на train или внутри его CV. Для связанных наблюдений используйте временное
   или групповое разбиение вместо случайного. Фиксируйте `random_state` и
   объясняйте единицу независимости.
5. **Покажите baseline до основной модели.** Назовите простое правило, с
   которым сравнивается модель, и объясните, какую нижнюю планку оно задаёт.
   Кандидатов сравнивайте на одних и тех же разбиениях.
6. **Обучите и сравните модели.** Подбор параметров и порога выполняйте внутри
   обучающей выборки. Показывайте компактную таблицу с одинаковыми метриками
   для baseline и кандидатов. Внешний test открывайте один раз после фиксации
   модели и правила принятия решения.
7. **Объясните метрики до интерпретации чисел.** Назовите направление
   улучшения, единицы и тип ошибки, который отражает каждая метрика. Для
   регрессии возвращайте прогнозы в исходный масштаб перед MAE/MSE; R²
   интерпретируйте вместе с абсолютной ошибкой. Для классификации дополняйте
   агрегатную метрику confusion matrix, метриками по классам или калибровкой,
   когда этого требует вопрос.
8. **Разберите ошибки.** Покажите остатки, ошибочные строки или изображения,
   срезы по важным группам либо калибровочную кривую. Объясните не только
   среднее качество, но и где модель ошибается дороже или систематичнее.
9. **Отделите факт от интерпретации.** Формулируйте отдельно наблюдаемое число
   или рисунок, поддерживаемое им объяснение, то, чего анализ не доказывает,
   ограничения данных и рекомендуемый следующий шаг.
10. **Завершите ответом на исходный вопрос.** Итог должен ссылаться на
    полученные таблицы и графики, а не повторять общий учебный тезис.

Используйте материалы домашних работ как ориентиры, но превращайте задания в
готовый семинарский разбор:

- в `ML_ДЗ_Неделя_1.ipynb` аудит велопроката объединяет словарь признаков,
  `info()`, описательную статистику, проверку дубликатов и пропусков до создания
  временных признаков (ячейки 6–21);
- каждый график спроса сопровождайте буквальным наблюдением о форме
  распределения, сезонности или различии будней и выходных, как в ячейках
  23–53 той же тетради;
- в тетради `Домашнее_задание_Логистическая_регрессия,_SVM_ipynb.ipynb`
  эксперимент с преобразованиями цели сравнивает одинаковые модели по MAE и R²
  в исходном масштабе (ячейки 14–27);
- разбор калибровки сначала объясняет расхождение предсказанной вероятности и
  фактической частоты, затем сравнивает Brier score и log loss и завершается
  калибровочной кривой (ячейки 28–43);
- assert-проверки показывайте вместе с объяснением проверяемого контракта, а не
  вместо аналитического вывода.

Не переносите утечку данных из исходных домашних работ: преобразования и
масштабирование всего `X` до train/test split являются антипаттерном. Обучайте
препроцессоры только на train или внутри конвейера и CV.

### Ритм Markdown и code cells

Для каждого существенного шага используйте тройку:

1. Markdown перед кодом: вопрос, причина действия, входные данные и ожидаемая
   форма результата.
2. Полностью заполненная code cell: одно связное действие, явный вывод таблицы,
   числа или графика.
3. Markdown после кода: конкретное наблюдение, его границы и связь со следующим
   шагом.

Не ставьте несколько code cells подряд без объяснения, если первая меняет
данные или создаёт результат, необходимый для понимания следующей. Не
пересказывайте очевидный синтаксис; объясняйте аналитическое решение, границу
данных и смысл результата.

### Шаблон одного аналитического этапа

**Markdown перед кодом**

> ### Форма распределения числа аренд
>
> Сначала проверим распределение `total_count` — количества аренд за один
> период. Гистограмма показывает, какие значения встречаются чаще, а KDE
> помогает увидеть общую форму распределения. Это нужно до выбора сводной
> статистики и модели: сильная асимметрия означает, что одно среднее значение
> описывает спрос неполно.

**Code cell**

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(data=bike, x="total_count", bins=40, kde=True, ax=ax)
ax.set(
    title="Распределение числа аренд за период",
    xlabel="Количество аренд",
    ylabel="Число наблюдений",
)
plt.tight_layout()
plt.show()

display(
    bike["total_count"]
    .describe(percentiles=[0.5, 0.75, 0.9, 0.95])
    .to_frame("total_count")
)
```

**Markdown после кода**

> Распределение скошено вправо: большинство периодов содержит сравнительно
> мало аренд, а большие значения встречаются заметно реже. Поэтому среднее
> тянется в сторону редких пиков и не должно быть единственным описанием
> спроса. На следующем шаге агрегируем аренды по датам и проверим, образуют ли
> высокие значения устойчивую временную динамику или остаются отдельными
> всплесками.

Таблица или график не считаются завершённым этапом без такого чтения
результата. Не придумывайте причинность по одной корреляции: называйте
наблюдаемую ассоциацию и отдельно указывайте, какие данные или эксперимент
потребовались бы для причинного вывода.

## Part II: seminar-style data-analysis workflow

A Part II notebook is a complete, reproducible walkthrough, not a homework
worksheet. The learner version must run from top to bottom without requiring
the learner to add code manually. Do not leave empty code cells, `TODO`
markers, `pass` stubs, prompts such as “write your code here,” unfinished
dictionaries, placeholder metrics, or cells labeled “Your conclusion.” All
code, tables, graphs, and substantive conclusions must already be present in
the notebook.

Structure the analysis as an explicit chain of decisions:

1. **State the question.** Name the unit of observation, the target variable,
   the point in time at which prediction or measurement occurs, and the
   criterion for a successful answer. Explain why the question matters before
   showing code.
2. **Load and audit the source.** State the origin and version of the data,
   verify its path or checksum, and show the table size, data types, ranges,
   missing values, duplicates, and target distribution. After the table,
   explain how the audit findings change the subsequent preparation.
3. **Perform visual exploration.** Each graph, or compact group of graphs,
   should answer a question stated in advance. Before the code, explain the
   comparison and the expected form of the result. After the graph, state the
   observation, its limitation, and the next analytical choice.
4. **Establish the evaluation boundaries.** Set aside the final test set first.
   Fit imputers, encoders, scalers, feature selection, target transformations,
   hyperparameter searches, and threshold selection only on the training set
   or inside its cross-validation. For related observations, use a temporal or
   group split instead of a random split. Set `random_state` explicitly and
   explain the unit of independence.
5. **Show a baseline before the main model.** Name the simple rule against
   which the model is compared and explain the lower bound it establishes.
   Compare all candidate models on the same splits.
6. **Train and compare models.** Tune parameters and decision thresholds
   within the training data. Show a compact table that reports the same metrics
   for the baseline and every candidate. Open the final test set only once,
   after the model and decision rule have been fixed.
7. **Explain metrics before interpreting their values.** State the direction
   of improvement, the units, and the type of error represented by each
   metric. For regression, return predictions to the original target scale
   before computing MAE or MSE; interpret R² alongside an absolute-error
   metric. For classification, supplement an aggregate metric with a confusion
   matrix, per-class metrics, or calibration when the question requires it.
8. **Analyze errors.** Show residuals, misclassified rows or images, slices for
   important groups, or a calibration curve. Explain not only average
   performance, but also where the model's errors are more costly or more
   systematic.
9. **Separate observation from interpretation.** Distinguish the observed
   number or graph, the explanation it supports, what the analysis does not
   prove, the limitations of the data, and the recommended next step.
10. **Finish by answering the original question.** The conclusion should refer
    to the tables and graphs produced in the analysis instead of repeating a
    generic teaching point.

Use the homework materials as references, but turn their assignments into a
complete seminar walkthrough:

- in `ML_ДЗ_Неделя_1.ipynb`, the bike-rental audit combines the feature
  dictionary, `info()`, descriptive statistics, duplicate checks, and
  missing-value checks before temporal features are created (cells 6–21);
- follow every demand graph with a literal observation about distribution
  shape, seasonality, or the difference between weekdays and weekends, as in
  cells 23–53 of the same notebook;
- in `Домашнее_задание_Логистическая_регрессия,_SVM_ipynb.ipynb`, the
  target-transformation experiment compares identical models using MAE and R²
  on the target's original scale (cells 14–27);
- the calibration walkthrough first explains the difference between predicted
  probability and observed frequency, then compares Brier score and log loss,
  and finishes with a calibration curve (cells 28–43);
- show assertions together with an explanation of the contract they verify;
  they do not replace an analytical conclusion.

Do not copy data leakage from the source homework: transforming or scaling all
of `X` before the train/test split is an anti-pattern. Fit preprocessors only
on the training data or inside a pipeline and cross-validation.

### Rhythm of Markdown and code cells

Use the following three-part sequence for every substantial step:

1. Markdown before the code: the question, the reason for the action, the input
   data, and the expected form of the result.
2. A complete code cell: one coherent action with explicit output in the form
   of a table, number, or graph.
3. Markdown after the code: a concrete observation, its limitations, and its
   connection to the next step.

Do not place several code cells in succession without explanation when the
first cell changes the data or produces a result needed to understand the next
one. Do not paraphrase obvious syntax; explain the analytical decision, the
data boundary, and the meaning of the result.

### Template for one analytical stage

**Markdown before the code**

> ### Distribution of the number of rentals
>
> We begin by checking the distribution of `total_count`, the number of rentals
> in one period. The histogram shows which values occur most often, while the
> KDE reveals the distribution's overall shape. This check comes before the
> choice of summary statistic and model: strong skew means that the mean alone
> does not describe demand adequately.

**Code cell**

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(data=bike, x="total_count", bins=40, kde=True, ax=ax)
ax.set(
    title="Distribution of rentals per period",
    xlabel="Number of rentals",
    ylabel="Number of observations",
)
plt.tight_layout()
plt.show()

display(
    bike["total_count"]
    .describe(percentiles=[0.5, 0.75, 0.9, 0.95])
    .to_frame("total_count")
)
```

**Markdown after the code**

> The distribution is right-skewed: most periods contain relatively few
> rentals, while large values occur much less often. The mean is therefore
> pulled toward rare peaks and should not be the only summary of demand. In the
> next step, we aggregate rentals by date and check whether the high values form
> a persistent temporal pattern or remain isolated spikes.

A table or graph does not complete a stage until the notebook includes this
kind of reading of the result. Do not infer causation from a correlation alone:
name the observed association and state separately which additional data or
experiment would be needed to support a causal conclusion.

## Learner and solution boundaries

Part I learner ZIPs intentionally contain an empty Python file that the learner
fills while following the chapter. Do not replace it with `TODO` stubs or a
finished implementation. The complete code belongs in the chapter and the
canonical solution, and those two versions must remain synchronized.

Part I tests are maintainer tools for checking that the tutorial works. Keep
test commands and test-driven instructions out of student-facing pages and
ZIPs.

Part II solution notebooks are canonical. Regenerate learner notebooks with
`pnpm build:notebooks`; do not edit generated learner notebooks by hand.
Learner notebooks are complete walkthroughs generated from the canonical
solution: the generator removes only `BEGIN/END SOLUTION` marker lines and
the `solution-only` tag, while preserving the enclosed code, substantive
Markdown, and tidy saved outputs. A `learner_source` override is allowed only
for technical bootstrap or variant handling, and it must remain runnable.
Exercise tags may identify guided practice, but exercise code must be complete.
After canonical changes, use
`python3 tools/run_part2_notebooks.py --write-solutions` to execute all
solutions top to bottom in the pinned clean environment and record their
outputs before regenerating learners and archives.

Treat schema labels and identifiers as implementation details, not learning
goals. Supply fixed values such as `finding_id` in the starter code when the
learner does not need to design them. At first use, explain the practical
reason for the identifier—for example, finding a record when list order
changes—and then return attention to the investigation task.

## Verification

Run the narrow checks for the edited area and use `pnpm verify` before handing
off broad course changes. `pnpm build` verifies the rendered site, while
`pnpm test:python`, `pnpm test:notebooks`, and `pnpm test:archives` cover the
project code and generated teaching materials.

After changing prominent copy, inspect the rendered page at desktop and mobile
widths. Rebalance type size, line length, or grid columns when a longer heading
changes the intended proportions.
