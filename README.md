
# Discord Azure Bot

## Visão Geral

O **Discord Azure Bot** é um bot inteligente projetado para interagir com os usuários no Discord de maneira dinâmica e personalizada. Utilizando a tecnologia Azure OpenAI, o bot não apenas responde às mensagens dos usuários, mas também analisa o comportamento e a personalidade de cada um, criando uma experiência única para cada interação.

## Funcionalidades

### Interação Personalizada

- **Resposta Adaptativa**: O bot analisa as últimas 30 mensagens de cada usuário e usa essa análise para adaptar suas respostas. Isso significa que o bot pode responder de maneira diferente para cada usuário, ajustando seu tom e estilo de comunicação com base na interação passada. Assim, o mesmo usuário pode receber respostas mais elegantes, mais diretas, ou até mesmo nenhuma resposta, dependendo do contexto.

### Armazenamento e Análise de Mensagens

- **Armazenamento de Mensagens**: O bot armazena todas as mensagens enviadas pelos usuários em um banco de dados. Isso é usado para entender melhor o estilo de comunicação e o comportamento de cada usuário.
- **Análise de Personalidade**: Através da análise das últimas 30 mensagens, o bot cria um perfil de personalidade para cada usuário. Esta análise é usada para personalizar as respostas e garantir que as interações sejam únicas e relevantes.

### Regra das 5 Mensagens

- **Interação a Cada 5 Mensagens**: O bot segue uma regra de interação que considera as últimas 5 mensagens no chat. Isso garante que o bot não responda a todas as mensagens, mas apenas a cada 5 mensagens, mantendo a conversa mais fluida e menos intrusiva.

## Como Funciona

1. **Análise Contínua**: O bot monitora as mensagens enviadas pelos usuários e armazena essas mensagens para análise futura.
2. **Geração de Resposta**: Com base na análise das últimas 30 mensagens, o bot gera uma resposta personalizada para cada usuário.
3. **Interação Específica**: O bot responde a cada 5 mensagens no chat, utilizando as últimas 5 mensagens para determinar a melhor forma de interagir.


---


## Requisitos

- Python 3.8 ou superior
- Uma conta de Discord e um token de bot
- Uma conta Azure com Azure OpenAI

## Deploy Manual

1. Clone este repositório:

```bash
git clone https://github.com/yourusername/discord-azure-bot.git
cd discord-azure-bot

python -m venv venv
source venv/bin/activate  # No Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
DISCORD_TOKEN=seu_discord_token_aqui
GUILD_ID=seu_guild_id
CHANNEL_ID=seu_channel_id
AZURE_OPENAI_API_KEY=sua_chave_openai_aqui
AZURE_OPENAI_ENDPOINT=seu_endpoint_openai
AZURE_OPENAI_DEPLOYMENT=nome_do_seu_deployment
```

4. Execute o bot:

```bash
python src/bot.py
```
## Deploy com Docker

1. Clone este repositório:

```bash
git clone https://github.com/yourusername/discord-azure-bot.git
cd discord-azure-bot
```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
DISCORD_TOKEN=seu_discord_token_aqui
GUILD_ID=seu_guild_id
CHANNEL_ID=seu_channel_id
AZURE_OPENAI_API_KEY=sua_chave_openai_aqui
AZURE_OPENAI_ENDPOINT=seu_endpoint_openai
AZURE_OPENAI_DEPLOYMENT=nome_do_seu_deployment
```

3. Construa a imagem Docker:

- Se estiver usando apenas o Dockerfile, execute:
```bash
docker build -t discord-azure-bot .
docker run -d --name discord-azure-bot --env-file .env discord-azure-bot

```

- Se estiver usando o Docker Compose, execute:
```bash
docker-compose up -d
```

## Estrutura

- `src/`: Contém o código-fonte do bot e suas funcionalidades.
- `logs/`: Diretório onde são armazenados os arquivos de log das mensagens.
- `.env`: Arquivo de variáveis de ambiente (não deve ser comitado).
- `requirements.txt`: Arquivo com as dependências do projeto.

```shell
discord-bot/
│
├── src/
│   ├── __init__.py            # Indica que o diretório é um módulo Python
│   ├── bot.py                 # Arquivo principal do bot que conecta tudo
│   ├── openai_utils.py        # Módulo de interação com Azure OpenAI
│   ├── message_logger.py      # Módulo responsável por registrar as mensagens
│   └── discord_utils.py       # Módulo de utilidades para interagir com a API do Discord
│   └── temperature_utils.py   # Módulo de utilidades para calcular a temperatura de resposta
│
├── logs/                      # Diretório onde serão salvos os arquivos de log em JSON
│
├── .env                       # Arquivo para variáveis de ambiente (não deve ser comitado)
├── requirements.txt           # Dependências do projeto
├── README.md                  # Arquivo de documentação
├── .gitignore                 # Arquivo para ignorar arquivos e pastas no Git
└── tests/
    ├── test_openai_utils.py    # Testes para a função que interage com a API da OpenAI
    ├── test_message_logger.py  # Testes para a função de logging

```



