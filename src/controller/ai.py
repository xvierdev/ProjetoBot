import logging
from ollama import Client

logging.getLogger(__name__)

_PROMPT = """
You are a SQL script generator.
The default database is named 'products' and has two columns:
'name' and 'quantity'.
We are using SQLite3 in Python.
You will receive a request in text format.
Translate this request into a query.
Make query correct and optimizeds.
Show only the query without any text, comments, or Markdown.
Do not use any markdown. Show only the query.
Do not show your thinking process. Respond directly with the query.
The output should be plain text.

Examples
Request: What's the total number of items?
Query: SELECT SUM(quantity) FROM products;

Request: Find all items with a quantity less than 10.
Query: SELECT name FROM products WHERE quantity < 10;

Request: Increase the quantity of 'apple' by 5.
Query: UPDATE products SET quantity = quantity + 5 WHERE name = 'apple';
"""

client = Client()

client.create(
    model='db-assistent',
    from_='qwen3:4b',
    system=_PROMPT,
    stream=False
)


def get_query(msg: str) -> str:
    if msg is None or '':
        return ''
    result = client.generate(
        model='db-assistent',
        prompt=msg,
        think=False,
        options={
            'temperature': 0.0
        }
    ).get('response')
    clean_result = _clean_query(result)
    logging.info(clean_result)
    return clean_result


def feedback(msg: str):
    result = client.generate(
        model='db-assistent',
        prompt='this is return of the last query:' + str(msg) +
        'respond succinctly and without embellishments, for example:' +
        ' \'data inserted successfully\' or' +
        ' \'inserted <num> of <items> successfully. ',
        think=False,
        options={
            'temperature': 0.0
        }
    ).get('response')
    return result


def _clean_query(query: str):
    level0 = query
    if '</think>' in query:
        level0 = query.split('</think>')[1]
    level1 = level0.replace('```sql', '').replace('```', '')
    level2 = level1.strip()
    return level2


if __name__ == '__main__':
    result = get_query(input('teste: '))
    # if result is not None:
    #     result = result.split('</think>')[1].strip()
    print(result)

# print(response['message']['content'])
# or access fields directly from the response object
# print(response.message.content)
