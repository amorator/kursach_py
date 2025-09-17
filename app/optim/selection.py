# -*- coding: utf-8 -*-
"""Выбор и запуск подходящего метода одномерной оптимизации.

Функция auto_select_and_run инкапсулирует логику выбора алгоритма на
основании доступных данных: интервала, производных и стартовых точек.
"""
from __future__ import annotations

from typing import Callable, Optional, Tuple, Dict, Any

from .methods import (
	OptimizationResult,
	passive_search,
	dichotomy,
	golden_section,
	newton_tangent,
	secant_on_gradient,
)


def auto_select_and_run(
	f: Callable[[float], float],
	bounds: Optional[Tuple[float, float]] = None,
	tol: float = 1e-5,
	samples: Optional[int] = None,
	df: Optional[Callable[[float], float]] = None,
	d2f: Optional[Callable[[float], float]] = None,
	x0: Optional[float] = None,
	x1: Optional[float] = None,
	prefer: Optional[str] = None,
) -> OptimizationResult:
	"""Выбрать подходящий метод и выполнить оптимизацию.

	Правила выбора:
	- prefer задаёт принудительный метод ("passive", "dichotomy", "golden", "newton", "secant").
	- есть df и d2f и x0 → Ньютон;
	- есть два старта x0, x1 → секущие по производной (численной или аналитической);
	- задан только интервал → пассивный поиск (если указан samples) или золотое сечение.

	Параметры:
		f: Callable[[float], float]
			Целевая функция.
		bounds: Optional[Tuple[float, float]]
			Интервал поиска минимума.
		tol: float
			Точность для интервальных/производных методов.
		samples: Optional[int]
			Число проб для пассивного поиска.
		df: Optional[Callable[[float], float]]
			Первая производная (если доступна).
		d2f: Optional[Callable[[float], float]]
			Вторая производная (для Ньютона).
		x0: Optional[float]
			Начальное приближение.
		x1: Optional[float]
			Второе начальное приближение (для секущих).
		prefer: Optional[str]
			Явный выбор метода.

	Возвращает:
		OptimizationResult: результат выбранного метода с историей итераций.

	Исключения:
		ValueError: если данных недостаточно или противоречивы для выбранного метода.
	"""
	# Принудительный выбор
	if prefer is not None:
		key = prefer.lower()
		if key == "passive":
			if not bounds:
				raise ValueError("Для пассивного поиска нужен интервал bounds=(a,b)")
			if not samples:
				samples = 50
			return passive_search(f, bounds, samples)
		elif key == "dichotomy":
			if not bounds:
				raise ValueError("Для дихотомии нужен интервал bounds=(a,b)")
			return dichotomy(f, bounds, tol=tol)
		elif key == "golden":
			if not bounds:
				raise ValueError("Для золотого сечения нужен интервал bounds=(a,b)")
			return golden_section(f, bounds, tol=tol)
		elif key == "newton":
			if d2f is None or df is None or x0 is None:
				raise ValueError("Для Ньютона требуются df, d2f и начальное x0")
			return newton_tangent(f, df, d2f, x0=x0, tol=tol)
		elif key == "secant":
			if x0 is None or x1 is None:
				raise ValueError("Для метода секущих нужны два старта x0 и x1")
			return secant_on_gradient(f, df=df, x0=x0, x1=x1, tol=tol)
		else:
			raise ValueError("Неизвестное значение prefer")

	# Автовыбор
	if d2f is not None and df is not None and x0 is not None:
		return newton_tangent(f, df, d2f, x0=x0, tol=tol)

	if (x0 is not None) and (x1 is not None):
		return secant_on_gradient(f, df=df, x0=x0, x1=x1, tol=tol)

	if bounds is not None:
		if samples is not None:
			return passive_search(f, bounds, samples)
		# по умолчанию интервальный быстрый метод
		return golden_section(f, bounds, tol=tol)

	raise ValueError("Недостаточно данных для выбора метода. Укажите bounds или стартовые точки.")
