# Инструкции по сборке приложения

## Установка зависимостей
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Сборка в один файл

### Flask веб-приложение (рекомендуется)
```bash
pyinstaller web_app.spec
```
Затем запустите: `dist/optimization_web_app.exe`
Откройте браузер: http://localhost:5000

## Простой запуск
Используйте bat файл:
```bash
run_optimization.bat
```

## Альтернативная сборка (простая команда)
```bash
pyinstaller --onefile --name optimization_web_app web_app.py --add-data "app;app" --hidden-import flask --hidden-import matplotlib.backends.backend_agg
```

## Запуск собранного приложения
```bash
# Flask веб-приложение (работает стабильно)
dist/optimization_web_app.exe
```

## Возможные проблемы и решения

### 1. Streamlit не работает в exe
- **Решение**: Используйте Flask веб-приложение (web_app.py)
- Flask полностью самодостаточен в exe файле

### 2. Отсутствующие модули
Если приложение не запускается, добавьте в hiddenimports:
- `flask`
- `matplotlib.backends.backend_agg`
- `app.optim.methods`
- `app.optim.selection`
- `app.visualize`

### 3. Большой размер файла
- Исключите ненужные модули в excludes
- Используйте --exclude-module для больших библиотек

### 4. Ошибки импорта
- Проверьте, что все модули app.* включены
- Добавьте недостающие зависимости в hiddenimports

## Тестирование сборки
```bash
# Flask веб-приложение
dist/optimization_web_app.exe
# Откройте http://localhost:5000 в браузере
```

## Рекомендации

- **Для exe файла**: Используйте Flask веб-приложение - оно стабильно работает
- **Для разработки**: Используйте Streamlit версию - более удобный интерфейс
- **Для курсовой**: Flask веб-приложение подходит для демонстрации функциональности