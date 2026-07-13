---
title: "II-02. Дебриф: Пассажиры после факта"
description: "Канонический вывод аудита утечки в Titanic и ссылка на выполненный solution notebook."
arc: part-2
caseNumber: II-02
projectId: part-2-case-02
time: "15–20 минут"
format: Дебриф
datasetIds: [openml-titanic-40945-frozen]
notebook: projects/part-2/case-02/solution/case-02-solution.ipynb
---

<span class="bureau-page-scope" aria-hidden="true"></span>

Сначала завершите [дело II-02](../passengers-after-the-fact/). Полный pipeline и сравнение вариантов доступны в notebook:

- [посмотреть solution notebook на GitHub](https://github.com/mkuziuk/python-tutorial/blob/main/projects/part-2/case-02/solution/case-02-solution.ipynb);
- [запустить solution notebook в Colab](https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-02/solution/case-02-solution.ipynb).

## Канонический вывод

**Установленный факт.** `boat` и `body` возникают после исхода и дают модели прямую или почти прямую информацию о целевой переменной. В одинаковом outer holdout leaky-вариант заметно превосходит pipeline, использующий только доступные заранее признаки.

**Поддержанная интерпретация.** Основная часть впечатляющего результата поставщика связана с post-outcome leakage. Честная модель решает существенно более трудную задачу.

**Что не доказано.** Мы не установили, кто выбрал столбцы и понимал ли этот человек временную семантику. Также сравнение не доказывает причинное влияние остальных признаков на выживание.

**Ограничения.** Исторический Titanic неполон, категории отражают конкретную эпоху, а snapshot учебно заморожен для воспроизводимости.

**Рекомендованное действие.** Для каждого будущего набора требовать карточку временной доступности признаков и выполнять preprocessing внутри pipeline после разбиения.

## Что важно унести

Утечку нельзя надежно найти только по типу столбца или корреляции. Нужен вопрос о моменте предсказания. `ColumnTransformer` решает другую, техническую задачу: одинаково и без подглядывания обучает разные преобразования числовых и категориальных признаков.

Следующее дело: [Цена одной ошибки](../cost-of-one-error/).
