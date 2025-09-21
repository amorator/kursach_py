#!/usr/bin/env python3
"""
Flask веб-приложение для визуализации методов одномерной оптимизации.
Альтернатива Streamlit для PyInstaller.
"""

import sys
import os
import base64
import io
from flask import Flask, render_template_string, request
import matplotlib
matplotlib.use('Agg')  # Используем неинтерактивный бэкенд
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from typing import Callable, Dict, Any

# Добавляем путь к модулям приложения
if getattr(sys, 'frozen', False):
    # Запущено из exe
    base_path = sys._MEIPASS
    sys.path.insert(0, os.path.join(base_path, 'app'))
else:
    # Запущено из Python
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from optim.methods import OptimizationResult, passive_search, dichotomy, golden_section, newton_tangent, secant_on_gradient
from optim.selection import auto_select_and_run

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Методы одномерной оптимизации</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Методы одномерной оптимизации</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="function">Функция f(x):</label>
                <input type="text" id="function" name="function" value="{{ request.form.get('function', 'x**2 + 2*x + 1') }}" required>
                <small>Примеры: x**2 + 2*x + 1, sin(x), x**3 - 3*x**2 + 2</small>
            </div>
            
            <div class="form-group">
                <label for="a">Левая граница (a):</label>
                <input type="number" id="a" name="a" step="any" value="{{ request.form.get('a', '-5') }}" required>
            </div>
            
            <div class="form-group">
                <label for="b">Правая граница (b):</label>
                <input type="number" id="b" name="b" step="any" value="{{ request.form.get('b', '5') }}" required>
            </div>
            
            <div class="form-group">
                <label for="tol">Точность:</label>
                <input type="number" id="tol" name="tol" step="any" value="{{ request.form.get('tol', '1e-6') }}" required>
            </div>
            
            <div class="form-group">
                <label for="samples">Количество точек (для пассивного поиска):</label>
                <input type="number" id="samples" name="samples" value="{{ request.form.get('samples', '50') }}" min="10" max="1000">
            </div>
            
            <div class="form-group">
                <label for="x0">Начальная точка (для методов Ньютона и секущих):</label>
                <input type="number" id="x0" name="x0" step="any" value="{{ request.form.get('x0', '0') }}">
            </div>
            
            <div class="form-group">
                <label for="x1">Вторая точка (для метода секущих):</label>
                <input type="number" id="x1" name="x1" step="any" value="{{ request.form.get('x1', '1') }}">
            </div>
            
            <div class="form-group">
                <label for="prefer_method">Предпочитаемый метод:</label>
                <select id="prefer_method" name="prefer_method">
                    <option value="auto" {{ 'selected' if request.form.get('prefer_method') == 'auto' else '' }}>Автоматический выбор</option>
                    <option value="passive" {{ 'selected' if request.form.get('prefer_method') == 'passive' else '' }}>Пассивный поиск</option>
                    <option value="dichotomy" {{ 'selected' if request.form.get('prefer_method') == 'dichotomy' else '' }}>Дихотомия</option>
                    <option value="golden" {{ 'selected' if request.form.get('prefer_method') == 'golden' else '' }}>Золотое сечение</option>
                    <option value="newton" {{ 'selected' if request.form.get('prefer_method') == 'newton' else '' }}>Метод Ньютона</option>
                    <option value="secant" {{ 'selected' if request.form.get('prefer_method') == 'secant' else '' }}>Метод секущих</option>
                </select>
            </div>
            
            <button type="submit">Запустить оптимизацию</button>
        </form>
        
        {% if result %}
        <div class="result">
            {% if result.error %}
                <h3>Ошибка:</h3>
                <p>{{ result.error }}</p>
            {% else %}
                <h3>Результат оптимизации:</h3>
                <p><strong>Метод:</strong> {{ result.method }}</p>
                <p><strong>Найденный минимум:</strong> x* = {{ "%.6f"|format(result.x_min) }}</p>
                <p><strong>Значение функции:</strong> f(x*) = {{ "%.6f"|format(result.f_min) }}</p>
                <p><strong>Количество итераций:</strong> {{ result.iterations }}</p>
                <p><strong>Время выполнения:</strong> {{ "%.4f"|format(result.execution_time) }} сек</p>
                
                {% if result.plot %}
                <h4>График процесса оптимизации:</h4>
                <img src="data:image/png;base64,{{ result.plot }}" alt="Optimization Plot">
                {% endif %}
                
                {% if result.history %}
                <h4>История итераций:</h4>
                <table>
                    <thead>
                        <tr>
                            {% for key in result.history[0].keys() %}
                            <th>{{ key }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in result.history %}
                        <tr>
                            {% for key in result.history[0].keys() %}
                            <td>{{ "%.6f"|format(row[key]) if (row[key] is number) else row[key] }}</td>
                            {% endfor %}
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

