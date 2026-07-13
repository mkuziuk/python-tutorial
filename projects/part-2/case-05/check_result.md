# Ожидаемая форма результата II-05

Данные
- Content hash load_digits совпадает с dataset_manifest.json.
- X: (1797, 64), images: (1797, 8, 8), 10 классов.

Процедура
- Stratified outer split: 1 347 train / 450 test, пересечение индексов 0.
- Train-only StratifiedKFold: 3 folds, shuffle=True, random_state=42.
- Сравнены scaled k-NN(5) и scaled RBF SVM по accuracy и macro-F1.
- Grid содержит ровно C={2,10} × gamma={scale,0.001}; scoring=f1_macro.
- Зафиксирована конфигурация StandardScaler -> RBF SVC(C=2, gamma=scale).

Holdout
- Accuracy и macro-F1 находятся примерно около 0,98 и выше 0,95.
- Показаны recall для цифр 0–9, confusion matrix и галерея реальных ошибок,
  а не только удачных примеров.

Артефакты
- artifacts/model_lock.json фиксирует процедуру и метрики.
- artifacts/audit_memo.md содержит пять разделов и не делает вывода об авторе.
