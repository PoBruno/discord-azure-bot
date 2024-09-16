import os
import json
import re
from src.openai_utils import generate_response  # Certifique-se de que a função generate_response está correta

def handle_temperature_command(author):
    # Caminho do arquivo JSON do usuário
    file_name = f"logs/messages/{author}.json"
    temperature_file_name = f"logs/temperature/{author}.json"

    # Verifica se o arquivo de mensagens existe
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []

        # Gera o prompt com o conteúdo das mensagens
        messages_content = [entry['content'] for entry in logs]
        prompt = f'''
```user_messages
{json.dumps(messages_content, ensure_ascii=False)}
```

```json_tamplate
{{
    "user_id": "exemplo_usuario",
    "personalidade": {{
        "agressividade_vs_passividade": {{
        "valor": ["Valor de 0 a 10"],
        "descricao": ["uma descricao breve"]
        }},
        "empatia_vs_frieza": {{
        "valor": ["Valor de 0 a 10"],
        "descricao": ["uma descricao breve"]
        }},
    "colaboracao_vs_egoismo": {{
        "valor": ["Valor de 0 a 10"],
        "descricao": ["uma descricao breve"]
        }},
    "otimismo_vs_pessimismo": {{
        "valor": ["Valor de 0 a 10"],
        "descricao": ["uma descricao breve"]
        }},
    "respeito_vs_desrespeito": {{
        "valor": ["Valor de 0 a 10"],
        "descricao": ["uma descricao breve"]
        }}
    }}
}}

1. Você irá realizar uma profunda analize de personalidade do histórico de mensagens de `user_messages` e ultilizar o `json_tamplate` como modelo para preencher cada valor `${[]}` do json de acordo com a analise.
a resposta tem que ser no formato json json_tamplate preenchido com os valores de 0 a 10 e uma descrição profunda de cada valor.
'''

# Obtém a resposta do OpenAI
        response = generate_response(prompt)

        if response:
            # Extrair a parte do JSON da resposta
            response_text = response.strip()
            # Encontrar a parte do JSON dentro dos delimitadores de código
            json_string_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_string_match:
                json_string = json_string_match.group(1)
                # Remover barras invertidas duplicadas
                json_string = json_string.replace(r'\\', r'\\')
                # Converter a string JSON para um objeto Python
                try:
                    parsed_json = json.loads(json_string)
                    # Formatando o JSON para exibição legível
                    formatted_json = json.dumps(parsed_json, indent=4, ensure_ascii=False)

                    # Prepara a resposta para salvar
                    response_json = {"response": formatted_json}
                    os.makedirs(os.path.dirname(temperature_file_name), exist_ok=True)
                    with open(temperature_file_name, 'w', encoding='utf-8') as file:
                        json.dump(response_json, file, ensure_ascii=False, indent=4)
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
            else:
                print("JSON não encontrado na resposta do OpenAI.")
        else:
            print("Não foi possível obter a resposta do OpenAI.")

    else:
        print(f"Arquivo {file_name} não encontrado para o usuário {author}.")

