# Discord Azure Bot

Este é um bot simples para Discord que usa o Azure OpenAI para responder a perguntas.

## Requisitos

- Python 3.8 ou superior
- Uma conta de Discord e um token de bot
- Uma conta Azure com Azure OpenAI

## Configuração

1. Clone este repositório:

```bash
   git clone https://github.com/yourusername/discord-azure-bot.git
   cd discord-azure-bot
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



