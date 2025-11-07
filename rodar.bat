@echo off
REM --- 1. CONFIGURE SUA API KEY AQUI ---
REM Cole sua chave entre as aspas
set "GOOGLE_API_KEY=SUA_CHAVE_API_VAI_AQUI"

echo "Ativando ambiente virtual..."
REM %~dp0 e o diretorio onde o .bat esta
call "%~dp0.venv\Scripts\activate.bat"

echo "Iniciando o script Python..."
python "%~dp0ocr_extrair.py"

echo "Processo concluido."
pause
