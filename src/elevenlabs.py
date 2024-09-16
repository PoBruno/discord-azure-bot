import os
import aiohttp
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Carregar variáveis de ambiente
load_dotenv()

API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Configurar o cliente Eleven Labs
client = ElevenLabs(api_key=API_KEY)

async def text_to_audio(text, filename):
    try:
        # Gera o áudio a partir do texto
        audio = client.generate(
            text=text,
            voice="Eric",  # Defina a voz desejada
            model="eleven_multilingual_v2"  # Modelo de voz desejado
        )
        with open(f'./music/{filename}', 'wb') as f:
            f.write(audio)
        print(f'Áudio salvo como {filename}')
    except Exception as e:
        print(f'Erro ao criar o áudio: {e}')

def delete_audio(filename):
    file_path = f'./music/{filename}'
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f'Áudio {filename} deletado')
    else:
        print(f'Áudio {filename} não encontrado')
