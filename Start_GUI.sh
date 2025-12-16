#!/bin/bash

# Ermittelt den verfügbaren Python-Befehl
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
else
  PYTHON_CMD="python"
fi

# Erstellt virtuelle Umbgebung ".venv" falls sie nicht existiert
if [ ! -d ".venv" ]; then
  echo "Virtuelle Python Umgebung wird erstellt..."
  $PYTHON_CMD -m venv .venv
  
  # Aktiviert Umgebung und installiert Abhängigkeiten
  echo "Umgebung wird Aktiviert..."
  source .venv/bin/activate
  
  echo "Abhängigkeiten werden Installiert..."
  pip install -r requirements.txt
  
else
  echo "Umgebung wird Aktiviert..."
  source .venv/bin/activate
fi

echo "Benutzeroberfläche wird gestartet..."
$PYTHON_CMD GUI.py

deactivate
read -p "Drücken Sie eine beliebige Taste, um fortzufahren..."

