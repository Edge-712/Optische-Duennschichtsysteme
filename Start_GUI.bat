@echo off
chcp 65001 >nul
:: Erstellt virtuelle Umbgebung ".venv" falls sie nicht existiert
if not exist ".venv" (
  echo Virtuelle Python Umgebung wird erstellt...
  python -m venv .venv
  
  :: Aktiviert Umgebung und installiert Abhängigkeiten
  echo Umgebung wird Aktiviert...
  call .venv\Scripts\activate
  
  echo Abhängigkeiten werden Installiert...
  pip install -r requirements.txt
  
  ) else (
  echo Umgebung wird Aktiviert...
  call .venv\Scripts\activate
)
echo Benutzeroberfläche wird gestartet...
python GUI.py

deactivate
pause
