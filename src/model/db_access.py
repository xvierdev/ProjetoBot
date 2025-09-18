import logging
import sqlite3

logging.getLogger(__name__)


def open_schema(file_schema: str = 'schema.sql') -> str:
    """
    Opens file containing an SQL script.

    Args:
        file_schema (str): path of sql script. Defaults to 'schema.sql'.

    Returns:
        str: The content of the SQL script as a string.
    """
    try:
        with open(file_schema, 'r', encoding='utf-8') as file:
            schema = file.read()
            logging.debug('Script {file_schema} sql lido com sucesso.')
            return schema
    except FileNotFoundError as error:
        logging.exception(error)
        raise


def init_db(db_name='test.db', schema: str = ''):
    """
    Initialize the database.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            if schema is not None:
                if schema != '':
                    conn.executescript(schema)
                    conn.commit()
                    logging.debug(f'Database {db_name} criada com sucesso!')
                    return
            raise ValueError(f"The schema can't be '{schema}'")
    except sqlite3.Error as e:
        logging.exception(f'Erro ao criar banco de dados: {e}')
        raise
    except Exception as e:
        logging.exception(f'Erro inexperado: {e}')
        raise


def query_run(db_name: str, query: str) -> list | str | bool:
    """
    Executa uma query genérica (leitura ou escrita).

    Args:
        query(str): A query a ser executada.

    Returns:
        list: Resultado da consulta se SELECT, True/False para outras
        operações.
    """
    try:
        with sqlite3.connect(db_name) as conn:
            if query.strip().lower().startswith("select"):
                result = conn.execute(query).fetchall()
                logging.debug(f'{result}')
                textual = ';'.join([str(item) for item in result]).replace(
                    '(', '').replace(')', '')
                return textual
            else:
                result = conn.execute(query).fetchall()
                conn.commit()
                logging.debug(f'{query=} has been executed.')
                return result
    except Exception as e:
        logging.error(f'Erro ao executar query: {e}')
        return False if not query.strip().lower().startswith("select") else []


if __name__ == '__main__':
    init_db('teste.db', open_schema())
