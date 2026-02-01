@echo off
setlocal
REM =========================
REM Geeignete Python-Version finden (>=3.10)
set PYTHON_EXE=

for %%V in (3.13 3.12 3.11 3.10) do (
    py -%%V --version >nul 2>&1
    if ERRORLEVEL 0 (
        set PYTHON_EXE=py -%%V
        goto :found_python
    )
)

echo Kein Python >= 3.10 gefunden!
echo Installiere bitte Python 3.10 oder neuer:
echo https://www.python.org/downloads/
pause
exit /b 1

:found_python
echo Verwende %PYTHON_EXE%

REM === In Projektverzeichnis wechseln ===
cd /d "%~dp0"

REM === Python prüfen ===
%PYTHON_EXE% --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python wurde nicht gefunden.
    echo Bitte installiere Python und stelle sicher, dass es im PATH ist.
    pause
    exit /b 1
)

REM === Virtual Environment erstellen (falls nicht vorhanden) ===
IF NOT EXIST ".venv\" (
    echo Erstelle Virtual Environment...
    %PYTHON_EXE% -m venv .venv
)

REM === Virtual Environment aktivieren ===
echo Aktiviere Virtual Environment...
call .venv\Scripts\activate.bat

REM === pip aktualisieren ===
echo Aktualisiere PIP...
python -m pip install --upgrade pip setuptools wheel >nul

REM === Projekt installieren (editable) ===
echo Installiere Projekt...
pip install -e . || goto :error

REM === Programm starten ===
echo Starte Programm...
python -m can2csv

pause
exit /b 0

:error
echo Fehler bei der Installation oder beim Start.
pause
exit /b 1