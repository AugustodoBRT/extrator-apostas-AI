@echo off

echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

set "GOOGLE_API_KEY=COLE_SUA_CHAVE_COMPLETA_AQUI"

echo Iniciando o script Python...


python extrator\ocr_extrair.py

echo Processo finalizado.
pause
