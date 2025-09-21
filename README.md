# Визуализация методов одномерной оптимизации

Приложение для демонстрации и сравнения методов одномерной оптимизации:
- пассивный поиск
- дихотомия
- золотое сечение
- метод касательных (Ньютона)
- метод секущих (по производной)

## Запуск

### Python (разработка)
```bash
pip install -r requirements.txt
python main.py
# или
streamlit run app/app.py
```

### Готовый exe файл
```bash
# Запуск через bat файл
run_optimization.bat

# Или прямой запуск
dist\optimization_proxy.exe
```

## Структура проекта
- `app/app.py` — Streamlit UI
- `app/optim/methods.py` — реализация методов с подробными докстрингами
- `app/optim/selection.py` — выбор подходящего метода
- `app/visualize.py` — вспомогательная визуализация итераций
- `main.py` — точка входа для Python
- `proxy_app.py` — прокси-приложение для exe
- `dist/optimization_proxy.exe` — готовый исполняемый файл
