import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const site = process.env.SITE_URL || 'https://example.com';
const base = process.env.BASE_PATH ? { base: process.env.BASE_PATH } : {};

export default defineConfig({
  site,
  ...base,
  integrations: [
    starlight({
      title: 'Python-расследования',
      description:
        'Проектный учебник по Python и машинному обучению на русском: расследования, рабочие инструменты и проверка моделей.',
      locales: {
        root: {
          label: 'Русский',
          lang: 'ru',
        },
      },
      customCss: ['./src/styles/starlight.css'],
      components: {
        Sidebar: './src/components/Sidebar.astro',
      },
      favicon: '/images/favicon.svg',
      sidebar: [
        { label: 'Главная', link: '/' },
        {
          label: 'Часть I · Архив',
          collapsed: true,
          items: [
            { label: 'Обзор первой части', slug: 'cases' },
            {
              label: '01. Кто оставил предупреждение?',
              slug: 'cases/anonymous-letter',
            },
            {
              label: '01. Разбор решения',
              slug: 'cases/anonymous-letter-solution',
            },
            {
              label: '02. Детектор текстовых совпадений',
              slug: 'cases/copy-paste-detector',
            },
            {
              label: '02. Разбор решения',
              slug: 'cases/copy-paste-detector-solution',
            },
            {
              label: '03. Фишинговое письмо или нет?',
              slug: 'cases/phishing-email',
            },
            {
              label: '03. Разбор решения',
              slug: 'cases/phishing-email-solution',
            },
            {
              label: '04. Ночной сигнал архива',
              slug: 'cases/secret-folder-archive',
            },
            {
              label: '04. Разбор решения',
              slug: 'cases/secret-folder-archive-solution',
            },
            {
              label: '05. Доска расследования',
              slug: 'cases/investigation-system',
            },
            {
              label: '05. Разбор решения',
              slug: 'cases/investigation-system-solution',
            },
            {
              label: '06. Вердикт перед открытием',
              slug: 'cases/final-verdict',
            },
            {
              label: '06. Разбор решения',
              slug: 'cases/final-verdict-solution',
            },
          ],
        },
        {
          label: 'Часть II · Бюро',
          collapsed: true,
          items: [
            { label: 'Обзор бюро', slug: 'bureau' },
            { label: 'II-01. Ирисовый экзамен', slug: 'bureau/iris-exam' },
            { label: 'II-01. Дебриф', slug: 'bureau/iris-exam-solution' },
            {
              label: 'II-02. Пассажиры после факта',
              slug: 'bureau/passengers-after-the-fact',
            },
            {
              label: 'II-02. Дебриф',
              slug: 'bureau/passengers-after-the-fact-solution',
            },
            { label: 'II-03. Цена одной ошибки', slug: 'bureau/cost-of-one-error' },
            { label: 'II-03. Дебриф', slug: 'bureau/cost-of-one-error-solution' },
            {
              label: 'II-04. Карта дорогих ошибок',
              slug: 'bureau/map-of-costly-errors',
            },
            { label: 'II-04. Дебриф', slug: 'bureau/map-of-costly-errors-solution' },
            { label: 'II-05. Знакомый почерк', slug: 'bureau/familiar-handwriting' },
            { label: 'II-05. Дебриф', slug: 'bureau/familiar-handwriting-solution' },
            { label: 'II-06. Экзамен для «Компаса»', slug: 'bureau/compass-exam' },
            { label: 'II-06. Финальный дебриф', slug: 'bureau/compass-exam-solution' },
          ],
        },
        {
          label: 'Справочник',
          items: [
            { label: 'Как пользоваться', slug: 'field-guide' },
            {
              label: 'Основы Python',
              collapsed: true,
              items: [
                { label: 'Установка Python', slug: 'field-guide/install-python' },
                { label: 'Условия и циклы', slug: 'field-guide/control-flow' },
                { label: 'str', slug: 'field-guide/str' },
                { label: 'list', slug: 'field-guide/list' },
                { label: 'dict', slug: 'field-guide/dict' },
                { label: 'set', slug: 'field-guide/set' },
                { label: 'tuple', slug: 'field-guide/tuple' },
                { label: 'Counter', slug: 'field-guide/counter' },
                { label: 'functions', slug: 'field-guide/functions' },
                { label: 'Включения и генераторы', slug: 'field-guide/comprehensions' },
                { label: 'regex', slug: 'field-guide/regex' },
                { label: 'Файлы', slug: 'field-guide/file-io' },
                { label: 'pathlib', slug: 'field-guide/pathlib' },
                { label: 'sorting', slug: 'field-guide/sorting' },
                { label: 'exceptions', slug: 'field-guide/exceptions' },
                { label: 'email, URL и IP', slug: 'field-guide/email-url-ip' },
                { label: 'hashlib', slug: 'field-guide/hashlib' },
                { label: 'JSON', slug: 'field-guide/json' },
                { label: 'Rich', slug: 'field-guide/rich' },
                { label: 'classes', slug: 'field-guide/classes' },
                { label: 'dataclasses', slug: 'field-guide/dataclasses' },
                { label: 'Аннотации типов', slug: 'field-guide/type-hints' },
                { label: 'unittest', slug: 'field-guide/testing' },
                { label: 'Дата и время', slug: 'field-guide/datetime' },
                { label: 'StrEnum и match', slug: 'field-guide/enums-match' },
              ],
            },
            {
              label: 'Машинное обучение',
              collapsed: true,
              items: [
                { label: 'Jupyter и Colab', slug: 'field-guide/ml-notebooks' },
                { label: 'NumPy и формы', slug: 'field-guide/numpy' },
                { label: 'pandas и пропуски', slug: 'field-guide/pandas' },
                { label: 'Графики', slug: 'field-guide/plotting' },
                { label: 'Постановка ML-задачи', slug: 'field-guide/ml-framing' },
                { label: 'Утечка и pipeline', slug: 'field-guide/leakage-pipelines' },
                { label: 'Классические модели', slug: 'field-guide/ml-models' },
                { label: 'Метрики и пороги', slug: 'field-guide/classification-metrics' },
                { label: 'CV и подбор', slug: 'field-guide/cross-validation' },
                { label: 'Регрессия и остатки', slug: 'field-guide/regression' },
                {
                  label: 'Группы, сдвиг и model card',
                  slug: 'field-guide/grouped-validation',
                },
              ],
            },
          ],
        },
        { label: 'Материалы', slug: 'materials' },
        { label: 'Карта навыков', slug: 'skill-map' },
      ],
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 3,
      },
      lastUpdated: true,
      credits: false,
    }),
  ],
});
