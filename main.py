# -*- coding: utf-8 -*-
"""Точка входа: запуск Streamlit-приложения через `python main.py`."""
import os
import sys
import subprocess


def main() -> int:
	"""Запустить Streamlit-приложение из файла app/app.py.

	Возвращает код завершения подпроцесса Streamlit.
	"""
	# Для PyInstaller: получаем путь к app.py относительно exe
	if getattr(sys, 'frozen', False):
		# Запущено из exe
		base_path = sys._MEIPASS
		app_path = os.path.join(base_path, "app", "app.py")
	else:
		# Запущено из Python
		app_path = os.path.join(os.path.dirname(__file__), "app", "app.py")
	
	cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.headless", "true"]
	return subprocess.call(cmd)


if __name__ == "__main__":
	sys.exit(main())
