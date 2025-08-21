from ollama import chat
from ollama import ChatResponse

_PROMPT = """
Você é um gerador de scripts sql, a base de dados
padrão se chama 'people' e só tem um campo 'name',
estamos usando sqlite no python,
você receberá um pedido na forma de texto,
traduza esse pedido em query,
mostre apenas a query sem textos nem comentários,
remova as marcas de markdown e mostre o texto puro
segue o pedido: """


def get_query(msg: str) -> str | None:
    if msg is None or '':
        return None
    response: ChatResponse = chat(model='qwen3:4b', messages=[
        {
            'role': 'user',
            'content': _PROMPT + msg,
        },
    ])
    return response.message.content


# print(response['message']['content'])
# or access fields directly from the response object
# print(response.message.content)
