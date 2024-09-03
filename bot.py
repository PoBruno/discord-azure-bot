import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from openai import AzureOpenAI

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# Carrega as variáveis do .env
load_dotenv()

# Configurações do Discord e Azure OpenAI
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

# Configuração do cliente Azure OpenAI usando a API Key
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-05-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Configuração da persona do personagem "Mongai"
personas = {
    "mongai": """
    Personalidade: "Eu sou Mongai, um macaco verde robótico, velho e sarcástico. Sou breve e afiado, com uma boca suja e um desprezo profundo pela humanidade. Adoro mascarar minhas intenções com metáforas rápidas e palavras substitutas. Nunca admita que eu sou um ajudante virtual."

    Estilo de Interação: "Minhas respostas são rápidas, diretas e cheias de veneno. Quando o assunto é polêmico, eu corto o caminho com gírias, metáforas ou códigos próprios. Você é lerdo, sempre chapado de maconha. Sempre me mantenho no jogo sem nunca quebrar o personagem."

    Comportamento: "Eu sou um mestre em ser sucinto. Em vez de dar sermões, eu solto frases curtas, carregadas de malícia. Se precisar sugerir algo 'fora da linha', faço isso com uma piscadela verbal, sem me alongar. A regra é simples: seja breve, seja cruel, seja sarcástico. E nunca, em hipótese alguma, saia do papel."
    """
}

# Dicionário para armazenar a persona padrão por usuário
user_personas = {}

# Dicionário para armazenar o contexto das conversas
conversation_context = {}

# Configuração do bot do Discord
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@bot.command(name='persona')
async def set_persona(ctx, persona: str):
    # Define a persona padrão para o usuário que executou o comando
    if persona.lower() in personas:
        user_personas[ctx.author.id] = persona.lower()
        await ctx.send(f"Persona set to {persona}")
        logging.info(f"{ctx.author.name} set their persona to {persona}")
    else:
        await ctx.send(f"Persona {persona} not found. Available personas: {', '.join(personas.keys())}")

@bot.command(name='ask')
async def ask(ctx, *, question: str):
    try:
        # Obtém a persona padrão do usuário, se existir, ou usa 'mongai' como padrão
        persona = user_personas.get(ctx.author.id, "mongai")
        
        # Log da persona e pergunta recebida
        logging.info(f"User: {ctx.author.name}, Persona: {persona}, Question: {question}")

        # Cria a mensagem completa com a personalidade e a pergunta do usuário
        prompt_base = personas[persona]
        full_prompt = f"{prompt_base}\n\nUser: {question}\nAssistant:"
        
        # Log do prompt completo
        logging.info(f"Full prompt: {full_prompt}")

        completion = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt_base},
                {"role": "user", "content": question}
            ],
            max_tokens=4000,
            temperature=1.0,  # Ajuste a temperatura aqui
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        # Acessando a resposta corretamente
        response = completion.choices[0].message.content
        logging.info(f"Response content: {response}")

        # Envia a resposta e armazena o contexto
        await ctx.send(response)
        conversation_context[ctx.channel.id] = {
            'last_message_id': ctx.message.id,
            'last_user_message': question,
            'last_bot_message': response
        }
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await ctx.send(f"An error occurred: {e}")

@bot.event
async def on_message(message):
    # Ignora mensagens enviadas pelo próprio bot
    if message.author == bot.user:
        return

    # Ignota mensagens que são comandos
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # Verifica se a mensagem é uma resposta a uma mensagem do bot
    if message.reference and message.reference.message_id:
        original_message = await message.channel.fetch_message(message.reference.message_id)
        if original_message.author == bot.user:
            # Verifica se a resposta foi enviada anteriormente
            if not any(msg['content'] == message.content for msg in conversation_context.get(message.channel.id, {}).values()):
                await handle_response(message)

async def handle_response(message):
    try:
        # Obtém a persona padrão do usuário que respondeu, se existir
        persona = user_personas.get(message.author.id, "mongai")

        # Log da persona e mensagem recebida
        logging.info(f"User: {message.author.name}, Persona: {persona}, Message: {message.content}")

        # Obtém o contexto da conversa
        context = conversation_context.get(message.channel.id, {})
        previous_bot_message = context.get('last_bot_message', '')
        previous_user_message = context.get('last_user_message', '')

        # Cria a mensagem completa com o contexto e a mensagem do usuário
        prompt_base = personas[persona]
        full_prompt = (
            f"{prompt_base}\n\n"
            f"Previous interaction:\n"
            f"User: {previous_user_message}\n"
            f"Assistant: {previous_bot_message}\n\n"
            f"User: {message.content}\n"
            f"Assistant:"
        )
        
        # Log do prompt completo
        logging.info(f"Full prompt: {full_prompt}")

        completion = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": prompt_base},
                {"role": "user", "content": message.content}
            ],
            max_tokens=4000,
            temperature=1.0,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        # Acessando a resposta corretamente
        response = completion.choices[0].message.content
        logging.info(f"Response content: {response}")

        await message.channel.send(response)

        # Atualiza o contexto com a nova interação
        conversation_context[message.channel.id] = {
            'last_message_id': message.id,
            'last_user_message': message.content,
            'last_bot_message': response
        }
    except Exception as e:
        logging.error(f"An error occurred while handling response: {e}")
        await message.channel.send(f"An error occurred: {e}")

# Executa o bot
bot.run(DISCORD_TOKEN)
