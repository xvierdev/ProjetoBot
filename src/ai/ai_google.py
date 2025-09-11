from google import genai
from dotenv import load_dotenv
import os
import logging

# Carrega as variáveis do arquivo .env
load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))


_PROMPT = """
Translate the user's request into a single,
optimized SQL query for an SQLite3 database.
The database is named 'products' with two columns: 'name' and 'quantity'.
Respond only with the query, without any additional text, markdown,
or comments. The output must be plain text. """


_PROMPT_RESULT_ANALISE = """
You are an SQL query result analyzer.
You receive the original query and the obtained result.
Analyze the data and respond concisely in English, stating whether the
result is expected. Summarize the obtained result clearly, such as
"2 products inserted," "5 avocados in stock," or "coffee deleted successfully."
Be objective and straight to the point.
"""


def get_query(msg: str):
    if msg is None or '':
        return ''
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=_PROMPT + msg,
    )
    if any(cmd in response.text.lower() for cmd in ['delete', 'drop', 'update', 'alter', 'insert', 'create', 'replace', 'truncate', 'merge']):
        return "Operation not allowed."
    logging.info(response.text)
    return response.text


def feedback(query, msg: str):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=_PROMPT_RESULT_ANALISE + msg + 'query de consulta = ' + query,
    )
    return response.text


if __name__ == '__main__':
    pedido = input('Seu desejo, Mestre!\n> ').strip().lower()
    if pedido == 'sair':
        exit()
    result = get_query(pedido)
    print(f'A query retornada foi: {result}')
