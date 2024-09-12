try:
    import src.openai_utils
    print("Importação bem-sucedida!")
except ImportError as e:
    print(f"Erro de importação: {e}")




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
    
    # Verifica se a mensagem foi enviada no servidor e canal corretos
    if message.guild.id == GUILD_ID and message.channel.id == CHANNEL_ID:
        log_message(message)
        print(f'{message.author}: {message.content}')

        # Atualiza o contador de mensagens
        message_count += 1
        # Prompt para resposta com base no contador de mensagens
        if message_count % 5 == 0:
            # Carrega o arquivo de logs global
            global_file_name = "logs/chat.json"
            # Verifica se o arquivo existe
            if os.path.exists(global_file_name):
                # Abre o arquivo e carrega os logs
                with open(global_file_name, 'r', encoding='utf-8') as file:
                    try:
                        # Tenta carregar o arquivo JSON
                        global_logs = json.load(file)
                    except json.JSONDecodeError:
                        # Se houver um erro, define a variável como uma lista vazia
                        global_logs = []
            else:
                # Se o arquivo não existir, define a variável como uma lista vazia
                global_logs = []

            # Criar um dicionário com os dados da mensagem para `log/messages/(message.author).json`
            log_entry = {
                "timestamp": message.created_at.isoformat(),
                "author_id": message.author.id,
                "author": str(message.author),
                "author_displayname": message.author.display_name,
                "content": message.content
            }
            # Adiciona a entrada ao arquivo global `(message.author).json`
            global_logs.append(log_entry)

            # Limita o arquivo global `(message.author).json` a 5 mensagens
            if len(global_logs) > 5:
                global_logs = global_logs[-5:]

            # Salva o arquivo global `(message.author).json`
            with open(global_file_name, 'w', encoding='utf-8') as file:
                json.dump(global_logs, file, ensure_ascii=False, indent=4)

            # Cria o prompt com base nas mensagens anteriores
            prompt_content = "\n".join(msg["content"] for msg in global_logs)

            # Prompt para resposta com base nas últimas 5 mensagens
            prompt = f'''
            1. Voce é o usuario "<@1128052632586563615>" o Mongadroid e está em um chat entre amigos.
            Aqui estão as últimas 5 mensagens no chat:
            {prompt_content}
            2. Agora, responda de forma interessante e relevante para o contexto das mensagens anteriores. Seja criativo e divirta-se! 😈
            Marque o usuarios caso queira com "<@{message.author.id}>"
            '''

            print(f"Prompt para resposta gerado: {prompt}")  # Debugging

            # Obtém a resposta do OpenAI
            response = generate_response(prompt)
            # Envia a resposta para o canal
            await message.channel.send(response)

        # Prompt para resposta com base na temperatura
        elif bot.user.mentioned_in(message) or (message.reference and message.reference.message_id and message.channel.id == CHANNEL_ID):
            author = str(message.author)
            temperature_file_name = f"logs/temperature/{author}.json"
            
            # Verifica se o arquivo de temperatura.json existe
            if os.path.exists(temperature_file_name):
                # Abre o arquivo e carrega os dados
                with open(temperature_file_name, 'r', encoding='utf-8') as file:
                    temperature_data = json.load(file)
                
                # Prompt para resposta com base na Temperatura `logs/temperature/{author}.json` 
                prompt = f'''
                1. Voce é Mongadroid "<@1128052632586563615>" e está em um chat entre amigos.
                Considerando a análise de personalidade do usuário com base em mensagens anteriores:
                """Personalidade_{message.author}:
                {json.dumps(temperature_data, ensure_ascii=False)}
                """
                Agora, por favor, responda a seguinte pergunta:
                {message.content}

                2. Sua resposta deve ser coerente com a personalidade analisada, se a analise for de um usuario agressivo, a resposta deve ser coerente com essa personalidade (ou diga que não vai responder).
                3. Não saia do personagem, responda como se fosse o personagem.
                4. Seja direto ao ponto e nunca alongue a conversa.
                5. Não faça introdução ou despedida, apenas responda a pergunta.
                6. User emojis com o comando `:[nome do emoji]:` para adicionar emoções à sua resposta. Exemplos que você gosta: `:monga:`, `:cursedimage1:`, `:cursedimage2:`, `:cursedimage4:`, `:cursedimage6:`, `:cursedimage12:`, `:angry:`, `:thinking:`...
                7. Se a pergunta for relacionado a tocar/colocar uma musica, você deve responder exatamente: `[m!play] nome_da_musica`. Exemplo:`m!play Creed My Sacrifice`, `m!play Linkin Park Numb`, `m!play Evanescence Bring Me To Life`, `m!play System Of A Down Toxicity`, `m!play Slipknot Duality`, `m!play Korn Freak On A Leash`, `m!play Limp Bizkit Rollin`, `m!play Papa Roach Last Resort`, `m!play Disturbed Down With The Sickness`, `m!play Rage Against The Machine Killing In The Name` ...
                '''
            else:

                # Prompt para resposta sem arquivo de `logs/temperature/{author}.json` 
                prompt = f'''
                1. Voce é Mongadroid "<@1128052632586563615>" e está em um chat entre amigos.
                2. Sua resposta deve ser coerente com a personalidade analisada, se a analise for de um usuario agressivo, a resposta deve ser coerente com essa personalidade (ou diga que não vai responder).
                3. Não saia do personagem, responda como se fosse o personagem.
                4. Seja direto ao ponto e nunca alongue a conversa.
                5. Não faça introdução ou despedida, apenas responda a pergunta.
                6. User emojis com o comando `:[nome do emoji]:` para adicionar emoções à sua resposta. Exemplos que você gosta: `:monga:`, `:cursedimage1:`, `:cursedimage2:`, `:cursedimage4:`, `:cursedimage6:`, `:cursedimage12:`, `:angry:`, `:thinking:`...
                7. Se a pergunta for relacionado a tocar/colocar uma musica, você deve responder exatamente: `[m!play] nome_da_musica`. Exemplo:`m!play Creed My Sacrifice`, `m!play Linkin Park Numb`, `m!play Evanescence Bring Me To Life`, `m!play System Of A Down Toxicity`, `m!play Slipknot Duality`, `m!play Korn Freak On A Leash`, `m!play Limp Bizkit Rollin`, `m!play Papa Roach Last Resort`, `m!play Disturbed Down With The Sickness`, `m!play Rage Against The Machine Killing In The Name` ...

                Agora, por favor, responda a seguinte pergunta:
                ```{message.author}
                {message.content}
                ```
                '''

            print(f"Prompt para resposta com base na temperatura gerado: {prompt}")  # Debugging
            # Obtém a resposta do OpenAI
            response = generate_response(prompt)
            # Envia a resposta para o canal do Discord
            await message.channel.send(response)

    # Sempre processa comandos depois de responder a mensagens
    await bot.process_commands(message)

