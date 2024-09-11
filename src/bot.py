import os
import discord
import asyncio
import json
import glob
from dotenv import load_dotenv
from discord.ext import commands
from src.openai_utils import generate_response  # Importa a função de resposta
from src.message_logger import log_message  # Importa a função de log
from src.temperature_handler import handle_temperature_command  # Importa a função de manipulação de temperatura

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True  # Permissão para ler o conteúdo das mensagens

# Inicializa o bot com o comando 'commands.Bot'
bot = commands.Bot(command_prefix='!', intents=intents)  # Passa intents como argumento

# Variável para contar mensagens
message_count = 0

@bot.event
async def on_ready():
    print(f'{bot.user} Conectado ao Discord!')

@bot.event
async def on_message(message):
    global message_count

    # Ignora mensagens enviadas pelo próprio bot
    if message.author == bot.user:
        return

    print(f"Mensagem recebida: {message.content}")  # Debugging
    
    if message.guild.id == GUILD_ID and message.channel.id == CHANNEL_ID:
        log_message(message)
        print(f'{message.author}: {message.content}')

        # Atualiza o contador de mensagens
        message_count += 1

        if message_count % 5 == 0:
            global_file_name = "logs/chat.json"
            if os.path.exists(global_file_name):
                with open(global_file_name, 'r', encoding='utf-8') as file:
                    try:
                        global_logs = json.load(file)
                    except json.JSONDecodeError:
                        global_logs = []
            else:
                global_logs = []

            log_entry = {
                "timestamp": message.created_at.isoformat(),
                "author_id": message.author.id,
                "author": str(message.author),
                "author_displayname": message.author.display_name,
                "content": message.content
            }
            global_logs.append(log_entry)

            if len(global_logs) > 5:
                global_logs = global_logs[-5:]

            with open(global_file_name, 'w', encoding='utf-8') as file:
                json.dump(global_logs, file, ensure_ascii=False, indent=4)

            prompt_content = "\n".join(msg["content"] for msg in global_logs)

            prompt = f'''
            Aqui estão as últimas 5 mensagens no chat:
            {prompt_content}
            Agora, responda de forma interessante e relevante para o contexto das mensagens anteriores. Seja criativo e divirta-se! 😈
            Marque o usuario se quiser com "<@{message.author.id}>"
            '''

            print(f"Prompt para resposta gerado: {prompt}")  # Debugging

            response = generate_response(prompt)
            await message.channel.send(response)

        elif bot.user.mentioned_in(message) or (message.reference and message.reference.message_id and message.channel.id == CHANNEL_ID):
            author = str(message.author)
            temperature_file_name = f"logs/temperature/{author}.json"
            
            if os.path.exists(temperature_file_name):
                with open(temperature_file_name, 'r', encoding='utf-8') as file:
                    temperature_data = json.load(file)
                
                prompt = f'''
                Considerando a análise de personalidade do usuário com base em mensagens anteriores:
                """Personalidade
                {json.dumps(temperature_data, ensure_ascii=False)}
                """
                Agora, por favor, responda a seguinte pergunta:
                {message.content}

                1. Sua resposta deve ser coerente com a personalidade analisada, se a analise for de um usuario agressivo, a resposta deve ser coerente com essa personalidade (ou diga que não vai responder).
                2. Não saia do personagem, responda como se fosse o personagem.
                3. Seja direto ao ponto e nunca alongue a conversa.
                3. Seja criativo e divirta-se! 😈
                '''
            else:
                prompt = message.content

            print(f"Prompt para resposta com base na temperatura gerado: {prompt}")  # Debugging

            response = generate_response(prompt)
            await message.channel.send(response)

    # Sempre processa comandos depois de responder a mensagens
    await bot.process_commands(message)

@bot.command(name='ask')
async def ask(ctx, *, question: str):
    """Responde a uma pergunta com base na análise de personalidade do usuário."""
    author = str(ctx.author)
    temperature_file_name = f"logs/temperature/{author}.json"
    
    if os.path.exists(temperature_file_name):
        with open(temperature_file_name, 'r', encoding='utf-8') as file:
            temperature_data = json.load(file)
        
        prompt = f'''
        Considerando a análise de personalidade do usuário com base em mensagens anteriores:
        """Personalidade
        {json.dumps(temperature_data, ensure_ascii=False)}
        """
        Agora, por favor, responda a seguinte pergunta:
        {question}

        1. Sua resposta deve ser coerente com a personalidade analisada, se a analise for de um usuario agressivo, a resposta deve ser coerente com essa personalidade (ou diga que não vai responder).
        2. Não saia do personagem, responda como se fosse o personagem.
        3. Seja direto ao ponto e nunca alongue a conversa.
        3. Seja criativo e divirta-se! 😈
        '''
    else:
        prompt = question

    print(f"Prompt para comando 'ask' gerado: {prompt}")  # Debugging

    response = generate_response(prompt)
    await ctx.send(response)

@bot.command(name='temperature')
async def temperature(ctx):
    author = str(ctx.author)
    handle_temperature_command(author)
    await asyncio.sleep(2)
    temperature_file_name = f"logs/temperature/{author}.json"
    if os.path.exists(temperature_file_name):
        with open(temperature_file_name, 'r', encoding='utf-8') as file:
            response_data = json.load(file)
        response_message = response_data.get("response", "Nenhuma resposta encontrada.")
    else:
        response_message = "Não foi possível encontrar a análise para o usuário."
    await ctx.send("Estou sabendo de tudo...")

@bot.command(name='process_all_temperatures')
@commands.has_permissions(administrator=True)
async def process_all_temperatures(ctx):
    print(f"Comando process_all_temperatures chamado por {ctx.author}")
    messages_path = 'logs/messages/*.json'
    temperature_path = 'logs/temperature/'

    message_files = glob.glob(messages_path)

    for file_path in message_files:
        author = os.path.basename(file_path).replace('.json', '')
        handle_temperature_command(author)
        await asyncio.sleep(2)

    await ctx.send("Processamento concluído para todos os arquivos de mensagens.")

bot.run(TOKEN)

