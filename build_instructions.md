# Инструкции по сборке приложения

## Установка зависимостей
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Сборка в один файл
```bash
pyinstaller optimization_app.spec
```

## Альтернативная сборка (простая команда)
```bash
pyinstaller --onefile --name optimization_app main.py --hidden-import streamlit --hidden-import app.optim.methods --hidden-import app.optim.selection --hidden-import app.visualize
```

## Запуск собранного приложения
```bash
# Windows
dist/optimization_app.exe

# Linux/Mac  
dist/optimization_app
```

## Возможные проблемы и решения

### 1. Отсутствующие модули
Если приложение не запускается, добавьте в hiddenimports:
- `streamlit.web.cli`
- `streamlit.runtime.scriptrunner`
- `matplotlib.backends.backend_agg`

### 2. Большой размер файла
- Исключите ненужные модули в excludes
- Используйте --exclude-module для больших библиотек

### 3. Ошибки импорта
- Проверьте, что все модули app.* включены
- Добавьте недостающие зависимости в hiddenimports

## Тестирование сборки
```bash
# После сборки
dist/optimization_app.exe --help
# или
dist/optimization_app.exe
```
