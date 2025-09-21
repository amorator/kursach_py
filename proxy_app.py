#!/usr/bin/env python3
"""
Простой запуск Streamlit приложения оптимизации.
"""

import subprocess
import time
import webbrowser
import sys
import os

def main():
    """Главная функция."""
    print("Запуск приложения оптимизации...")
    
    try:
        # Получаем путь к app.py
        if getattr(sys, 'frozen', False):
            # Запущено из exe
            base_path = sys._MEIPASS
            app_path = os.path.join(base_path, "app", "app.py")
        else:
            # Запущено из Python
            app_path = os.path.join(os.path.dirname(__file__), "app", "app.py")
        
        print(f"Запуск Streamlit приложения: {app_path}")
        
        # Запускаем Streamlit
        if getattr(sys, 'frozen', False):
            # В exe файле нужно использовать python из окружения
            python_exe = "python"
        else:
            python_exe = sys.executable
            
        cmd = [python_exe, "-m", "streamlit", "run", app_path, "--server.headless", "true"]
        print("Команда:", " ".join(cmd))
        
        # Открываем браузер через 2 секунды
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:8501')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Запускаем Streamlit
        result = subprocess.call(cmd)
        return result
        
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())