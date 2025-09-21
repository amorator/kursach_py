# Инструкции по сборке приложения

## Установка зависимостей
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Сборка в один файл

### Прокси-приложение (рекомендуется)
```bash
pyinstaller optimization_proxy.spec
```
Затем запустите: `dist/optimization_proxy.exe`
Откройте браузер: http://localhost:8501

## Простой запуск
Используйте bat файл:
```bash
run_optimization.bat
```

## Альтернативная сборка (простая команда)
```bash
pyinstaller --onefile --name optimization_proxy proxy_app.py --add-data "app;app"
```

## Запуск собранного приложения
```bash
# Прокси-приложение (работает стабильно)
dist/optimization_proxy.exe
```

## Возможные проблемы и решения

### 1. Streamlit не работает в exe
- **Решение**: Используйте прокси-приложение (proxy_app.py)
- Прокси запускает Streamlit через системный Python

### 2. Отсутствующие модули
Если приложение не запускается, добавьте в hiddenimports:
- `streamlit`
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
# Прокси-приложение
dist/optimization_proxy.exe
# Откройте http://localhost:8501 в браузере
```

## Рекомендации

- **Для exe файла**: Используйте прокси-приложение - оно стабильно работает
- **Для разработки**: Используйте Streamlit версию - более удобный интерфейс
- **Для курсовой**: Прокси-приложение подходит для демонстрации функциональности