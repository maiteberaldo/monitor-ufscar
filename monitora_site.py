# Importa as bibliotecas necessárias
import requests
import time
import smtplib
import hashlib
from email.message import EmailMessage
from bs4 import BeautifulSoup # <-- NOVA BIBLIOTECA

# --- CONFIGURAÇÕES ---
# Altere os valores abaixo com as suas informações

URL_A_VERIFICAR = "https://www.propq.ufscar.br/pt-br/iniciacao-cientifica/editais/pibic-pibic-af-pibiti-2025-2026"
SEU_EMAIL_GMAIL = "maiteberaldo@gmail.com"
SUA_SENHA_DE_APP = "zylgyoxvdxnuwmqf"
EMAIL_DESTINO = "maiteberaldo@gmail.com"
INTERVALO_SEGUNDOS = 300
ARQUIVO_HASH = "hash_site_ufscar.txt"
# -------------------

def enviar_email_notificacao():
    """
    Esta função constrói e envia o e-mail de notificação.
    """
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
    """
    Acessa a URL, extrai APENAS o conteúdo principal e retorna o hash.
    """
    try:
        resposta = requests.get(URL_A_VERIFICAR, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        resposta.raise_for_status()
        
        # Usa o BeautifulSoup para "entender" o HTML
        soup = BeautifulSoup(resposta.content, 'html.parser')
        
        # Encontra a parte específica da página que contém o conteúdo do edital.
        # O ID 'content-core' é o container principal do texto nesta página da UFSCar.
        conteudo_principal = soup.find(id='content-core')
        
        # Se não encontrar a área de conteúdo, retorna None para evitar erros.
        if not conteudo_principal:
            print("AVISO: Não foi possível encontrar a área de conteúdo principal ('content-core') na página.")
            return None
            
        # Cria um hash APENAS do conteúdo principal.
        return hashlib.md5(conteudo_principal.encode('utf-8')).hexdigest()
        
    except requests.exceptions.RequestException as e:
        print(f"AVISO: Falha ao acessar o site. Causa: {e}")
        return None

def monitorar_site():
    """
    Função principal que executa o loop de monitoramento.
    """
    print("--- Iniciando o Monitor de Site da UFSCar (Versão Melhorada) ---")
    hash_anterior = ""
    try:
        with open(ARQUIVO_HASH, 'r') as f:
            hash_anterior = f.read().strip()
        print("Registro anterior do site carregado com sucesso.")
    except FileNotFoundError:
        print("Nenhum registro anterior encontrado. Um novo será criado.")

    while True:
        print(f"\nVerificando o site em {time.strftime('%d/%m/%Y %H:%M:%S')}...")
        # Chama a nova função melhorada
        hash_novo = obter_hash_site_melhorado()

        if hash_novo:
            if not hash_anterior:
                print("Salvando o estado inicial do conteúdo do site.")
                with open(ARQUIVO_HASH, 'w') as f:
                    f.write(hash_novo)
                hash_anterior = hash_novo
            elif hash_novo != hash_anterior:
                enviar_email_notificacao()
                with open(ARQUIVO_HASH, 'w') as f:
                    f.write(hash_novo)
                hash_anterior = hash_novo
            else:
                print("Nenhuma mudança detectada no conteúdo principal.")
        
        print(f"Aguardando {INTERVALO_SEGUNDOS / 60:.0f} minutos para a próxima verificação...")
        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    if "seu-email" in SEU_EMAIL_GMAIL or "coloque_aqui" in SUA_SENHA_DE_APP:
        print("ERRO: Por favor, configure as variáveis 'SEU_EMAIL_GMAIL' e 'SUA_SENHA_DE_APP' no código antes de executar.")
    else:
        monitorar_site()
