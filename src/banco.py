import sqlite3
import logging

logging.basicConfig(level=logging.INFO, filename='debug.log')

DB_PATH = "demo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity >= 0)
);
"""


def init_db():
    """Inicializa o banco de dados."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SCHEMA)
            conn.commit()
            logging.info(f'Database {DB_PATH} criada com sucesso!')
    except sqlite3.Error as e:
        logging.error(f'Erro ao criar banco de dados: {e}')
    except Exception as e:
        logging.error(f'Erro inexperado: {e}')


def query_run(query: str):
    """
    Executa uma query genérica (leitura ou escrita).

    Args:
        query(str): A query a ser executada.

    Returns:
        list: Resultado da consulta se SELECT, True/False para outras
        operações.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            if query.strip().lower().startswith("select"):
                result = conn.execute(query).fetchall()
                logging.info('retorno da query: ' + str(result))
                # result = [data for data in result]
                textual = ';'.join([str(item) for item in result]).replace(
                    '(', '').replace(')', '')
                return textual
            else:
                conn.execute(query)
                conn.commit()
                logging.info(query + ' executada com sucesso.')
                return query + ' executada com sucesso.'
    except Exception as e:
        logging.error(f'Erro ao executar query: {e}')
        return False if not query.strip().lower().startswith("select") else []


if __name__ == "__main__":
    init_db()
    # script de teste

    # from ai.ai import get_query, feedback
    from ai.ai_google import get_query, feedback
    while True:
        query = input('Enter query here: ')
        if query == 'quit':
            break
        sql_query = get_query(query)
        feedback_msg = query_run(sql_query if sql_query is not None else '')
        msg = feedback(sql_query, str(feedback_msg))
        print(msg)
    # print(query_run('SELECT nome, quantidade FROM produtos'))
