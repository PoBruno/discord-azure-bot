import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(dotenv_path='./.env')  # Ajuste o caminho se necessário

# Obter variáveis de ambiente
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))  # Convertendo para int
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Convertendo para int
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Imprimir valores para depuração
print(f"DISCORD_TOKEN: {TOKEN}")
print(f"GUILD_ID: {GUILD_ID}")
print(f"CHANNEL_ID: {CHANNEL_ID}")
print(f"ELEVENLABS_API_KEY: {ELEVENLABS_API_KEY}")







#import os
#import discord
#import asyncio
#from dotenv import load_dotenv
#from discord.ext import commands
#from src.elevenlabs import text_to_audio, delete_audio
#
## Carregar variáveis de ambiente
#load_dotenv()
#TOKEN = os.getenv('DISCORD_TOKEN')
#
## Configuração do bot
#intents = discord.Intents.default()
#intents.message_content = True
#intents.voice_states = True
#bot = commands.Bot(command_prefix='!', intents=intents)
#
#@bot.event
#async def on_ready():
#    print(f'Logged in as {bot.user.name}')
#
#@bot.command()
#async def falar(ctx, *, text):
#    # Gera o áudio a partir do texto
#    filename = 'output.mp3'
#    await text_to_audio(text, filename)
#
#    # Toca o áudio no canal de voz
#    if ctx.author.voice:
#        channel = ctx.author.voice.channel
#        voice_client = await channel.connect()
#
#        audio_source = discord.FFmpegPCMAudio(f'./music/{filename}')
#        voice_client.play(audio_source, after=lambda e: print('Done playing', e))
#
#        # Espera o áudio terminar
#        while voice_client.is_playing():
#            await asyncio.sleep(1)
#
#        # Desconecta e exclui o arquivo de áudio
#        await voice_client.disconnect()
#        delete_audio(filename)
#    else:
#        await ctx.send('Você não está em um canal de voz.')
#
## Executar o bot
#bot.run(TOKEN)
#