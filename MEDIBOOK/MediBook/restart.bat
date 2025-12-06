@echo off
echo Stopping any running Flask servers...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Deleting old database...
if exist instance\medibook.db (
    del /F instance\medibook.db
    echo Database deleted.
) else (
    echo No database file found.
)

echo Starting Flask server...
python app.py
