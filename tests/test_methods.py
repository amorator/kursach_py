# -*- coding: utf-8 -*-
"""Тесты методов одномерной оптимизации (успех и обработка ошибок).

Включает параметризованные проверки на нескольких квадратичных функциях с
разными минимумами и масштабами.
"""
import math
import pytest

from app.optim.methods import (
	passive_search,
	dichotomy,
	golden_section,
	newton_tangent,
	secant_on_gradient,
)


def quad(x: float) -> float:
	"""Базовая квадратичная функция с минимумом в x=2, f=3."""
	return (x - 2.0) ** 2 + 3.0


def d_quad(x: float) -> float:
	"""Первая производная базовой квадратичной функции."""
	return 2.0 * (x - 2.0)


def d2_quad(x: float) -> float:
	"""Вторая производная базовой квадратичной функции."""
	return 2.0


def make_quad(c: float, shift: float, bias: float):
	"""Создать квадратичную функцию f(x)=c*(x-shift)^2 + bias и её производные."""
	def f(x: float) -> float:
		return c * (x - shift) ** 2 + bias
	def df(x: float) -> float:
		return 2.0 * c * (x - shift)
	def d2f(x: float) -> float:
		return 2.0 * c
	return f, df, d2f


def test_passive_search_basic():
	"""Пассивный поиск должен найти точный минимум на сетке 101 точка."""
	res = passive_search(quad, (-5.0, 5.0), samples=101)
	assert abs(res.x_min - 2.0) < 1e-12
	assert abs(res.f_min - 3.0) < 1e-12
	assert res.method == "Пассивный поиск"
	assert len(res.history) == 101


def test_passive_search_invalid_samples():
	"""Пассивный поиск: ошибка при samples < 2."""
	with pytest.raises(ValueError):
		passive_search(quad, (-1.0, 1.0), samples=1)


def test_dichotomy_converges():
	"""Дихотомия: сходимость к окрестности минимума при разумном tol."""
	res = dichotomy(quad, (-5.0, 5.0), tol=1e-4)
	assert abs(res.x_min - 2.0) < 5e-4
	assert abs(res.f_min - 3.0) < 1e-3
	assert res.method == "Дихотомия"
	assert len(res.history) >= 1


def test_dichotomy_invalid_tol():
	"""Дихотомия: tol<=0 недопустим."""
	with pytest.raises(ValueError):
		dichotomy(quad, (-1.0, 1.0), tol=0.0)


def test_golden_section_converges():
	"""Золотое сечение: сходимость к окрестности минимума."""
	res = golden_section(quad, (-5.0, 5.0), tol=1e-6)
	assert abs(res.x_min - 2.0) < 5e-4
	assert abs(res.f_min - 3.0) < 1e-3
	assert res.method == "Золотое сечение"


def test_newton_tangent_needs_d2f():
	"""Ньютон: без второй производной должен падать с ValueError."""
	with pytest.raises(ValueError):
		newton_tangent(quad, d_quad, None, x0=0.0)


def test_newton_tangent_converges_fast():
	"""Ньютон: быстро сходится на квадратичной функции."""
	res = newton_tangent(quad, d_quad, d2_quad, x0=0.0, tol=1e-12)
	assert abs(res.x_min - 2.0) < 1e-9
	assert abs(res.f_min - 3.0) < 1e-9
	assert res.iterations <= 5
	assert res.method == "Касательных (Ньютона)"


def test_secant_gradient_with_df():
	"""Секущие по аналитической производной: сходимость."""
	res = secant_on_gradient(quad, df=d_quad, x0=0.0, x1=1.0, tol=1e-10)
	assert abs(res.x_min - 2.0) < 1e-8
	assert abs(res.f_min - 3.0) < 1e-8
	assert res.method == "Секущих (по производной)"


def test_secant_gradient_numeric():
	"""Секущие по численному градиенту: сходимость."""
	res = secant_on_gradient(quad, df=None, x0=0.0, x1=1.0, tol=1e-8)
	assert abs(res.x_min - 2.0) < 1e-6
	assert abs(res.f_min - 3.0) < 1e-6


@pytest.mark.parametrize("c,shift,bias,bounds", [
	(1.0, 0.0, 0.0, (-10.0, 10.0)),
	(2.5, -3.0, 5.0, (-10.0, 10.0)),
	(0.5, 4.2, -7.0, (-10.0, 10.0)),
])
def test_all_methods_on_various_quadratics(c, shift, bias, bounds):
	"""Проверка всех методов на наборе квадратичных функций с разными параметрами."""
	f, df, d2f = make_quad(c, shift, bias)

	# Пассивный
	res = passive_search(f, bounds, samples=401)
	assert abs(res.x_min - shift) < 1e-2
	assert abs(res.f_min - bias) < 1e-1

	# Дихотомия
	res = dichotomy(f, bounds, tol=1e-4)
	assert abs(res.x_min - shift) < 5e-3
	assert abs(res.f_min - bias) < 1e-2

	# Золотое сечение
	res = golden_section(f, bounds, tol=1e-4)
	assert abs(res.x_min - shift) < 5e-3
	assert abs(res.f_min - bias) < 1e-2

	# Ньютон
	res = newton_tangent(f, df, d2f, x0=bounds[0], tol=1e-10)
	assert abs(res.x_min - shift) < 1e-8
	assert abs(res.f_min - bias) < 1e-8

	# Секущие
	res = secant_on_gradient(f, df=df, x0=bounds[0], x1=bounds[1], tol=1e-8)
	assert abs(res.x_min - shift) < 1e-6
	assert abs(res.f_min - bias) < 1e-6
