REM === In Projektverzeichnis wechseln ===
cd /d "%~dp0"

IF NOT EXIST ".venv\" (
    echo Zuerst install.bat ausfuehren!
    pause
    exit /b 1
)

REM === Virtual Environment aktivieren ===
echo Aktiviere Virtual Environment...
call .venv\Scripts\activate.bat

REM === Programm starten ===
echo Starte Can2Csv...
python -m can2csv

pause

