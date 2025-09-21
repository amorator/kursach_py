# -*- coding: utf-8 -*-
"""
Простой launcher для Streamlit приложения.
Запускает Streamlit напрямую без subprocess.
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем Streamlit
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Путь к app.py
    app_path = os.path.join(os.path.dirname(__file__), "app", "app.py")
    
    # Запускаем Streamlit
    sys.argv = ["streamlit", "run", app_path, "--server.headless", "true"]
    sys.exit(stcli.main())
