@echo off
REM --- 1. CONFIGURE SUA API KEY AQUI ---
REM Cole sua chave entre as aspas
set "GOOGLE_API_KEY=SUA_CHAVE_API_VAI_AQUI"

echo "Ativando ambiente virtual..."
call "%~dp0.venv\Scripts\activate.bat"

echo "Iniciando o script Python..."
REM CORREÇÃO AQUI: adicione "extrator\"
python "%~dp0extrator\ocr_extrair.py"

echo "Processo concluido."
pause
