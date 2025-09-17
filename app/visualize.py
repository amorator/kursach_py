# -*- coding: utf-8 -*-
"""Визуализация истории итераций одномерной оптимизации."""
from __future__ import annotations

from typing import Callable, Dict, Any, List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt


def plot_history_1d(
	f: Callable[[float], float],
	history: List[Dict[str, Any]],
	bounds: Optional[Tuple[float, float]] = None,
	title: str = "",
	points_only: bool = False,
):
	"""Построить график функции и отобразить историю итераций.

	Параметры:
		f: Callable[[float], float]
			Числовая функция одной переменной.
		history: List[Dict[str, Any]]
			Список шагов, сформированный методами оптимизации.
		bounds: Optional[Tuple[float, float]]
			Интервал визуализации функции. Если None — рисуются только точки.
		title: str
			Заголовок графика.
		points_only: bool
			Если True, функция не рисуется, только точки/интервалы.

	Возвращает:
		matplotlib.figure.Figure: объект фигуры с построенным графиком.
	"""
	fig, ax = plt.subplots(figsize=(7, 4))

	if bounds is not None and not points_only:
		a, b = bounds
		xs = np.linspace(a, b, 400)
		fx = [float(f(x)) for x in xs]
		ax.plot(xs, fx, label="f(x)", color="#1f77b4")

	# Рисуем историю
	for step in history:
		if "a" in step and "b" in step:
			a = float(step["a"])
			b = float(step["b"])
			ax.hlines(y=step.get("f", ax.get_ylim()[0]), xmin=a, xmax=b, colors="#ff7f0e", alpha=0.3)
			ax.vlines([a, b], *ax.get_ylim(), colors="#ff7f0e", alpha=0.05)
		if "x" in step:
			x = float(step["x"])
			ax.plot([x], [float(step.get("f", f(x)))], marker="o", color="#d62728", alpha=0.7)
		if "x1" in step and "x2" in step:
			x1 = float(step["x1"])
			x2 = float(step["x2"])
			ax.plot([x1, x2], [float(step.get("f1", f(x1))), float(step.get("f2", f(x2)))],
				marker="x", linestyle="none", color="#2ca02c", alpha=0.6)

	if title:
		ax.set_title(title)
	ax.set_xlabel("x")
	ax.set_ylabel("f(x)")
	ax.grid(True, alpha=0.2)
	ax.legend(loc="best")
	fig.tight_layout()
	return fig
