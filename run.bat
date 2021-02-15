@echo OFF

IF NOT EXIST .env (
    ECHO .env doesn't exist, you need to create one, aborting.
    PAUSE
    EXIT
)
IF EXIT venv\ (
	ECHO Activating venv.
	CALL venv/Scripts/activate.bat
	ECHO Running bot.
	python bot/main.py
) ELSE (
	ECHO No venv, aborting.
	PAUSE
	EXIT
)