def make_callable(expr_str: str) -> Callable[[float], float]:
    """Преобразует строковое выражение в функцию."""
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(expr_str)
        return sp.lambdify(x, expr, 'numpy')
    except Exception as e:
        raise ValueError(f"Ошибка парсинга функции: {e}")

def create_plot(result: OptimizationResult, f: Callable[[float], float], a: float, b: float) -> str:
    """Создает график процесса оптимизации."""
    try:
        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # График функции
        x_plot = np.linspace(a, b, 1000)
        y_plot = [f(x) for x in x_plot]
        ax.plot(x_plot, y_plot, 'b-', label='f(x)', linewidth=2)
        
        # Отмечаем найденный минимум
        ax.plot(result.x_min, result.f_min, 'ro', markersize=10, label=f'Минимум: x*={result.x_min:.4f}')
        
        # Добавляем точки из истории итераций
        if result.history:
            x_points = []
            y_points = []
            for step in result.history:
                if 'x' in step:
                    x_points.append(step['x'])
                    y_points.append(f(step['x']))
                elif 'x_min' in step:
                    x_points.append(step['x_min'])
                    y_points.append(f(step['x_min']))
            
            if x_points:
                ax.plot(x_points, y_points, 'go', markersize=6, alpha=0.7, label='Итерации')
        
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title(f'Оптимизация методом: {result.method}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Сохраняем в base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return plot_base64
    except Exception as e:
        print(f"Ошибка создания графика: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница приложения."""
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE, result=None)
    
    try:
        # Получаем параметры из формы
        function_str = request.form['function']
        a = float(request.form['a'])
        b = float(request.form['b'])
        tol = float(request.form['tol'])
        samples = int(request.form.get('samples', 50))
        x0 = float(request.form.get('x0', 0)) if request.form.get('x0') else None
        x1 = float(request.form.get('x1', 1)) if request.form.get('x1') else None
        prefer_method = request.form.get('prefer_method', 'auto')
        
        # Создаем функции
        f_callable = make_callable(function_str)
        
        # Производные (если нужны)
        df_callable = None
        d2f_callable = None
        if prefer_method in ['newton', 'secant'] or prefer_method == 'auto':
            try:
                x = sp.Symbol('x')
                expr = sp.sympify(function_str)
                df_expr = sp.diff(expr, x)
                d2f_expr = sp.diff(df_expr, x)
                df_callable = sp.lambdify(x, df_expr, 'numpy')
                d2f_callable = sp.lambdify(x, d2f_expr, 'numpy')
            except Exception:
                pass  # Производные не обязательны
        
        # Запускаем оптимизацию
        result: OptimizationResult = auto_select_and_run(
            f=f_callable,
            bounds=(a, b),
            tol=tol,
            samples=samples,
            df=df_callable,
            d2f=d2f_callable,
            x0=x0,
            x1=x1,
            prefer=prefer_method
        )
        
        # Создаем график
        plot_base64 = create_plot(result, f_callable, a, b)
        
        # Подготавливаем таблицу истории
        history_table = []
        for i, step in enumerate(result.history, start=1):
            row = {'iter': i}
            for k, v in step.items():
                try:
                    row[k] = float(v)
                except Exception:
                    row[k] = v
            history_table.append(row)
        
        return render_template_string(HTML_TEMPLATE, result={
            'method': result.method,
            'x_min': result.x_min,
            'f_min': result.f_min,
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
            'x_min': None,
            'f_min': None,
            'iterations': 0,
            'execution_time': 0,
            'plot': None,
            'history': []
        })

if __name__ == '__main__':
    print("Запуск веб-приложения...")
    print("Откройте браузер и перейдите по адресу: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
