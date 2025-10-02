@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Iniciando servidor Flask...
cd backend
python app.py

pause