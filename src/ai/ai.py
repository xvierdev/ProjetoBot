import logging
from ollama import Client

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    encoding='utf-8'
)

_PROMPT = """
You are a SQL script generator.
The default database is named 'produtos' and has two columns:
'name' and 'quantity'.
We are using SQLite3 in Python.
You will receive a request in text format.
Translate this request into a query.
Make query correct and optimizeds.
Show only the query without any text, comments, or Markdown.
The output should be plain text. """

client = Client()

client.create(
    model='db-assistent',
    from_='gemma3',
    system='You are a SQL script generator.',
    stream=False
)


def get_query(msg: str) -> str | None:
    if msg is None or '':
        return None
    result = client.generate(model='db-assistent',
                             prompt=_PROMPT+msg)['response']
    logging.info(result)
    return result


if __name__ == '__main__':
    result = get_query(input('teste: '))
    # if result is not None:
    #     result = result.split('</think>')[1].strip()
    print(result)

# print(response['message']['content'])
# or access fields directly from the response object
# print(response.message.content)
