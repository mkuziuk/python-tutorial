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
        'Проектный учебник по Python на русском: реальные задачи, рабочие инструменты и короткий справочник по понятиям.',
      locales: {
        root: {
          label: 'Русский',
          lang: 'ru',
        },
      },
      customCss: ['./src/styles/starlight.css'],
      favicon: '/images/favicon.svg',
      sidebar: [
        { label: 'Главная', link: '/' },
        {
          label: 'Дела',
          items: [
            { label: 'Обзор дел', slug: 'cases' },
            {
              label: '01. Кто оставил предупреждение?',
              slug: 'cases/anonymous-letter',
            },
            {
              label: '01. Разбор полного решения',
              slug: 'cases/anonymous-letter-solution',
            },
            {
              label: '02. Детектор текстовых совпадений',
              slug: 'cases/copy-paste-detector',
            },
            {
              label: '02. Разбор полного решения',
              slug: 'cases/copy-paste-detector-solution',
            },
            {
              label: '03. Фишинговое письмо или нет?',
              slug: 'cases/phishing-email',
            },
            {
              label: '03. Разбор полного решения',
              slug: 'cases/phishing-email-solution',
            },
            {
              label: '04. Ночной сигнал архива',
              slug: 'cases/secret-folder-archive',
            },
            {
              label: '04. Разбор полного решения',
              slug: 'cases/secret-folder-archive-solution',
            },
            {
              label: '05. Доска расследования',
              slug: 'cases/investigation-system',
            },
            {
              label: '05. Разбор полного решения',
              slug: 'cases/investigation-system-solution',
            },
            {
              label: '06. Вердикт перед открытием',
              slug: 'cases/final-verdict',
            },
            {
              label: '06. Разбор полного решения',
              slug: 'cases/final-verdict-solution',
            },
          ],
        },
        {
          label: 'Справочник',
          items: [
            { label: 'Как пользоваться', slug: 'field-guide' },
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
