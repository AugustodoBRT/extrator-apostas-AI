import google.generativeai as genai
from PIL import Image
import csv
import os
import json
import datetime
import time
import google.api_core.exceptions

# --- 1. Função de Segurança de String ---
def safe_str(value):
    if value is None:
        return ""
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return str(value)
    return str(value).strip()

# --- 2. Função de Limpeza de Números ---
def clean_decimal(value_str):
    s = safe_str(value_str).replace("R$", "").strip()
    if not s:
        return "0.00"
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    return s

# --- 3. Configuração da API Key ---
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("\n❌ ERRO: Variável de ambiente GOOGLE_API_KEY não definida.")
    print("➡️ No Windows, abra o CMD e digite:\n")
    print('   setx GOOGLE_API_KEY "sua_chave_aqui"')
    print("\nDepois feche e abra o terminal novamente.\n")
    exit(1)

genai.configure(api_key=api_key)

# --- 4. Configurações de Pastas ---
pasta_imagens_entrada = "imagens"
pasta_imagens_saida = "imagens_processadas"
caminho_csv_saida = "NOVAS_APOSTAS_BETANALYTIX.csv"

os.makedirs(pasta_imagens_entrada, exist_ok=True)
os.makedirs(pasta_imagens_saida, exist_ok=True)

# --- 5. Mapa de Esportes ---
SPORT_MAP = {
    'football': 'Futebol',
    'futebol': 'Futebol',
    'soccer': 'Futebol',
    'basketball': 'Basquetebol',
    'tenis': 'Tênis',
    'tennis': 'Tênis',
    'nfl': 'NFL',
    'mma': 'MMA',
}
DEFAULT_SPORT = 'Outros'

# --- 6. Configuração de Modelos e Prompt ---
modelo_principal = "gemini-2.5-flash"
modelo_secundario = "gemini-2.5-pro"

prompt = """
Analise a imagem e extraia TODAS as apostas visíveis.
Retorne SOMENTE em formato JSON (array).

Cada aposta deve conter:
- date (YYYY-MM-DD HH:MM)
- type ("S" para Simples, "B" Back, "L" Lay)
- sport (em inglês, ex: "Football")
- competition (liga ou torneio)
- match (ex: "Flamengo - Palmeiras")
- bettype (ex: "Over 2.5 goals")
- bookmaker (ex: "Betano") (a casa sempre vai estar visível na imagem, se nao conseguir de jeito nenhum, escreva 10Bet)
- stake (valor apostado)
- odds (multiplicador da aposta)
"""

# --- 7. Colunas do CSV ---
colunas_csv = ['Date', 'Type', 'Sport', 'Label', 'Odds', 'Stake', 'State', 'Bookmaker']

# --- 8. Execução Principal ---
try:
    arquivos = [f for f in os.listdir(pasta_imagens_entrada)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not arquivos:
        print("⚠️ Nenhuma imagem encontrada na pasta 'imagens/'.")
        input("\nPressione Enter para sair...")
        exit()

    modelos = {
        "gemini-2.5-flash": genai.GenerativeModel(modelo_principal),
        "gemini-2.5-pro": genai.GenerativeModel(modelo_secundario)
    }

    with open(caminho_csv_saida, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=colunas_csv, delimiter=';')
        writer.writeheader()

        processadas = 0
        for arquivo in arquivos:
            caminho = os.path.join(pasta_imagens_entrada, arquivo)
            print(f"\n🔄 Processando {arquivo}...")

            imagem = Image.open(caminho)
            modelo_usado = modelo_principal
            resposta = None

            try:
                resposta = modelos[modelo_usado].generate_content([prompt, imagem])
                imagem.close()

                texto = resposta.text.strip().replace("```json", "").replace("```", "")
                apostas = json.loads(texto)

                if isinstance(apostas, dict):
                    apostas = [apostas]

                for aposta in apostas:
                    data_raw = safe_str(aposta.get('date', ''))
                    try:
                        dt = datetime.datetime.strptime(data_raw, "%Y-%m-%d %H:%M")
                        data_fmt = dt.strftime("%Y-%m-%d %H:%M:00")
                    except ValueError:
                        data_fmt = datetime.datetime.now().strftime("%Y-%m-%d 10:00:00")

                    stake = clean_decimal(aposta.get('stake', '0'))
                    odds = clean_decimal(aposta.get('odds', '0'))
                    sport = SPORT_MAP.get(safe_str(aposta.get('sport', '')).lower(), DEFAULT_SPORT)
                    tipo = safe_str(aposta.get('type', 'S')).upper()
                    if tipo not in ['S', 'B', 'L']:
                        tipo = 'S'
                    match = safe_str(aposta.get('match', ''))
                    bettype = safe_str(aposta.get('bettype', ''))
                    label = f"{match} - {bettype}" if match and bettype else match or bettype

                    linha = {
                        "Date": data_fmt,
                        "Type": tipo,
                        "Sport": sport,
                        "Label": label,
                        "Odds": odds,
                        "Stake": stake,
                        "State": "P",
                        "Bookmaker": aposta.get('bookmaker', '10Bet')
                    }
                    writer.writerow(linha)

                # Usa replace() pra evitar erro de permissão no Windows
                os.replace(caminho, os.path.join(pasta_imagens_saida, arquivo))
                processadas += 1
                print(f"✅ {arquivo} processada com sucesso.")

            except Exception as e:
                print(f"⚠️ Erro ao processar '{arquivo}': {e}")
                imagem.close()

    print(f"\n✅ Total de imagens processadas: {processadas}/{len(arquivos)}")
    print(f"📁 Arquivo CSV gerado: {caminho_csv_saida}")

except Exception as e:
    print(f"❌ Erro crítico: {e}")

input("\nPressione Enter para fechar...")
