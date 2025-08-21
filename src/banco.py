import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG, filename='debug.log')

DB_PATH = "demo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK(quantidade >= 0)
);
"""


def init_db():
    """Inicializa o banco de dados."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SCHEMA)
            conn.commit()
            logging.debug(f'Database {DB_PATH} criada com sucesso!')
    except sqlite3.Error as e:
        logging.error(f'Erro ao criar banco de dados: {e}')
    except Exception as e:
        logging.error(f'Erro inexperado: {e}')


def query_run(query: str) -> list | bool:
    """
    Executa uma query genérica (leitura ou escrita).

    Args:
        query(str): A query a ser executada.

    Returns:
        list: Resultado da consulta se SELECT, True/False para outras operações.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            if query.strip().lower().startswith("select"):
                result = conn.execute(query).fetchall()
                return result
            else:
                conn.execute(query)
                conn.commit()
                return True
    except Exception as e:
        logging.error(f'Erro ao executar query: {e}')
        return False if not query.strip().lower().startswith("select") else []

if __name__ == "__main__":
    init_db()
    # script de teste

    from ai.ai_google import get_query
    while True:
        print('Qual a instrução?')
        ordem = input('\n> ')
        script = get_query(ordem)
        if script is not None:
            query_run(script)
