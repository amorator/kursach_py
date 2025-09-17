# -*- coding: utf-8 -*-
"""Self-test: проверка реализованных методов одномерной оптимизации.

Запускается так:
	python selftest.py
"""
from __future__ import annotations

from typing import Tuple

from app.optim.methods import (
	passive_search,
	dichotomy,
	golden_section,
	newton_tangent,
	secant_on_gradient,
)


def quad(x: float) -> float:
	return (x - 2.0) ** 2 + 3.0


def d_quad(x: float) -> float:
	return 2.0 * (x - 2.0)


def d2_quad(x: float) -> float:
	return 2.0


def run_all() -> None:
	bounds: Tuple[float, float] = (-5.0, 5.0)
	print("Function: (x-2)^2 + 3; true minimum at x*=2, f*=3\n")

	# Пассивный поиск
	res = passive_search(quad, bounds, samples=101)
	print(f"[Пассивный] x_min={res.x_min:.6f}, f_min={res.f_min:.6f}, iters={res.iterations}")

	# Дихотомия
	res = dichotomy(quad, bounds, tol=1e-6)
	print(f"[Дихотомия] x_min={res.x_min:.6f}, f_min={res.f_min:.6f}, iters={res.iterations}")

	# Золотое сечение
	res = golden_section(quad, bounds, tol=1e-6)
	print(f"[Золотое] x_min={res.x_min:.6f}, f_min={res.f_min:.6f}, iters={res.iterations}")

	# Ньютон (касательных)
	res = newton_tangent(quad, d_quad, d2_quad, x0=0.0, tol=1e-10)
	print(f"[Ньютон] x_min={res.x_min:.12f}, f_min={res.f_min:.12f}, iters={res.iterations}")

	# Секущие по производной (аналитическая df)
	res = secant_on_gradient(quad, df=d_quad, x0=0.0, x1=1.0, tol=1e-10)
	print(f"[Секущие df] x_min={res.x_min:.12f}, f_min={res.f_min:.12f}, iters={res.iterations}")

	# Секущие по численному градиенту
	res = secant_on_gradient(quad, df=None, x0=0.0, x1=1.0, tol=1e-10)
	print(f"[Секущие num] x_min={res.x_min:.12f}, f_min={res.f_min:.12f}, iters={res.iterations}")

	print("\nOK: методы отработали. Проверьте численные значения, ожидаем x~2, f~3.")


if __name__ == "__main__":
	run_all()
