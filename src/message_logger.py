import os
import json
from datetime import datetime

MAX_MESSAGES_PER_USER = 30
MAX_MESSAGES_GLOBAL = 10

def log_message(message):
    # Cria o nome do arquivo JSON com o nome do autor
    file_name = f"logs/messages/{message.author}.json"
    global_file_name = "logs/chat.json"

    # Cria o diretório logs se não existir
    if not os.path.exists('logs/messages'):
        os.makedirs('logs/messages')
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Formata a mensagem
    log_entry = {
        "timestamp": message.created_at.isoformat(),
        "author_id": message.author.id,
        "author": str(message.author),
        "author_displayname": message.author.display_name,
        "content": message.content
    }

    # Carrega as mensagens existentes no arquivo do usuário, ou cria uma nova lista
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            try:
                user_logs = json.load(file)
            except json.JSONDecodeError:
                user_logs = []
    else:
        user_logs = []

    # Adiciona a nova mensagem ao log do usuário
    user_logs.append(log_entry)

    # Mantém apenas as últimas MAX_MESSAGES_PER_USER mensagens
    if len(user_logs) > MAX_MESSAGES_PER_USER:
        user_logs = user_logs[-MAX_MESSAGES_PER_USER:]

    # Escreve o log atualizado de volta ao arquivo JSON do usuário
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(user_logs, file, ensure_ascii=False, indent=4)

    # Carrega as mensagens globais existentes, ou cria uma nova lista
    if os.path.exists(global_file_name):
        with open(global_file_name, 'r', encoding='utf-8') as file:
            try:
                global_logs = json.load(file)
            except json.JSONDecodeError:
                global_logs = []
    else:
        global_logs = []

    # Adiciona a nova mensagem ao log global
    global_logs.append(log_entry)

    # Mantém apenas as últimas MAX_MESSAGES_GLOBAL mensagens
    if len(global_logs) > MAX_MESSAGES_GLOBAL:
        global_logs = global_logs[-MAX_MESSAGES_GLOBAL:]

    # Escreve o log atualizado de volta ao arquivo JSON global
    with open(global_file_name, 'w', encoding='utf-8') as file:
        json.dump(global_logs, file, ensure_ascii=False, indent=4)

