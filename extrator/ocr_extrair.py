import google.generativeai as genai
from PIL import Image
import csv
import os
import json
import datetime
import time 
import google.api_core.exceptions

# --- 1. Configuração da API Key (Lida pelo rodar.sh) ---
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Erro Crítico: A variável de ambiente GOOGLE_API_KEY não foi configurada.")
    print("Execute o script 'rodar.sh' ou 'rodar.bat', ou defina a variável manualmente.")
    exit(1)

genai.configure(api_key=api_key)

# --- 2. Configurações de Pastas (Pode alterar se desejar) ---
pasta_imagens_entrada = "imagens"
pasta_imagens_saida = "imagens_processadas"
caminho_csv_saida = "NOVAS_APOSTAS.csv"

if not os.path.exists(pasta_imagens_saida):
    os.makedirs(pasta_imagens_saida)

# --- 3. Modelos de IA e Prompt (Pode alterar os modelos e o prompt) ---
modelo_principal = "gemini-2.5-flash" 
modelo_secundario = "gemini-2.5-pro"  

prompt = f"""
Analise a imagem da aposta e extraia TODAS as apostas visíveis.
Para cada aposta, extraia as seguintes informações:

- esporte (ex: Futebol, Basquete, Tênis, NFL)
- partida: Siga esta lógica:
    1. Se for uma aposta em um ÚNICO jogo (Simples), escreva o nome da partida (ex: "Time A vs Time B").
    2. Se for uma aposta com MÚLTIPLOS jogos (ex: "Dupla", "Tripla", "Acumulada", "3 games", ou uma lista de jogos), escreva "Multipla".
    3. Se não for claro ou não se aplicar (ex: "Campeão da Liga"), retorne "".
- tip (A descrição da aposta, ex: "Menos de 2.5 Gols", "Handicap Asiático -1.5")
- odd (ex: 4.5)
- valor (o valor apostado, ex: "R$ 1.00"). Tenha MUITO CUIDADO com decimais (ex: "2.50" e não "250").
- casa (a casa de aposta, ex: "bet365"). Se não estiver visível, retorne "".

Responda APENAS em formato de uma LISTA JSON (um array). Cada aposta deve ser um objeto JSON dentro da lista.

EXEMPLO DE RESPOSTA (Uma simples e uma múltipla):
[
  {{
    "esporte": "Futebol",
    "partida": "Real Madrid vs Barcelona",
    "tip": "Mais de 2.5 Gols",
    "odd": "1.80",
    "valor": "R$ 10.00",
    "casa": "Betano"
  }},
  {{
    "esporte": "NFL",
    "partida": "Multipla",
    "tip": "Tripla - Packers, Chiefs e 49ers Para Vencerem",
    "odd": "5.50",
    "valor": "R$ 2.00",
    "casa": ""
  }}
]
"""

# --- 4. Colunas de Saída do CSV (Altere esta ordem se sua planilha for diferente) ---
colunas_csv = [
    "BLANK",
    "DATA",
    "ESPORTE",
    "PARTIDA",
    "TIP",
    "CASA",
    "VALOR",
    "ODD",
    "RESULTADO",
    "LUCRO/PERDA"
]

# --- Início da Lógica de Execução ---

try:
    arquivos_na_pasta = os.listdir(pasta_imagens_entrada)
except FileNotFoundError:
    print(f"Erro: A pasta de entrada '{pasta_imagens_entrada}' não foi encontrada.")
    exit(1)

imagens_para_processar = [
    f for f in arquivos_na_pasta 
    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
]

if not imagens_para_processar:
    print(f"Nenhuma imagem encontrada na pasta '{pasta_imagens_entrada}'. Saindo.")
    exit()

print(f"Encontradas {len(imagens_para_processar)} imagens. Iniciando processamento...")

NOMES_DOS_MODELOS = [modelo_principal, modelo_secundario]

try:
    modelos = {nome: genai.GenerativeModel(nome) for nome in NOMES_DOS_MODELOS}
    modelos_em_cooldown = {nome: 0 for nome in NOMES_DOS_MODELOS}
    print(f"Iniciando processamento com {len(modelos)} modelos em paralelo.")

except Exception as e:
    print(f"Erro FATAL ao inicializar os modelos da API: {e}")
    exit(1)


