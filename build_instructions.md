# Инструкции по сборке приложения

## Установка зависимостей
```bash
pip install -r requirements.txt
pip install pyinstaller flask
```

## Сборка в один файл

### Вариант 1: Flask веб-приложение (рекомендуется)
```bash
pyinstaller web_app.spec
```
Затем запустите: `dist/optimization_web_app.exe`
Откройте браузер: http://localhost:5000

### Вариант 2: Streamlit приложение (может не работать)
```bash
pyinstaller launcher.spec
```
Затем запустите: `dist/optimization_app.exe`

## Простой запуск
Используйте bat файл:
```bash
run_optimization_app.bat
```

## Альтернативная сборка (простая команда)
```bash
pyinstaller --onefile --name optimization_web_app web_app.py --hidden-import flask --hidden-import app.optim.methods --hidden-import app.optim.selection --hidden-import app.visualize
```

## Запуск собранного приложения
```bash
# Flask веб-приложение (работает стабильно)
dist/optimization_web_app.exe

# Streamlit приложение (может не работать)
dist/optimization_app.exe
```

## Возможные проблемы и решения

### 1. Streamlit не работает в exe
- **Решение**: Используйте Flask версию (web_app.py)
- Flask более совместим с PyInstaller

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
# Flask приложение
dist/optimization_web_app.exe
# Откройте http://localhost:5000 в браузере

# Streamlit приложение (если работает)
dist/optimization_app.exe
```

## Рекомендации

- **Для exe файла**: Используйте Flask версию - она стабильно работает
- **Для разработки**: Используйте Streamlit версию - более удобный интерфейс
- **Для курсовой**: Flask версия подходит для демонстрации функциональности