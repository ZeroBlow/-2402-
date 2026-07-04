# Детекция брошенных предметов на улице

Веб-приложение для детекции потенциально брошенных предметов (сумки, рюкзаки, чемоданы, зонты) с использованием YOLOv8 и Flask.

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ZeroBlow/-2402-
   cd abandoned_object_detection
   
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   
4. Установите зависимости:
   ```bash
   pip install flask ultralytics opencv-python numpy
   
6. Запустите приложение:
   ```bash
   python app.py
   
8. Откройте в браузере: http://127.0.0.1:5000