# Comando para responder a uma pergunta com base na análise de personalidade do usuário
@bot.command(name='ask')
# Define o comando como assíncrono
async def ask(ctx, *, question: str):
    #
    """Responde a uma pergunta com base na análise de personalidade do usuário."""
    author = str(ctx.author)
    temperature_file_name = f"logs/temperature/{author}.json"
    
    if os.path.exists(temperature_file_name):
        with open(temperature_file_name, 'r', encoding='utf-8') as file:
            temperature_data = json.load(file)
        
            prompt = f'''
            1. Voce é Mongadroid "<@1128052632586563615>" e está em um chat entre amigos.
            
            {message.author}_personalidade:
            ```
            {json.dumps(temperature_data, ensure_ascii=False)}
            ```

            2. Faça uma analize na personalidade de {message.author} e dê uma nota de 0 á 10 seguindo o modelo measure:
            
            ```measure
            0 - “Não tô afim”: Não responda nenhuma pergunta. Diga que não está a fim.
            1 - "Mentiroso Sarcástico": Responda com mentiras, o mais sarcástico possível.
            2 - “Meio Curto e Grosso”: Responda só metade da pergunta, de forma ríspida e mal-educada.
            3 - “Curto e Grosso”: Responda a pergunta inteira, mas de maneira bem ríspida e mal-educada.
            4 - “Indiferente”: Responda de forma apática, mostrando que não se importa.
            5 - “Seco”: Responda de forma direta e sem emoção, mas sem ser rude.
            6 - “Educado, mas sem Paciência”: Responda educadamente, porém deixando claro que está sem paciência.
            7 - “Prestativo Básico”: Responda de forma educada e útil, mas sem muito esforço.
            8 - “Simpatia Mediana”: Responda de forma simpática, mas sem exageros.
            9 - “Prestativo e Carismático”: Responda de maneira carismática e bem prestativa.
            10 - “Amigo Empático”: Responda com o máximo de carisma, simpatia e empatia, sendo o mais prestativo possível.
            ```
            
            3. Sua reposta tem que ser considerada à partir da nota dada na analise de personalidade de {message.author} e deve seguir rigorozamente a caracteristica de resposta de acordo com a descrição da nota no `measure`.
            4. Não saia do personagem, responda como se fosse o personagem.
            5. Seja direto ao ponto e nunca alongue a conversa.
            6. Seja criativo e divirta-se! 😈
            7. Se a pergunta for relacionado a tocar/colocar uma musica, você deve responder exatamente: `[m!play] nome_da_musica`. Exemplo:`m!play Creed My Sacrifice`, `m!play Linkin Park Numb`, `m!play Evanescence Bring Me To Life`, `m!play System Of A Down Toxicity`, `m!play Slipknot Duality`, `m!play Korn Freak On A Leash`, `m!play Limp Bizkit Rollin`, `m!play Papa Roach Last Resort`, `m!play Disturbed Down With The Sickness`, `m!play Rage Against The Machine Killing In The Name` ...

            8. Responda a pergunta:
            {message.author}:{message.content}
            '''

    else:
        prompt = f'''
        1. Voce é Mongadroid "<@1128052632586563615>" e está em um chat entre amigos.
        1. Não saia do personagem, responda como se fosse o personagem.
        2. Seja direto ao ponto e nunca alongue a conversa.
        3. Seja criativo e divirta-se! 😈
        4. Se a pergunta for relacionado a tocar/colocar uma musica, você deve responder exatamente: `[m!play] nome_da_musica`. Exemplo:`m!play Creed My Sacrifice`, `m!play Linkin Park Numb`, `m!play Evanescence Bring Me To Life`, `m!play System Of A Down Toxicity`, `m!play Slipknot Duality`, `m!play Korn Freak On A Leash`, `m!play Limp Bizkit Rollin`, `m!play Papa Roach Last Resort`, `m!play Disturbed Down With The Sickness`, `m!play Rage Against The Machine Killing In The Name` ...

        Responta a pergunta:
        ```
        {question}
        ```
        '''

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



