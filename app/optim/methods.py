# -*- coding: utf-8 -*-
"""Методы одномерной оптимизации.

Содержит реализации и единый тип результата для визуализации итераций:
- passive_search: пассивный поиск (равномерное сканирование интервала)
- dichotomy: метод дихотомии
- golden_section: метод золотого сечения
- newton_tangent: метод касательных (Ньютона) по df и d2f
- secant_on_gradient: метод секущих, применяемый к уравнению f'(x)=0

Формат элементов history по методам:
- Пассивный поиск: {"x": float, "f": float}
- Дихотомия/золотое сечение: {"a": float, "b": float, "x1": float, "x2": float, "f1": float, "f2": float}
  Заключительная запись может быть {"a": float, "b": float, "x": float, "f": float}
- Ньютон: {"x": float, "df": float, "d2f": float, "f": float}
- Секущие: {"x": float, "g": float, "f": float}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class OptimizationResult:
	"""Результат работы метода оптимизации.

	Атрибуты:
		x_min: float
			Приближение к точке минимума.
		f_min: float
			Значение функции в точке минимума.
		iterations: int
			Количество выполненных итераций.
		history: List[Dict[str, Any]]
			История итераций для визуализации. Формат зависит от метода, но
			обычно содержит текущий интервал или точку и значение функции.
		method: str
			Название использованного метода.
	"""

	x_min: float
	f_min: float
	iterations: int
	history: List[Dict[str, Any]]
	method: str


def passive_search(
	f: Callable[[float], float],
	bounds: Tuple[float, float],
	samples: int = 50,
) -> OptimizationResult:
	"""Метод пассивного поиска (равномерное сканирование интервала).

	Метод равномерно разбивает отрезок [a, b] на заданное число точек и
	выбирает точку с наименьшим значением функции.

	Плюсы: простота, не требует дополнительных условий.
	Минусы: медленный, точность ограничена числом проб.

	Параметры:
		f: Callable[[float], float]
			Целевая функция одной переменной.
		bounds: Tuple[float, float]
			Интервал поиска (a, b), где a < b.
		samples: int, по умолчанию 50
			Количество равномерно распределенных пробных точек.

	Возвращает:
		OptimizationResult: результат оптимизации и история точек.

	Исключения:
		ValueError: если некорректен интервал или количество проб < 2.
	"""
	a, b = bounds
	if not (a < b):
		raise ValueError("Неверные границы интервала: требуется a < b")
	if samples < 2:
		raise ValueError("Число проб должно быть >= 2")

	xs = np.linspace(a, b, samples)
	history: List[Dict[str, Any]] = []
	f_vals = []
	for x in xs:
		fx = float(f(x))
		f_vals.append(fx)
		history.append({"x": float(x), "f": fx})

	idx = int(np.argmin(f_vals))
	x_min = float(xs[idx])
	f_min = float(f_vals[idx])
	return OptimizationResult(
		x_min=x_min,
		f_min=f_min,
		iterations=samples,
		history=history,
		method="Пассивный поиск",
	)


def dichotomy(
	f: Callable[[float], float],
	bounds: Tuple[float, float],
	tol: float = 1e-5,
	delta: Optional[float] = None,
	max_iter: int = 10_000,
) -> OptimizationResult:
	"""Метод дихотомии для поиска минимума на отрезке.

	На каждой итерации выбираются две близкие точки по разные стороны от
	середины интервала: x1 = m - δ, x2 = m + δ, где m — середина интервала.
	Сравнивая f(x1) и f(x2), сужаем интервал. Останавливаемся, когда длина
	интервала становится меньше tol или достигнут лимит итераций.

	Параметры:
		f: Callable[[float], float]
			Целевая функция.
		bounds: Tuple[float, float]
			Интервал (a, b), где a < b.
		tol: float, по умолчанию 1e-5
			Точность по длине интервала.
		delta: Optional[float]
			Малое положительное число для смещения от середины. Если None,
			берётся delta = tol / 2.
		max_iter: int
			Максимальное количество итераций.

	Возвращает:
		OptimizationResult: результат оптимизации с историей интервалов.

	Исключения:
		ValueError: при некорректных параметрах tol/delta или интервале.
	"""
	a, b = bounds
	if not (a < b):
		raise ValueError("Неверные границы интервала: требуется a < b")
	if tol <= 0:
		raise ValueError("tol должен быть > 0")
	if delta is None:
		delta = tol / 2.0
	if delta <= 0:
		raise ValueError("delta должен быть > 0")

	history: List[Dict[str, Any]] = []
	iterations = 0
	while (b - a) > tol and iterations < max_iter:
		m = (a + b) / 2.0
		x1 = m - delta
		x2 = m + delta
		f1 = float(f(x1))
		f2 = float(f(x2))
		history.append({"a": a, "b": b, "x1": x1, "x2": x2, "f1": f1, "f2": f2})
		if f1 < f2:
			b = x2
		else:
			a = x1
		iterations += 1

	x_min = (a + b) / 2.0
	f_min = float(f(x_min))
	history.append({"a": a, "b": b, "x": x_min, "f": f_min})
	return OptimizationResult(
		x_min=x_min,
		f_min=f_min,
		iterations=iterations,
		history=history,
		method="Дихотомия",
	)


def golden_section(
	f: Callable[[float], float],
	bounds: Tuple[float, float],
	tol: float = 1e-5,
	max_iter: int = 10_000,
) -> OptimizationResult:
	"""Метод золотого сечения для унимодальной функции на отрезке.

	Использует фиксированное отношение отрезков, основанное на золотом сечении,
	обеспечивая эффективное сужение интервала без пересчёта внутренних точек.

	Параметры:
		f: Callable[[float], float]
			Целевая функция.
		bounds: Tuple[float, float]
			Интервал (a, b), a < b.
		tol: float
			Критерий остановки по длине интервала.
		max_iter: int
			Максимальное количество итераций.

	Возвращает:
		OptimizationResult: результат с историей интервалов и точек.

	Исключения:
		ValueError: если интервал некорректен или tol <= 0.
	"""
	a, b = bounds
	if not (a < b):
		raise ValueError("Неверные границы интервала: требуется a < b")
	if tol <= 0:
		raise ValueError("tol должен быть > 0")

	phi = (1 + 5 ** 0.5) / 2
	resphi = 2 - phi

	x1 = a + resphi * (b - a)
	x2 = b - resphi * (b - a)
	f1 = float(f(x1))
	f2 = float(f(x2))

	history: List[Dict[str, Any]] = []
	iterations = 0
	while (b - a) > tol and iterations < max_iter:
		history.append({"a": a, "b": b, "x1": x1, "x2": x2, "f1": f1, "f2": f2})
		if f1 < f2:
			b, x2, f2 = x2, x1, f1
			x1 = a + resphi * (b - a)
			f1 = float(f(x1))
		else:
			a, x1, f1 = x1, x2, f2
			x2 = b - resphi * (b - a)
			f2 = float(f(x2))
		iterations += 1

	x_min = (a + b) / 2
	f_min = float(f(x_min))
	history.append({"a": a, "b": b, "x": x_min, "f": f_min})
	return OptimizationResult(
		x_min=x_min,
		f_min=f_min,
		iterations=iterations,
		history=history,
		method="Золотое сечение",
	)


def newton_tangent(
	f: Callable[[float], float],
	df: Callable[[float], float],
	d2f: Optional[Callable[[float], float]],
	x0: float,
	tol: float = 1e-6,
	max_iter: int = 100,
) -> OptimizationResult:
	"""Метод касательных (Ньютона) для поиска минимума.

	Итерационная схема: x_{k+1} = x_k - f'(x_k) / f''(x_k).
	Требует вычисления первой и второй производных. Если d2f не задан, метод
	не может быть применён напрямую.

	Параметры:
		f: Callable[[float], float]
			Целевая функция.
		df: Callable[[float], float]
			Первая производная функции.
		d2f: Optional[Callable[[float], float]]
			Вторая производная функции. Обязательна для метода Ньютона.
		x0: float
			Начальное приближение.
		tol: float
			Критерий остановки по норме шага и |f'(x)|.
		max_iter: int
			Максимум итераций.

	Возвращает:
		OptimizationResult: точка минимума, значение, история итераций.

	Исключения:
		ValueError: если не задана d2f.
		ZeroDivisionError: если f''(x) обращается в ноль на итерации.
	"""
	if d2f is None:
		raise ValueError("Для метода касательных требуется d2f (вторая производная)")

	history: List[Dict[str, Any]] = []
	x = float(x0)
	for _ in range(max_iter):
		g = float(df(x))
		h = float(d2f(x))
		history.append({"x": x, "df": g, "d2f": h, "f": float(f(x))})
		if abs(g) < tol:
			break
		if h == 0:
			raise ZeroDivisionError("d2f(x) = 0, метод Ньютона не применим")
		step = g / h
		x_new = x - step
		if abs(x_new - x) < tol:
			x = x_new
			break
		x = x_new

	x_min = x
	f_min = float(f(x_min))
	return OptimizationResult(
		x_min=x_min,
		f_min=f_min,
		iterations=len(history),
		history=history,
		method="Касательных (Ньютона)",
	)


def secant_on_gradient(
	f: Callable[[float], float],
	df: Optional[Callable[[float], float]],
	x0: float,
	x1: float,
	tol: float = 1e-6,
	max_iter: int = 200,
	h_fd: float = 1e-6,
) -> OptimizationResult:
	"""Метод секущих, применённый к уравнению f'(x) = 0 для минимума.

	Если аналитическая производная df недоступна, используется численное
	приближение производной по конечной разности:
		g(x) ≈ (f(x + h) - f(x - h)) / (2h)

	Итерации секущих: x_{k+1} = x_k - g(x_k) * (x_k - x_{k-1}) / (g(x_k) - g(x_{k-1})).

	Параметры:
		f: Callable[[float], float]
			Целевая функция.
		df: Optional[Callable[[float], float]]
			Первая производная, если доступна.
		x0: float
			Первое начальное приближение.
		x1: float
			Второе начальное приближение.
		tol: float
			Критерий остановки по |x_k - x_{k-1}| и |g(x_k)|.
		max_iter: int
			Максимум итераций.
		h_fd: float
			Шаг для численного дифференцирования, если df не задана.

	Возвращает:
		OptimizationResult: оценка минимума и история итераций.

	Исключения:
		— нет специальных, но возможна остановка по делению на малую разность градиентов.
	"""
	def grad(x: float) -> float:
		if df is not None:
			return float(df(x))
		return float((f(x + h_fd) - f(x - h_fd)) / (2.0 * h_fd))

	history: List[Dict[str, Any]] = []

	x_prev = float(x0)
	x_curr = float(x1)
	g_prev = grad(x_prev)
	g_curr = grad(x_curr)
	history.append({"x": x_prev, "g": g_prev, "f": float(f(x_prev))})
	history.append({"x": x_curr, "g": g_curr, "f": float(f(x_curr))})

	for _ in range(max_iter):
		if abs(g_curr - g_prev) < 1e-20:
			break
		x_next = x_curr - g_curr * (x_curr - x_prev) / (g_curr - g_prev)
		x_prev, g_prev = x_curr, g_curr
		x_curr = float(x_next)
		g_curr = grad(x_curr)
		history.append({"x": x_curr, "g": g_curr, "f": float(f(x_curr))})
		if abs(x_curr - x_prev) < tol or abs(g_curr) < tol:
			break

	x_min = x_curr
	f_min = float(f(x_min))
	return OptimizationResult(
		x_min=x_min,
		f_min=f_min,
		iterations=len(history),
		history=history,
		method="Секущих (по производной)",
	)
