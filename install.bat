@echo off
echo 🚀 Iniciando Instalacao do Extrator de Apostas com Gemini...

REM 1. Cria o ambiente virtual
echo 1. Criando ambiente virtual (.venv)...
python -m venv .venv
if errorlevel 1 goto error_venv
echo Ambiente virtual criado com sucesso.

REM 2. Ativa o ambiente virtual
echo 2. Ativando e instalando dependencias...
call .venv\Scripts\activate.bat

REM 3. Instala as dependências (localizadas na subpasta extrator\)
pip install -r extrator\requirements.txt
if errorlevel 1 goto error_pip

REM 4. Cria as pastas de trabalho
if not exist imagens mkdir imagens
if not exist imagens_processadas mkdir imagens_processadas
echo 4. Pastas de trabalho criadas.

REM 5. Adiciona marcadores para pastas vazias
type nul > imagens\.gitkeep
type nul > imagens_processadas\.gitkeep

echo.
echo ========================================================
echo ✅ INSTALACAO CONCLUIDA!
echo PROXIMO PASSO CRITICO:
echo 1. Edite o arquivo 'rodar.bat' e insira sua CHAVE DE API.
echo 2. Coloque seus screenshots na pasta 'imagens\'.
echo 3. Execute o programa com: rodar.bat
echo ========================================================
goto end

:error_venv
echo ERRO: Falha ao criar o ambiente virtual. Certifique-se de que o Python esta instalado.
pause
goto end

:error_pip
echo ERRO: Falha ao instalar dependencias. Verifique sua conexao.
pause
goto end

:end
REM Nao desativa o venv. O usuario deve fechar o CMD.
