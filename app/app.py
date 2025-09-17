# -*- coding: utf-8 -*-
"""Streamlit-приложение для визуализации методов одномерной оптимизации."""
from __future__ import annotations

import streamlit as st
import numpy as np
import sympy as sp
from typing import Optional, Tuple

from optim.methods import OptimizationResult
from optim.selection import auto_select_and_run
from visualize import plot_history_1d


st.set_page_config(page_title="1D Optimization", layout="centered")
st.title("Визуализация методов одномерной оптимизации")

with st.sidebar:
	st.header("Параметры")
	f_text = st.text_input("Функция f(x)", value="(x-2)**2 + 3")
	var = sp.symbols("x")

	col1, col2 = st.columns(2)
	with col1:
		a = st.number_input("a (левая граница)", value=-5.0, step=0.5)
	with col2:
		b = st.number_input("b (правая граница)", value=5.0, step=0.5)
	if a >= b:
		st.warning("Требуется a < b")
	bounds: Optional[Tuple[float, float]] = (a, b)

	method = st.selectbox(
		"Метод",
		["Автовыбор", "Пассивный поиск", "Дихотомия", "Золотое сечение", "Касательных (Ньютона)", "Секущих"],
	)

	tol = st.number_input("Точность tol", value=1e-5, format="%e")
	samples = st.number_input("Число проб (для пассивного поиска)", value=50, min_value=2, step=1)

	st.divider()
	st.caption("Начальные приближения (для методов производных)")
	x0 = st.number_input("x0", value=0.0)
	x1 = st.number_input("x1 (для секущих)", value=1.0)

	st.divider()
	with st.expander("Производные (опционально)"):
		df_text = st.text_input("f'(x)", value="")
		d2f_text = st.text_input("f''(x)", value="")


def make_callable(expr_text: str):
	"""Преобразовать текст выражения в числовую функцию одной переменной.

	Возвращает кортеж: (f, sympy_expr), где
	- f: вызываемая функция f(x) для численных расчётов;
	- sympy_expr: символьное выражение для возможного дальнейшего анализа.
	"""
	if not expr_text.strip():
		raise ValueError("Пустое выражение функции")
	expr = sp.sympify(expr_text)
	var = sp.symbols("x")
	f = sp.lambdify(var, expr, modules=["numpy", "math"])
	return f, expr


run = st.button("Запустить оптимизацию")

if run:
	try:
		f, f_expr = make_callable(f_text)
		# Производные (если заданы)
		df = None
		d2f = None
		if df_text.strip():
			_, df_expr = make_callable(df_text)
			df = sp.lambdify(sp.symbols("x"), df_expr, modules=["numpy", "math"])
		if d2f_text.strip():
			_, d2f_expr = make_callable(d2f_text)
			d2f = sp.lambdify(sp.symbols("x"), d2f_expr, modules=["numpy", "math"])

		prefer = None
		if method == "Пассивный поиск":
			prefer = "passive"
		elif method == "Дихотомия":
			prefer = "dichotomy"
		elif method == "Золотое сечение":
			prefer = "golden"
		elif method == "Касательных (Ньютона)":
			prefer = "newton"
		elif method == "Секущих":
			prefer = "secant"

		res: OptimizationResult = auto_select_and_run(
			f=f,
			bounds=bounds,
			tol=float(tol),
			samples=int(samples) if method in ("Пассивный поиск", "Автовыбор") else None,
			df=df,
			d2f=d2f,
			x0=float(x0),
			x1=float(x1),
			prefer=prefer if method != "Автовыбор" else None,
		)

		st.success(f"Метод: {res.method}")
		st.write(f"x_min ≈ {res.x_min:.8g}")
		st.write(f"f(x_min) ≈ {res.f_min:.8g}")
		st.write(f"Итераций: {res.iterations}")

		fig = plot_history_1d(f, res.history, bounds=bounds, title=res.method)
		st.pyplot(fig)

		# Таблица итераций
		st.subheader("Таблица итераций")
		rows = []
		for i, step in enumerate(res.history, start=1):
			row = {"iter": i}
			# Приводим значения к числам там, где возможно
			for k, v in step.items():
				try:
					row[k] = float(v)
				except Exception:
					row[k] = v
			rows.append(row)
		st.dataframe(rows, use_container_width=True)
	except Exception as e:
		st.error(str(e))
