#!/bin/bash

# --- CONFIGURAÇÃO ---
# 1. Cole sua chave de API aqui
export GOOGLE_API_KEY="AIzaSyBjO3k_1rnpfucCiCzyo13Tmatkm77ddl4"

# 2. Encontra o diretório onde este script (rodar.sh) está
#    Isso torna o script portátil, não importa onde a pasta 'bet.py' esteja
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# --- EXECUÇÃO ---

# 3. Ativa o ambiente virtual (venv)
echo "Ativando ambiente virtual..."
source "$SCRIPT_DIR/.venv/bin/activate"

# 4. Executa o script Python
echo "Iniciando o script Python..."
python "$SCRIPT_DIR/ocr_extrair.py"

# 5. (Opcional) Desativa o venv ao terminar
deactivate
echo "Processo concluído."
