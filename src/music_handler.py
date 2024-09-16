import discord
from discord.ext import commands
import yt_dlp as youtube_dl  # Substitua youtube_dl por yt_dlp
import os
import asyncio
import json

# Caminho para o arquivo JSON da fila
QUEUE_FILE = './music/queue.json'
MUSIC_DIR = './music/youtube/'

# Cria a pasta de música se não existir
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

# Configurações do youtube_dl
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(MUSIC_DIR, '%(extractor)s-%(id)s-%(title)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Classe para gerenciar fontes de áudio do YouTube
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Função para carregar a fila de músicas do JSON
def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, 'r') as f:
        return json.load(f)

# Função para salvar a fila de músicas no JSON
def save_queue(queue):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=4)

# Adicionar uma música à fila
def add_to_queue(title, url):
    queue = load_queue()
    fila = len(queue) + 1
    queue.append({'title': title, 'url': url, 'fila': fila})
    save_queue(queue)

# Remover a música da fila após terminar de tocar e atualizar os valores de fila
def remove_from_queue():
    queue = load_queue()
    
    if queue:
        # Remove a primeira música (a que acabou de tocar)
        queue.pop(0)
        
        # Atualizar o valor da fila para os itens restantes
        for i, item in enumerate(queue):
            item['fila'] = i + 1
            
    save_queue(queue)

# Função para tocar a próxima música na fila
async def play_next(ctx):
    queue = load_queue()

    if queue and not ctx.voice_client.is_playing():
        next_song = queue[0]
        player = await YTDLSource.from_url(next_song['url'], loop=ctx.bot.loop)
        ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(on_song_end(ctx), ctx.bot.loop))
        await ctx.send(f'Tocando: {player.title}')

# Função chamada quando uma música termina
async def on_song_end(ctx):
    remove_from_queue()  # Remover a música que terminou
    await play_next(ctx)  # Tocar a próxima música

# função para inserir o bot no canal de voz com mais usuários
async def join_voice(ctx):
    voice_channels = ctx.guild.voice_channels
    if not voice_channels:
        await ctx.send("Não há canais de voz disponíveis para conectar.")
        return

    most_populated_channel = max(voice_channels, key=lambda vc: len(vc.members))

    if len(most_populated_channel.members) == 0:
        await ctx.send("Nenhum usuário está conectado a um canal de voz.")
        return

    channel = most_populated_channel
    await ctx.send(f"Conectando ao canal de voz: {channel.name} com {len(channel.members)} usuários.")
    await channel.connect()

# Função para tocar música
async def play_music(ctx, url):
    try:
        # Se o autor não estiver em um canal de voz
        if ctx.author.voice is None:
            print("Autor não está em um canal de voz, procurando o canal com mais usuários.")
            voice_channels = ctx.guild.voice_channels
            if not voice_channels:
                await ctx.send("Não há canais de voz disponíveis para conectar.")
                return

            most_populated_channel = max(voice_channels, key=lambda vc: len(vc.members))

            if len(most_populated_channel.members) == 0:
                await ctx.send("Nenhum usuário está conectado a um canal de voz.")
                return

            channel = most_populated_channel
            await ctx.send(f"Conectando ao canal de voz: {channel.name} com {len(channel.members)} usuários.")
        
        else:
            channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            print(f"Conectando ao canal de voz: {channel.name}")
            await channel.connect()

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=ctx.bot.loop)
            add_to_queue(player.title, url)  # Adicionar a música ao JSON
            if not ctx.voice_client.is_playing():  # Se nenhuma música estiver tocando, tocar a primeira
                await play_next(ctx)

    except Exception as e:
        await ctx.send(f'Ocorreu um erro: {str(e)}')
        print(f"Erro ao tentar tocar a música: {str(e)}")

