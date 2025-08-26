# Importa as bibliotecas necessárias
import requests
import time
import smtplib
import hashlib
from email.message import EmailMessage
from bs4 import BeautifulSoup # <-- NOVA BIBLIOTECA

# --- CONFIGURAÇÕES ---
# Importa as bibliotecas necessárias
import requests
import time
import smtplib
import hashlib
from email.message import EmailMessage
from bs4 import BeautifulSoup
import os # <-- IMPORTANTE: para ler os segredos

# --- CONFIGURAÇÕES (LIDAS DOS SEGREDOS DO GITHUB) ---
URL_A_VERIFICAR = "https://www.propq.ufscar.br/pt-br/iniciacao-cientifica/editais/pibic-pibic-af-pibiti-2025-2026"

# Pega as credenciais dos segredos do GitHub Actions
SEU_EMAIL_GMAIL = os.environ.get('GMAIL_USER')
SUA_SENHA_DE_APP = os.environ.get('GMAIL_PASS')

EMAIL_DESTINO = "maiteberaldo@gmail.com"
ARQUIVO_HASH = "hash_site_ufscar.txt"
# Não precisamos mais do intervalo, pois o GitHub Actions controla isso
# -------------------

def enviar_email_notificacao():
    # (O resto da função continua exatamente igual)
    print("MUDANÇA DETETADA! Preparando para enviar o e-mail...")
    msg = EmailMessage()
    msg.set_content(f"Olá!\n\nO conteúdo principal do edital da UFSCar parece ter sido atualizado.\n\nVerifique o link: {URL_A_VERIFICAR}")
    msg['Subject'] = 'Alerta: Possível Atualização no Edital da UFSCar'
    msg['From'] = SEU_EMAIL_GMAIL
    msg['To'] = EMAIL_DESTINO
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SEU_EMAIL_GMAIL, SUA_SENHA_DE_APP)
            smtp.send_message(msg)
        print("E-mail de notificação enviado com sucesso!")
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível enviar o e-mail. Causa: {e}")

def obter_hash_site_melhorado():
    # (Esta função continua exatamente igual)
    try:
        resposta = requests.get(URL_A_VERIFICAR, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.content, 'html.parser')
        conteudo_principal = soup.find(id='content-core')
        if not conteudo_principal:
            print("AVISO: Não foi possível encontrar a área de conteúdo principal ('content-core') na página.")
            return None
        return hashlib.md5(conteudo_principal.encode('utf-8')).hexdigest()
    except requests.exceptions.RequestException as e:
        print(f"AVISO: Falha ao acessar o site. Causa: {e}")
        return None

def monitorar_site():
    # (Esta função foi simplificada, pois não precisa mais do loop infinito)
    print("--- Iniciando o Monitor de Site da UFSCar via GitHub Actions ---")
    hash_anterior = ""
    try:
        with open(ARQUIVO_HASH, 'r') as f:
            hash_anterior = f.read().strip()
        print("Registro anterior do site carregado com sucesso.")
    except FileNotFoundError:
        print("Nenhum registro anterior encontrado. Um novo será criado.")

    print(f"Verificando o site em {time.strftime('%d/%m/%Y %H:%M:%S')}...")
    hash_novo = obter_hash_site_melhorado()

    if hash_novo:
        if not hash_anterior:
            print("Salvando o estado inicial do conteúdo do site.")
            with open(ARQUIVO_HASH, 'w') as f:
                f.write(hash_novo)
        elif hash_novo != hash_anterior:
            enviar_email_notificacao()
            with open(ARQUIVO_HASH, 'w') as f:
                f.write(hash_novo)
        else:
            print("Nenhuma mudança detectada no conteúdo principal.")
    
    print("--- Verificação concluída ---")


if __name__ == "__main__":
    if not SEU_EMAIL_GMAIL or not SUA_SENHA_DE_APP:
        print("ERRO: As credenciais GMAIL_USER e GMAIL_PASS não foram encontradas nos segredos do GitHub.")
    else:
        monitorar_site()


