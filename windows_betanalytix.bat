@echo off
REM --- CONFIGURAÇÃO ---
REM Cole sua chave de API aqui:
set GOOGLE_API_KEY=SUA-CHAVE-AQUI
REM --------------------

REM Obtém o diretório onde o script está
set SCRIPT_DIR=%~dp0

echo Ativando ambiente virtual...
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

echo Iniciando o script Python (Versão Bet-Analytix)...
python "%SCRIPT_DIR%extrator\ocr_extrair_betanalytix.py"

call deactivate
echo Processo concluído.
pause

