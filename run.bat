@echo OFF

ECHO Activating venv.
CALL venv/Scripts/activate.bat
ECHO Running bot.
python bot/main.py