# -*- coding: utf-8 -*-
"""Расширенные тесты: неунимодальные функции, шум и эффективность итераций."""
import math
import random
import numpy as np
import pytest

from app.optim.methods import (
	passive_search,
	golden_section,
	dichotomy,
)


def multimodal(x: float) -> float:
	"""Мультимодальная функция с несколькими минимумами на отрезке."""
	return math.sin(3*x) + 0.1*(x-1)**2


def noisy_quadratic(x: float) -> float:
	"""Слабо шумная квадратичная функция."""
	return (x-2.0)**2 + 3.0 + 1e-3*math.sin(50*x)


def test_multimodal_interval_methods_still_return_value():
	"""Интервальные методы должны возвращать конечные значения на мультимодальной функции."""
	res_g = golden_section(multimodal, (-2.0, 2.0), tol=1e-3)
	res_d = dichotomy(multimodal, (-2.0, 2.0), tol=1e-3)
	assert np.isfinite(res_g.f_min)
	assert np.isfinite(res_d.f_min)


def test_noisy_quadratic_interval_methods_robust():
	"""Интервальные методы сохраняют устойчивость при малом шуме."""
	res_g = golden_section(noisy_quadratic, (-5.0, 5.0), tol=1e-3)
	res_d = dichotomy(noisy_quadratic, (-5.0, 5.0), tol=1e-3)
	assert abs(res_g.x_min - 2.0) < 5e-2
	assert abs(res_d.x_min - 2.0) < 5e-2


def test_iteration_efficiency_golden_vs_passive():
	"""Золотое сечение обычно требует меньше итераций, чем пассивный поиск."""
	res_g = golden_section(lambda x: (x-1.2345)**2, (-10, 10), tol=1e-5)
	res_p = passive_search(lambda x: (x-1.2345)**2, (-10, 10), samples=401)
	assert res_g.iterations < res_p.iterations
