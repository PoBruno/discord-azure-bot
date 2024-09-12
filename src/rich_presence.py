# src/rich_presence.py

import os
import asyncio
from pypresence import AioPresence
from dotenv import load_dotenv  

# Carregar variáveis de ambiente  
load_dotenv()  

CLIENT_ID = os.getenv('CLIENT_ID')

# Configurar o Rich Presence
async def setup_presence():
    """Configura e conecta o Presence do Discord."""
    rpc = AioPresence(CLIENT_ID)  # Usar AioPresence em vez de Presence
    await rpc.connect()  # Conectar ao RPC do Discord
    return rpc
    print(rcp)

async def update_presence(rpc):
    """Atualiza a presença do bot no Discord."""
    try:
        # Atualizar a presença com parâmetros básicos
        await rpc.update(
            state="Em desenvolvimento",
            details="Bot Discord em funcionamento",
            large_image="image_key",  # Substitua por uma chave de imagem válida
            large_text="Texto grande",  # Texto exibido ao passar o mouse sobre a imagem
            small_image="small_image_key",  # Substitua por uma chave de imagem válida
            small_text="Texto pequeno"  # Texto exibido ao passar o mouse sobre a imagem pequena
        )
        
        print("Presença atualizada com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar presença: {e}")

