# bot.py  
import os  
import discord  
import asyncio  
import json  
import glob  
from dotenv import load_dotenv  
from discord.ext import commands  
from src.openai_utils import generate_response  # Função para gerar resposta da OpenAI  
from src.message_logger import log_message  # Função para log de mensagens  
from src.temperature_handler import handle_temperature_command  # Função para manipulação de temperatura  
from src.rich_presence import setup_presence, update_presence, start_rich_presence_update  # Importar funções do rich_presence  
from src.music_handler import play_music  # Função para tocar música  
from src.elevenlabs import text_to_audio, delete_audio  
from elevenlabs import VoiceSettings, play, save  
from elevenlabs.client import ElevenLabs  
  
# Carregar variáveis de ambiente  
load_dotenv()  
TOKEN = os.getenv('DISCORD_TOKEN')  
GUILD_ID = int(os.getenv('GUILD_ID'))  
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')  
  
# Definir intenções do bot (inclui permissão para ler o conteúdo das mensagens)  
intents = discord.Intents.default()  
intents.message_content = True  
intents.voice_states = True  
  
# Inicializar o bot com o prefixo '!'  
bot = commands.Bot(command_prefix='!', intents=intents)  
  
message_count = 0  # Inicializa a variável `message_count`  
temperature_count = 0  # Inicializa a variável `temperature_count`  
  
# Evento quando o bot estiver pronto  
#@bot.event  
#async def on_ready():  
#    print(f'{bot.user} Conectado ao Discord!')  
#    rpc = await setup_presence()  # Aguarda a configuração do RPC  
#    #bot.loop.create_task(update_presence(rpc))  # Inicia a tarefa assíncrona para atualizar o Rich Presence  
#    start_rich_presence_update(bot)  
  
# Evento para quando uma mensagem for recebida  
@bot.event  
async def on_message(message):  
    # Declarar que usaremos a variável global  
    global message_count  
    global temperature_count  
  
    # Ignorar mensagens do próprio bot  
    if message.author == bot.user:  
        return  
  
    print(f"Mensagem recebida: {message.content}")  
  
    # Verificar se a mensagem contém algum conteúdo  
    if message.content.strip() == "":  
        print("Mensagem recebida, mas sem conteúdo.")  
        await bot.process_commands(message)  
        return  
  
    # Verificar se o bot foi mencionado ou se a mensagem é uma resposta a outra mensagem  
    if bot.user.mentioned_in(message) or (message.reference and message.reference.message_id):  
        print("Bot mencionado ou mensagem é uma resposta a outra mensagem.")  
        author = str(message.author)  
        temperature_file_name = f"logs/temperature/{author}.json"  
        music_plylist = f"music/queue.json"  
  
        # Se o arquivo de temperatura existe, criar o prompt com base na análise de personalidade  
        if os.path.exists(temperature_file_name):  
            with open(temperature_file_name, 'r', encoding='utf-8') as file:  
                temperature_data = json.load(file)  
  
            prompt = f'''  
                1. Você está participando do chat do Discord com seu grupo "Monga" e está interagindo com **{message.author}**  
                Personalidade de **{message.author}**:  
                ```{message.author}_personalidade  
                {json.dumps(temperature_data, ensure_ascii=False)}  
                ```  
                **{message.author}** mandou a mensagem:  
                ```  
                {message.content}  
                ```  
                2. Responda a mensagem de forma amigável e relevante para a personalidade de **{message.author}**.  
                "Sempre que for solicitação de música apenas responder com o comando `!play <nome da música e autor>` SEM NENHUMA INFORMAÇÃO A MAIS."  
                '''  
        else:  
            # Prompt se não houver análise de temperatura  
            prompt = f'''  
            1. Você está participando do chat do Discord com seu grupo "Monga" e está interagindo com **{message.author}**  
            **{message.author}** mandou a mensagem:  
            ```{message.author}_Message  
            {message.content}  
            ```  
            3. Agora, responda a mensagem de **{message.author}**  
            "Sempre que for solicitação de música, apenas responder com o comando `!play <nome da música e autor>` SEM NENHUMA INFORMAÇÃO A MAIS."  
            '''  
        print(f"Prompt gerado: {prompt}")  
        # Gerar e enviar a resposta  
        response = generate_response(prompt)  
        print(f"\n - - - - Azure OpenAI Prompt - - - - \n")  
        print(f"\nResposta gerada:\n {response}")  
  
        # Verificar se a resposta possui um comando de música  
        if "!play" in response:  
            # Extrair a música da resposta  
            song_request = response.split("!play", 1)[1].strip()  
            print(f"{song_request}")  
            print(f"Comando de música detectado: {song_request}")  
  
            # Chamar a função para tocar a música  
            await play_music(await bot.get_context(message), song_request)  
        else:  
            print(f"\n - - - Enviando resposta para o canal - - - \n")  
            await message.channel.send(response)  
  
    # Verificar se a mensagem é do canal correto no servidor correto  
    if message.guild.id == GUILD_ID and message.channel.id == CHANNEL_ID:  
        log_message(message)  
        print(f'{message.author}: {message.guild.name}')  
  
        # Incrementar o contador de mensagens  
        message_count += 1  
        temperature_count += 1  
  
        # TEMPERATURE_ALL  
        # TEMPERATURA Rodar a análise de personalidade a cada 100 mensagens  
        if temperature_count % 100 == 0:  
            async def process_all_temperatures(ctx):  
                print(f"Comando process_all_temperatures chamado por {ctx.author}")  
                messages_path = 'logs/messages/*.json'  
                temperature_path = 'logs/temperature/'  
  
                message_files = glob.glob(messages_path)  
                for file_path in message_files:  
                    author = os.path.basename(file_path).replace('.json', '')  
                    handle_temperature_command(author)  
                    await asyncio.sleep(2)  
  
                await ctx.send("Fiz umas análises legais aqui")  
  
        # INTERACAO ORGANICA  
        # Se o contador for múltiplo de 25, responder com base nas últimas 5 mensagens  
        if message_count % 25 == 0:  
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
  
            # Limitar as últimas 10 mensagens  
            if len(global_logs) > 10:  
                global_logs = global_logs[-10:]  
  
            # Salvar o log global  
            with open(global_file_name, 'w', encoding='utf-8') as file:  
                json.dump(global_logs, file, ensure_ascii=False, indent=4)  
  
            # Criar o prompt com base nos logs globais  
            prompt_content = "\n".join(msg["content"] for msg in global_logs)  
            prompt = f'''  
                1. Você está participando do chat do Discord com seu grupo "Monga"  
                Aqui estão as últimas mensagens no chat para contexto:  
                ```Mensagens  
                {prompt_content}  
                ```  
                2. Analise as últimas mensagens e escolha uma para responder.  
                3. Marque o usuário com "<@[author_id]>" caso queira.  
                3. Agora, responda a mensagem escolhida de forma interessante e relevante para o contexto das mensagens anteriores. Faça perguntas se achar interessante. Seja criativo e divirta-se! 😈  
                "Sempre que for solicitação de música, apenas responder com o comando `!play <nome da música e autor>` SEM NENHUMA INFORMAÇÃO A MAIS."  
                '''  
            print(f"Prompt gerado: {prompt}")  
            # Gerar e enviar a resposta  
            response = generate_response(prompt)  
            await message.channel.send(response)  
  
    # Processar comandos do bot  
    await bot.process_commands(message)  
  
