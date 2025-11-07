#!/bin/bash

echo "🚀 Iniciando Instalação do Extrator de Apostas com Gemini..."

# Verifica se o Git está instalado
if ! command -v git &> /dev/null
then
    echo "ERRO: O Git não está instalado. Por favor, instale o Git e tente novamente."
    exit 1
fi

# 1. Cria o ambiente virtual
echo "1. Criando ambiente virtual (.venv)..."
if python3 -m venv .venv; then
    echo "Ambiente virtual criado com sucesso."
else
    echo "ERRO: Falha ao criar o ambiente virtual. Certifique-se de que o python3-venv está instalado."
    exit 1
fi

# 2. Ativa o ambiente virtual
source .venv/bin/activate
echo "2. Ambiente virtual ativado."

# 3. Instala as dependências (localizadas na subpasta extrator/)
echo "3. Instalando dependências (google-generativeai, pillow)..."
if pip install -r extrator/requirements.txt; then
    echo "Dependências instaladas com sucesso."
else
    echo "ERRO: Falha ao instalar dependências. Verifique sua conexão."
    deactivate
    exit 1
fi

# 4. Adiciona permissão de execução ao script rodar.sh
chmod +x rodar.sh
echo "4. Permissão de execução adicionada ao rodar.sh."

# 5. Cria as pastas de trabalho se não existirem
mkdir -p imagens imagens_processadas
echo "5. Pastas de trabalho 'imagens/' e 'imagens_processadas/' criadas."

# 6. Adiciona um marcador nas pastas vazias para o Git (opcional, mas bom)
touch imagens/.gitkeep
touch imagens_processadas/.gitkeep

echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "--------------------------------------------------------"
echo "PRÓXIMO PASSO CRÍTICO:"
echo "1. Edite o arquivo 'rodar.sh' e insira sua CHAVE DE API."
echo "2. Coloque seus screenshots na pasta 'imagens/'."
echo "3. Execute o programa com: ./rodar.sh"
echo "--------------------------------------------------------"

deactivate
