import google.generativeai as genai
import os

# Carrega a chave da variável de ambiente
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Variável de ambiente GOOGLE_API_KEY não configurada.")
    
genai.configure(api_key=api_key)

print("Listando modelos disponíveis para sua chave de API:")

# Itera e imprime os modelos que suportam "generateContent"
for modelo in genai.list_models():
    if 'generateContent' in modelo.supported_generation_methods:
        print(f"- {modelo.name}")