try:
    with open(caminho_csv_saida, "w", newline="", encoding="utf-8") as arquivo_csv:
        
        escritor = csv.DictWriter(arquivo_csv, fieldnames=colunas_csv)
        
        imagens_processadas_com_sucesso = 0
        
        for nome_arquivo in imagens_para_processar:
            caminho_completo_imagem = os.path.join(pasta_imagens_entrada, nome_arquivo)
            print(f"\n--- 🔄 Iniciando processamento para: {nome_arquivo} ---")
            
            imagem_processada_com_sucesso_nesta_iteracao = False
            
            while not imagem_processada_com_sucesso_nesta_iteracao:
                
                modelo_selecionado = None
                
                for nome_modelo in NOMES_DOS_MODELOS:
                    agora = time.time()
                    if agora > modelos_em_cooldown[nome_modelo]:
                        modelo_selecionado = nome_modelo
                        break 
                
                if modelo_selecionado is None:
                    print("  ...Todos os modelos estão em cooldown. Aguardando 10 segundos...")
                    time.sleep(10)
                    continue 

                print(f"  -> Usando modelo: {modelo_selecionado}")
                modelo_obj = modelos[modelo_selecionado]
                
                try:
                    imagem = Image.open(caminho_completo_imagem)
                    resposta = modelo_obj.generate_content([prompt, imagem])
                    
                    
                    # Fecha o arquivo de imagem para liberar o bloqueio do Windows
                    imagem.close()
                    
                    
                    print(f"  🔹 Resposta bruta: {resposta.text}")
                    
                    clean_text = resposta.text.strip().replace("```json", "").replace("```", "").strip()
                    if not clean_text:
                        raise json.JSONDecodeError("Resposta do modelo estava vazia.", "", 0)
                    
                    dados_lista_ia = json.loads(clean_text)

                    if isinstance(dados_lista_ia, dict):
                        dados_lista_ia = [dados_lista_ia]
                    elif not isinstance(dados_lista_ia, list):
                        raise TypeError("Resposta da IA não foi uma lista JSON.")

                    if not dados_lista_ia:
                        print(f"  ⚠️ Nenhuma aposta encontrada em '{nome_arquivo}'.")
                    
                    hoje = datetime.date.today()
                    data_completa_str = hoje.strftime("%d/%m/%Y")
                    
                    for i, dados_ia in enumerate(dados_lista_ia):
                        print(f"    -> Processando Aposta #{i+1}...")
                        
                        valor_apostado_str = dados_ia.get('valor', '0')
                        s_valor = valor_apostado_str.replace("R$", "").strip()
                        if "," in s_valor and "." in s_valor:
                            valor_limpo = s_valor.replace(".", "")
                        elif "." in s_valor and "," not in s_valor:
                            valor_limpo = s_valor.replace(".", ",")
                        else:
                            valor_limpo = s_valor
                        
                        odd_str = dados_ia.get('odd', '0')
                        odd_limpa = odd_str.replace(".", ",")
                        
                        # --- LÓGICA DE CLASSIFICAÇÃO DE ESPORTE (Pode alterar) ---
                        esportes_validos_map = {
                            "futebol": "Futebol",
                            "basquete": "Basquete",
                            "nfl": "NFL"
                            # Adicione mais se precisar, ex: "tênis": "Tênis",
                        }
                        
                        esporte_raw = dados_ia.get('esporte', '').strip().lower()
                        esporte_final = esportes_validos_map.get(esporte_raw, "Outros")
                        # --- FIM DA LÓGICA DE CLASSIFICAÇÃO ---

                        partida_str = dados_ia.get('partida', '') 
                        tip_str = dados_ia.get('tip', 'N/A')
                        casa_str = dados_ia.get('casa', '')
                        
                        dados_para_csv = {
                            "BLANK": "",
                            "DATA": data_completa_str,
                            "ESPORTE": esporte_final,
                            "PARTIDA": partida_str,
                            "TIP": tip_str,
                            "CASA": casa_str,
                            "VALOR": valor_limpo,
                            "ODD": odd_limpa,
                            "RESULTADO": "",
                            "LUCRO/PERDA": ""
                        }
                        
                        escritor.writerow(dados_para_csv) 
                        print(f"    ✅ Aposta #{i+1} salva no CSV.")
                    
                    caminho_destino = os.path.join(pasta_imagens_saida, nome_arquivo)
                    os.rename(caminho_completo_imagem, caminho_destino)
                    print(f"   Imagem '{nome_arquivo}' processada e movida.")
                    
                    imagens_processadas_com_sucesso += 1
                    imagem_processada_com_sucesso_nesta_iteracao = True

                except google.api_core.exceptions.ResourceExhausted as e:
                    print(f"  ⚠️ LIMITE ATINGIDO (429) para {modelo_selecionado}.")
                    print(f"  ...Colocando {modelo_selecionado} em cooldown por 60s...")
                    modelos_em_cooldown[modelo_selecionado] = time.time() + 60

                except Exception as e:
                    print(f"  ⚠️ ERRO NÃO RECUPERÁVEL ao processar '{nome_arquivo}'. Erro: {e}")
                    imagem_processada_com_sucesso_nesta_iteracao = True 
        
        print(f"\n--- Processamento Concluído ---")
        print(f"Total de imagens processadas com sucesso: {imagens_processadas_com_sucesso} de {len(imagens_para_processar)}")
        print(f"✅ Arquivo de saída limpo foi criado em: '{caminho_csv_saida}'")


except IOError as e:
    print(f"\nErro CRÍTICO ao abrir ou escrever no arquivo CSV '{caminho_csv_saida}': {e}")
except Exception as e:
    print(f"\nUm erro inesperado ocorreu fora do loop: {e}")
