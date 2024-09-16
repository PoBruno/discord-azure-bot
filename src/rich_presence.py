# rich_presence.py

import discord
import asyncio
import os
from discord.ext import tasks

# Função para configurar o Rich Presence
async def setup_presence():
    # Criar uma instância do RichPresence
    rpc = discord.Game(name="Música 🎵", type=discord.ActivityType.listening)
    return rpc

# Função para atualizar o Rich Presence de forma periódica
@tasks.loop(minutes=5)  # Atualiza a cada 5 minutos
async def update_presence(rpc, bot):
    # Exemplo: alternar entre diferentes atividades
    activities = [
        discord.Game(name="🎮 Jogando com amigos"),
        discord.Streaming(name="🎧 Mixando sons", url="https://twitch.tv/exemplo"),
        discord.Activity(type=discord.ActivityType.watching, name="🎬 Assistindo a série")
    ]

    # Escolher uma atividade aleatória da lista
    current_activity = activities[asyncio.get_event_loop().time() % len(activities)]

    # Atualizar a presença do bot
    await bot.change_presence(activity=current_activity)
    print(f"Rich Presence atualizado para: {current_activity.name}")

# Função para iniciar a tarefa de atualização do Rich Presence
def start_rich_presence_update(bot):
    # Setup inicial do Rich Presence
    rpc = asyncio.run(setup_presence())

    # Iniciar a tarefa de atualização recorrente
    update_presence.start(rpc, bot)
    print("Tarefa de atualização do Rich Presence iniciada.")
