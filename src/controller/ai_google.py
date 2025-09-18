import os
import logging
from google import genai
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logging.error("API_KEY not found in environment variables.")
    raise ValueError(
        "The API key not found. Check .env file.")

client = genai.Client(api_key=API_KEY)


def _get_prompt(file_name: str = 'config.prompt'):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.error(f"File '{file_name}' not found.")
        raise


def get_query(msg: str, filter: bool = True):
    if not msg:
        return ''
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=_get_prompt('config.prompt') + msg
        )

        query = (response.text or '').strip()
        logging.debug(f"Query gerada: {query}")

        if not allow_destructive:
            destructive_commands = ['delete', 'drop', 'update', 'alter',
                                    'insert', 'create', 'replace', 'truncate', 'merge']
            if any(cmd in query.lower() for cmd in destructive_commands):
                return "Operação não permitida. Apenas consultas de leitura são suportadas."

        return query

    except FileNotFoundError:
        # A exceção já foi tratada em _get_prompt, mas a levantamos aqui para o chamador
        return "Erro: Arquivo de configuração de prompt não encontrado."
    except Exception as e:
        logging.error(f"Erro ao gerar a query: {e}")
        return "Erro ao processar a requisição. Por favor, tente novamente."
    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     contents=_get_prompt() + msg,
    # )
    # if filter and any(
    #         cmd in response.text.lower() if response.text != None else ''
    #         for cmd in ['delete', 'drop', 'update', 'alter', 'insert', 'create', 'replace', 'truncate', 'merge']):
    #     return "Operation not allowed."
    # logging.debug(response.text)
    # return response.text


def feedback(query, msg: str):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=_get_prompt('analyse.prompt') + msg +
        'original query = ' + query,
    )
    return response.text


if __name__ == '__main__':
    pedido = input('Test input > ').strip().lower()
    if pedido.strip().lower() in ('quit', 'exit', 'sair', 'fechar'):
        exit()
    result = get_query(pedido, True)
    print(f'{result=}')
