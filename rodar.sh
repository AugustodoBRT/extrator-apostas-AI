#!/bin/bash

export GOOGLE_API_KEY="SUA_CHAVE_API_VAI_AQUI"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Ativando ambiente virtual..."
source "$SCRIPT_DIR/.venv/bin/activate"

echo "Iniciando o script Python..."
python "$SCRIPT_DIR/extrator/ocr_extrair.py"

deactivate
echo "Processo finalizado."
