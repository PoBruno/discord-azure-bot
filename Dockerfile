# Use a imagem base do Python 3.12
FROM python:3.12-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie o arquivo de requisitos para o container
COPY requirements.txt requirements.txt

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código fonte para o container
COPY src/ src/
COPY .env .env

# Defina a variável de ambiente para o bot
ENV PYTHONPATH=/app/src

# Defina o comando para iniciar o bot
CMD ["python", "-m", "src.bot"]
