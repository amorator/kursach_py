# -*- coding: utf-8 -*-
"""Тесты логики выбора метода (auto_select_and_run)."""
import pytest
from app.optim.selection import auto_select_and_run


def quad(x: float) -> float:
	"""Базовая квадратичная функция с минимумом в x=2."""
	return (x - 2.0) ** 2 + 3.0


def d_quad(x: float) -> float:
	"""Первая производная."""
	return 2.0 * (x - 2.0)


def d2_quad(x: float) -> float:
	"""Вторая производная (константа)."""
	return 2.0


def test_select_newton_when_derivatives_and_x0():
	res = auto_select_and_run(quad, bounds=None, df=d_quad, d2f=d2_quad, x0=0.0, tol=1e-10)
	assert abs(res.x_min - 2.0) < 1e-8
	assert res.method.startswith("Касательных")


def test_select_secant_when_two_starts():
	res = auto_select_and_run(quad, bounds=None, df=None, x0=0.0, x1=1.0, tol=1e-8)
	assert abs(res.x_min - 2.0) < 1e-6
	assert res.method.startswith("Секущих")


def test_select_passive_when_samples_given():
	res = auto_select_and_run(quad, bounds=(-5.0, 5.0), samples=21)
	assert res.method == "Пассивный поиск"


def test_select_golden_by_default_with_bounds():
	res = auto_select_and_run(quad, bounds=(-5.0, 5.0), tol=1e-5)
	assert res.method == "Золотое сечение"


def test_select_prefer_overrides():
	res = auto_select_and_run(quad, bounds=(-5.0, 5.0), tol=1e-5, prefer="dichotomy")
	assert res.method == "Дихотомия"


def test_select_raises_when_insufficient_data():
	with pytest.raises(ValueError):
		auto_select_and_run(quad)
