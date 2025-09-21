# -*- coding: utf-8 -*-
"""
Веб-приложение для визуализации методов одномерной оптимизации.
Использует Flask вместо Streamlit для лучшей совместимости с PyInstaller.
"""
import os
import sys
import json
import traceback
from flask import Flask, render_template_string, request, jsonify
from app.optim.methods import *
from app.optim.selection import auto_select_and_run
from app.visualize import plot_history_1d
import matplotlib
matplotlib.use('Agg')  # Используем неинтерактивный бэкенд
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# HTML шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Методы одномерной оптимизации</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; margin-bottom: 10px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; }
        .error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .success { background: #d4edda; border-color: #c3e6cb; color: #155724; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Визуализация методов одномерной оптимизации</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="function">Функция f(x):</label>
                <input type="text" id="function" name="function" value="(x-2)**2 + 3" required>
            </div>
            
            <div class="form-group">
                <label for="bounds">Интервал [a, b]:</label>
                <input type="text" id="bounds" name="bounds" value="0, 5" placeholder="a, b">
            </div>
            
            <div class="form-group">
                <label for="method">Метод:</label>
                <select id="method" name="method">
                    <option value="auto">Автоматический выбор</option>
                    <option value="passive">Пассивный поиск</option>
                    <option value="dichotomy">Дихотомия</option>
                    <option value="golden">Золотое сечение</option>
                    <option value="newton">Метод Ньютона</option>
                    <option value="secant">Метод секущих</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="tol">Точность:</label>
                <input type="number" id="tol" name="tol" value="1e-5" step="1e-8">
            </div>
            
            <div class="form-group">
                <label for="samples">Количество проб (для пассивного поиска):</label>
                <input type="number" id="samples" name="samples" value="50" min="10" max="1000">
            </div>
            
            <div class="form-group">
                <label for="x0">Начальная точка x0 (для Ньютона/секущих):</label>
                <input type="number" id="x0" name="x0" value="1" step="0.1">
            </div>
            
            <div class="form-group">
                <label for="x1">Вторая точка x1 (для секущих):</label>
                <input type="number" id="x1" name="x1" value="3" step="0.1">
            </div>
            
            <button type="submit">Запустить оптимизацию</button>
        </form>
        
        {% if result %}
        <div class="result {{ 'error' if result.error else 'success' }}">
            {% if result.error %}
                <h3>Ошибка:</h3>
                <p>{{ result.error }}</p>
            {% else %}
                <h3>Результат оптимизации:</h3>
                <p><strong>Метод:</strong> {{ result.method }}</p>
                <p><strong>Найденный минимум:</strong> x* = {{ "%.6f"|format(result.x_opt) }}</p>
                <p><strong>Значение функции:</strong> f(x*) = {{ "%.6f"|format(result.f_opt) }}</p>
                <p><strong>Количество итераций:</strong> {{ result.iterations }}</p>
                <p><strong>Время выполнения:</strong> {{ "%.4f"|format(result.execution_time) }} сек</p>
                
                {% if result.plot %}
                <h4>График процесса оптимизации:</h4>
                <img src="data:image/png;base64,{{ result.plot }}" alt="График оптимизации">
                {% endif %}
                
                {% if result.history %}
                <h4>Таблица итераций:</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Итерация</th>
                            <th>x</th>
                            <th>f(x)</th>
                            <th>Примечание</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in result.history %}
                        <tr>
                            <td>{{ row.iteration }}</td>
                            <td>{{ "%.6f"|format(row.x) }}</td>
                            <td>{{ "%.6f"|format(row.fx) }}</td>
                            <td>{{ row.note or "" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def make_callable(func_str):
    """Преобразует строку функции в callable объект."""
    try:
        # Безопасная замена x на переменную
        func_str = func_str.replace('x', 'x')
        # Создаем функцию
        func_code = f"def f(x): return {func_str}"
        local_vars = {}
        exec(func_code, {"math": __import__("math"), "numpy": __import__("numpy")}, local_vars)
        return local_vars['f']
    except Exception as e:
        raise ValueError(f"Ошибка в функции: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)
    
    try:
        # Получаем параметры из формы
        func_str = request.form.get('function', '(x-2)**2 + 3')
        bounds_str = request.form.get('bounds', '0, 5')
        method = request.form.get('method', 'auto')
        tol = float(request.form.get('tol', 1e-5))
        samples = int(request.form.get('samples', 50))
        x0 = float(request.form.get('x0', 1))
        x1 = float(request.form.get('x1', 3))
        
        # Парсим интервал
        bounds = tuple(map(float, bounds_str.split(',')))
        if len(bounds) != 2 or bounds[0] >= bounds[1]:
            raise ValueError("Неверный интервал [a, b]")
        
        # Создаем функцию
        f = make_callable(func_str)
        
        # Выбираем метод
        if method == 'auto':
            result = auto_select_and_run(f, bounds, tol, samples)
        elif method == 'passive':
            result = passive_search(f, bounds, samples)
        elif method == 'dichotomy':
            result = dichotomy(f, bounds, tol)
        elif method == 'golden':
            result = golden_section(f, bounds, tol)
        elif method == 'newton':
            # Для Ньютона нужна производная
            from sympy import symbols, diff, lambdify
            x_sym = symbols('x')
            f_sym = eval(func_str.replace('x', 'x_sym'))
            df_sym = diff(f_sym, x_sym)
            df = lambdify(x_sym, df_sym, 'numpy')
            d2f_sym = diff(df_sym, x_sym)
            d2f = lambdify(x_sym, d2f_sym, 'numpy')
            result = newton_tangent(f, df, d2f, x0, tol)
        elif method == 'secant':
            # Для секущих нужна производная
            from sympy import symbols, diff, lambdify
            x_sym = symbols('x')
            f_sym = eval(func_str.replace('x', 'x_sym'))
            df_sym = diff(f_sym, x_sym)
            df = lambdify(x_sym, df_sym, 'numpy')
            result = secant_on_gradient(f, df, x0, x1, tol)
        else:
            raise ValueError(f"Неизвестный метод: {method}")
        
        # Создаем график
        try:
            fig = plot_history_1d(f, result.history, bounds)
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            plot_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close(fig)
        except Exception as e:
            plot_base64 = None
            print(f"Ошибка создания графика: {e}")
        
        # Форматируем историю для таблицы
        history_table = []
        for i, (x, fx) in enumerate(result.history):
            history_table.append({
                'iteration': i + 1,
                'x': x,
                'fx': fx,
                'note': ''
            })
        
        return render_template_string(HTML_TEMPLATE, result={
            'method': result.method,
            'x_opt': result.x_opt,
            'f_opt': result.f_opt,
            'iterations': result.iterations,
            'execution_time': result.execution_time,
            'plot': plot_base64,
            'history': history_table,
            'error': None
        })
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, result={
            'error': str(e),
            'method': None,
            'x_opt': None,
            'f_opt': None,
            'iterations': 0,
            'execution_time': 0,
            'plot': None,
            'history': []
        })

if __name__ == '__main__':
    print("Запуск веб-приложения...")
    print("Откройте браузер и перейдите по адресу: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
