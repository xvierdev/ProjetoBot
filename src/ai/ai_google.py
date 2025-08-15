from google import genai
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))


_PROMPT = """
Você é um gerador de scripts sql, a base de dados
padrão se chama 'people' e só tem um campo 'name',
estamos usando sqlite no python,
você receberá um pedido na forma de texto,
traduza esse pedido em query,
mostre apenas a query sem textos nem comentários,
segue o pedido: """


def get_query(msg: str) -> str | None:
    if msg is None or '':
        return None
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=_PROMPT + msg,
    )
    return response.text


if __name__ == '__main__':
    print('nossa base de dados se chama \'people\' e o campos disponível é \'name\'')
    pedido=input('Seu desejo, Mestre!\n> ')
    result = get_query(pedido)
    print(f'A query retornada foi: {result}')