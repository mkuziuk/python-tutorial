---
title: Материалы
description: Данные, стартовые файлы и команды для проектных глав.
---

На этой странице собраны рабочие папки первой арки — от первых операций со строками до объектной модели и итогового вердикта. Дела расположены по возрастанию сложности: начните с дела 01 и двигайтесь по порядку. В каждом архиве лежат файлы ученика: README, данные, пустой стартовый скрипт, `requirements.txt`, пример формы вывода и папка `tests/` для самопроверки. Полные решения открываются отдельно в главах разбора.

Если во время работы нужно быстро вспомнить `list`, `dict`, функции, `pathlib`, JSON или другой инструмент, возвращайтесь в [Справочник следователя](../field-guide/): ссылки на нужные страницы также есть в начале каждого дела.

## Дело 01. Кто оставил предупреждение?

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-01/</code></p>
  <p><strong>Уровень:</strong> начальный+</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-01.zip">case-01.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/anonymous-letter/">сборка инструмента</a> · <a href="../cases/anonymous-letter-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой `anonymous_letter.py`
- `data/anonymous.txt`
- `data/author_morozova.txt`, `data/author_sokolov.txt`, `data/author_korolev.txt`
- `check_result.txt`

```bash
cd case-01
python -m pip install -r requirements.txt
python anonymous_letter.py
python -m unittest discover -s tests
```

## Дело 02. Детектор текстовых совпадений

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-02/</code></p>
  <p><strong>Уровень:</strong> начальный+</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-02.zip">case-02.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/copy-paste-detector/">сборка инструмента</a> · <a href="../cases/copy-paste-detector-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый скрипт детектора;
- папка `data/` с отчетами и заметками;
- `check_result.txt` с примером формы отчета.

```bash
cd case-02
python -m pip install -r requirements.txt
python copy_paste_detector.py
python -m unittest discover -s tests
```

## Дело 03. Фишинговое письмо или нет?

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-03/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-03.zip">case-03.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/phishing-email/">сборка инструмента</a> · <a href="../cases/phishing-email-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый скрипт анализатора писем;
- письма `.eml` в `data/`;
- `check_result.txt` с примером отчета по риск-сигналам.

```bash
cd case-03
python -m pip install -r requirements.txt
python phishing_email.py
python -m unittest discover -s tests
```

## Дело 04. Ночной сигнал архива

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-04/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-04.zip">case-04.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/secret-folder-archive/">сборка инструмента</a> · <a href="../cases/secret-folder-archive-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый скрипт индексатора;
- папка `data/secret_folder/` с архивными заметками и копиями;
- `check_result.txt` с формой отчета по manifest.

```bash
cd case-04
python -m pip install -r requirements.txt
python secret_folder_archive.py
python -m unittest discover -s tests
```

## Дело 05. Доска расследования

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-05/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-05.zip">case-05.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/investigation-system/">сборка инструмента</a> · <a href="../cases/investigation-system-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый скрипт доски расследования;
- начальные данные в `data/`;
- `check_result.txt` с примером терминальной сводки.

```bash
cd case-05
python -m pip install -r requirements.txt
python investigation_system.py
python -m unittest discover -s tests
```

## Дело 06. Вердикт перед открытием

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-06/</code></p>
  <p><strong>Уровень:</strong> продвинутый</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-06.zip">case-06.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/final-verdict/">сборка инструмента</a> · <a href="../cases/final-verdict-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой `final_verdict.py`;
- `data/evidence_bundle.json` с фактами, гипотезами и ограничениями;
- `check_result.txt` с формой финального отчета;
- `tests/` для проверки хронологии, баллов и вердикта.

```bash
cd case-06
python -m pip install -r requirements.txt
python final_verdict.py
python -m unittest discover -s tests
```
