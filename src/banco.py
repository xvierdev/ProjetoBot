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


def query_execute(query: str) -> bool:
    """
    Executa a query genérica.

    Args:
        query(str): a query a ser executada.

    Returns:
        bool: True em caso de sucesso, False em caso de falha.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(query)
            conn.commit()
            return True
    except Exception as e:
        logging.error(f'Erro ao executar query: {e}')
        return False


def query_read(query: str) -> list:
    """
    Executa uma query de consulta..

    Args:
        query(str): A query de consulta na database.

    Returns:
        list: Uma lista com os dados obtidos.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            result = conn.execute(query).fetchall()
            return result
    except Exception as e:
        logging.error(f"Erro ao ler query: {e}")
        return []


if __name__ == "__main__":
    init_db()
    # script de teste

    from ai.ai_google import get_query
    while True:
        print('Qual a instrução?')
        ordem = input('\n> ')
        script = get_query(ordem)
        if script is not None:
            query_execute(script)
