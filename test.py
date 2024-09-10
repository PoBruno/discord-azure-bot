import os
import json
from datetime import datetime
from dotenv import load_dotenv
import discord
import requests
import time
import openai

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

intents = discord.Intents.default()
intents.message_content = True  # Permissão para ler o conteúdo das mensagens

# Função para gerar resposta usando a Azure OpenAI API
def generate_response(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": DEPLOYMENT_NAME,
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 1.0,
        "top_p": 1.0,
    }
    
    response = requests.post(
        f"{ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/completions?api-version=2024-05-01-preview",
        headers=headers,
        json=data
    )
    
    response_json = response.json()
    if response.status_code == 200:
        return response_json['choices'][0]['text'].strip()
    else:
        return f"Error: {response_json.get('error', {}).get('message', 'Unknown error')}"

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.guild.id == GUILD_ID and message.channel.id == CHANNEL_ID:
        log_message(message)

def log_message(message):
    # Cria o nome do arquivo JSON com o nome do canal
    file_name = f"logs/{message.author}.json"

    # limitar o tamanho do arquivo de log
    if os.path.exists(file_name):
        if os.path.getsize(file_name) > 1024 * 1024:
            # Renomeia o arquivo para incluir a data e hora
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            os.rename(file_name, f"logs/{message.author}_{timestamp}.json")
    
    # Cria o diretório logs se não existir
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

    # Carrega as mensagens existentes no arquivo, ou cria uma nova lista
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            logs = json.load(file)
    else:
        logs = []

    # Adiciona a nova mensagem ao log
    logs.append(log_entry)

    # Escreve o log atualizado de volta ao arquivo JSON
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(logs, file, ensure_ascii=False, indent=4)

client.run(TOKEN)
