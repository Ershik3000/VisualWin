## VisualWin Client

Ку тут есть исходник и клиент для чит сети **VisualWin**

---

## Работа клиента

Простой PyQt6 с понятным интерфейсом доступно скачивание всего софта от **VisualWin**

Запросы на скачку dll идут на сайт **VisualWin**

## Работа с исходниками

Попробовал расписать все более менее понятно с понятными коментариями 
иногда есть функции которые лучше не менять

А так кастомизируйте изучайте итд (:

## Библиотеки и сборка

Библиотеки
```bash
pip install PyQt6 requests
```

Дефолт сборка
```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon;icon" --add-data "ttf;ttf" --hidden-import=cs2 --hidden-import=settings --hidden-import=client client.py
```
