# Iris: происхождение данных

Тетрадь не загружает изменяемый файл из сети. В архив вложен замороженный
`iris.csv`, экспортированный скриптом `freeze_iris.py` из
`sklearn.datasets.load_iris(as_frame=True)` в зафиксированной версии
scikit-learn. Notebook проверяет SHA-256 файла и создаёт `DataFrame` через
`pd.read_csv()` до начала анализа.

- Идентификатор курса: `sklearn-iris`
- Записей: 150
- Числовых признаков: 4
- Цель: один из трёх видов ириса
- Исходная публикация: R. A. Fisher, *The use of multiple measurements in taxonomic problems* (1936)
- Документация scikit-learn: <https://scikit-learn.org/stable/datasets/toy_dataset.html#iris-dataset>
- Карточка UCI: <https://archive.ics.uci.edu/dataset/53/iris>

Имя файла, схема и контрольная сумма записаны в `dataset_manifest.json` и
`CHECKSUMS.sha256`. Версию экспортера фиксирует `requirements.txt`
(`scikit-learn==1.9.0`). Набор используется только как учебный пример; ссылка и
атрибуция должны сохраняться в производных материалах.
