# Iris: происхождение данных

Тетрадь не загружает изменяемый файл из сети. Она вызывает `sklearn.datasets.load_iris(as_frame=True)` из зафиксированной версии scikit-learn и использует встроенную копию классического набора Iris.

- Идентификатор курса: `sklearn-iris`
- Записей: 150
- Числовых признаков: 4
- Цель: один из трёх видов ириса
- Исходная публикация: R. A. Fisher, *The use of multiple measurements in taxonomic problems* (1936)
- Документация scikit-learn: <https://scikit-learn.org/stable/datasets/toy_dataset.html#iris-dataset>
- Карточка UCI: <https://archive.ics.uci.edu/dataset/53/iris>

В ZIP дела нет отдельного файла с наблюдениями, поэтому контрольная сумма датасета отсутствует. Версию реализации фиксирует `requirements.txt` (`scikit-learn==1.9.0`). Набор используется только как учебный пример; ссылка и атрибуция должны сохраняться в производных материалах.
