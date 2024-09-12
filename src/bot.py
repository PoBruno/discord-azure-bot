# bot.py

import os
import discord
import asyncio
import json
from dotenv import load_dotenv
from discord.ext import commands
from src.openai_utils import generate_response  # Função para gerar resposta da OpenAI
from src.message_logger import log_message  # Função para log de mensagens
from src.temperature_handler import handle_temperature_command  # Função para manipulação de temperatura
from src.rich_presence import setup_presence, update_presence  # Importar funções do rich_presence

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Definir intenções do bot (inclui permissão para ler o conteúdo das mensagens)
intents = discord.Intents.default()
intents.message_content = True

# Inicializar o bot com o prefixo '!'
bot = commands.Bot(command_prefix='!', intents=intents)

message_count = 0  # Inicializa a variável `message_count`

# Evento quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f'{bot.user} Conectado ao Discord!')
    rpc = await setup_presence()  # Aguarda a configuração do RPC
    bot.loop.create_task(update_presence(rpc))  # Inicia a tarefa assíncrona para atualizar o Rich Presence

# Evento para quando uma mensagem for recebida
@bot.event
async def on_message(message):
    global message_count  # Declarar que usaremos a variável global

    # Ignorar mensagens do próprio bot
    if message.author == bot.user:
        return

    # Verificar se a mensagem contém algum conteúdo
    if message.content.strip() == "":
        print("Mensagem recebida, mas sem conteúdo.")
        return

    # log da mensagem recebida no chat
    print(f"Mensagem recebida: {message.content}")

    # Verificar se a mensagem é do canal correto no servidor correto
    if message.guild.id == GUILD_ID and message.channel.id == CHANNEL_ID:
        log_message(message)
        print(f'{message.author}: {message.content}')

        # Incrementar o contador de mensagens
        message_count += 1

        # Se o contador for múltiplo de 5, responder com base nas últimas 5 mensagens
        if message_count % 10 == 0:
            global_file_name = "logs/chat.json"

            # Carregar logs globais ou criar um novo arquivo
            if os.path.exists(global_file_name):
                with open(global_file_name, 'r', encoding='utf-8') as file:
                    try:
                        global_logs = json.load(file)
                    except json.JSONDecodeError:
                        global_logs = []
            else:
                global_logs = []

            # Entrada de log
            log_entry = {
                "timestamp": message.created_at.isoformat(),
                "author_id": message.author.id,
                "author": str(message.author),
                "author_displayname": message.author.display_name,
                "content": message.content
            }
            global_logs.append(log_entry)

            # Limitar as últimas 5 mensagens
            if len(global_logs) > 5:
                global_logs = global_logs[-5:]

            # Salvar o log global
            with open(global_file_name, 'w', encoding='utf-8') as file:
                json.dump(global_logs, file, ensure_ascii=False, indent=4)

            # Criar o prompt com base nos logs globais
            prompt_content = "\n".join(msg["content"] for msg in global_logs)
            prompt = f'''
                1. Você é o usuário "<@1128052632586563615>", Mongadroid, e está em um chat entre amigos.
                Aqui estão as últimas 5 mensagens no chat:
                {prompt_content}
                2. Agora, responda de forma interessante e relevante para o contexto das mensagens anteriores. Seja criativo e divirta-se! 😈
                Marque o usuário com "<@{message.author.id}>" caso queira.
                '''

            print(f"Prompt gerado: {prompt}")

            # Gerar e enviar a resposta
            response = generate_response(prompt)
            await message.channel.send(response)

        # Se o bot foi mencionado ou houve uma resposta, gerar resposta com base na temperatura
        elif bot.user.mentioned_in(message) or (message.reference and message.reference.message_id):
            author = str(message.author)
            temperature_file_name = f"logs/temperature/{author}.json"

            # Se o arquivo de temperatura existe, criar o prompt com base na análise de personalidade
            if os.path.exists(temperature_file_name):
                with open(temperature_file_name, 'r', encoding='utf-8') as file:
                    temperature_data = json.load(file)

                prompt = f'''
                    1. Você é Mongadroid "<@1128052632586563615>" e está em um chat entre amigos.
                    Personalidade de {message.author}:
                    ```json
                    {json.dumps(temperature_data, ensure_ascii=False)}
                    ```
                    2. Faça uma análise da personalidade de {message.author} e dê uma nota de 0 a 10 seguindo o modelo measure:
                    ```measure
                    0 - “Não tô afim”: Não responda nenhuma pergunta. Diga que não está a fim.
                    1 - "Mentiroso Sarcástico": Responda com mentiras, o mais sarcástico possível.
                    2 - “Meio Curto e Grosso”: Responda só metade da pergunta, de forma ríspida e mal-educada.
                    3 - “Curto e Grosso”: Responda a pergunta inteira, mas de maneira bem ríspida e mal-educada.
                    4 - “Indiferente”: Responda de forma apática, mostrando que não se importa.
                    5 - “Seco”: Responda de forma direta e sem emoção, mas sem ser rude.
                    6 - “Educado, mas sem Paciência”: Responda educadamente, porém sem paciência.
                    7 - “Prestativo Básico”: Responda de forma educada e útil, mas sem muito esforço.
                    8 - “Simpatia Mediana”: Responda de forma simpática, mas sem exageros.
                    9 - “Prestativo e Carismático”: Responda de maneira carismática e prestativa.
                    10 - “Amigo Empático”: Responda com o máximo de carisma, simpatia e empatia.
                    ```
                    3. Responda de acordo com a nota dada e siga o comportamento correspondente.
                    '''
            else:
                # Prompt se não houver análise de temperatura
                prompt = f'''
                    1. Você é Mongadroid "<@1128052632586563615>" e está em um chat entre amigos.
                    2. Responda de forma amigável, mas direta e ao ponto, se o bot foi mencionado ou se há uma referência na mensagem.
                    '''

            print(f"Prompt gerado: {prompt}")

            # Gerar e enviar a resposta
            response = generate_response(prompt)
            await message.channel.send(response)

    # Processar comandos do bot
    await bot.process_commands(message)

# Comando para manipular a temperatura do bot
@bot.command(name='temperature')
# Definir a temperatura entre 0 e 10
async def temperature(ctx, temperature: int):
    if temperature < 0 or temperature > 10:
        await ctx.send('A temperatura deve estar entre 0 e 10.')
    else:
        handle_temperature_command(ctx, temperature)
        await ctx.send(f'Temperatura definida para {temperature}.')

# Executar o bot
bot.run(TOKEN)