# Comando para tocar música  
@bot.command(name='play')  
async def play(ctx, *, url: str):  
    # Adicionar um log para verificar a execução do comando  
    print(f"Comando !play acionado por {ctx.author} com URL: {url}")  
  
    # Chamar a função de manipulação de música  
    await play_music(ctx, url)  
  
# Eleven Labs  
# Comando para gerar e tocar áudio  
@bot.command(name='falar')  
async def falar(ctx, *, text: str):  
    # Verificar se o autor do comando está em um canal de voz  
    if ctx.author.voice is None:  
        await ctx.send('Você precisa estar em um canal de voz para usar este comando.')  
        return  
  
    # Conectar ao canal de voz do autor  
    channel = ctx.author.voice.channel  
    voice_client = await channel.connect()  
  
    try:  
        # Inicializar o cliente ElevenLabs  
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)  
        print("Cliente ElevenLabs inicializado.")  
  
        # Gerar áudio  
        print("Gerando o áudio...")  
        audio = client.generate(text=text, voice="Eric", model="eleven_multilingual_v2")  
  
        # Salvar o áudio em um arquivo temporário  
        print("Salvando o áudio...")  
        with open('output.mp3', 'wb') as f:  
            for chunk in audio:  
                f.write(chunk)  
  
        # Tocar o áudio no canal de voz  
        print("Tocando o áudio...")  
        voice_client.play(discord.FFmpegPCMAudio('output.mp3'), after=lambda e: print('Áudio finalizado.', e))  
  
        # Esperar o áudio terminar de tocar  
        while voice_client.is_playing():  
            await asyncio.sleep(1)  
        print("Áudio terminado.")  
  
    finally:  
        # Desconectar do canal de voz  
        print("Desconectando do canal de voz...")  
        await voice_client.disconnect()  
  
# Comando para manipular a temperatura do bot  
@bot.command(name='temperature')  
async def temperature(ctx):  
    # Get the author of the message  
    author = str(ctx.author)  
    handle_temperature_command(author)  
  
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
  
# Executar o bot  
bot.run(TOKEN)  
