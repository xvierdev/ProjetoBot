import logging
import sqlite3

logging.basicConfig(level=logging.DEBUG)


def _open_schema(file_schema: str = 'schema.sql') -> str:
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
            logging.info('Script {file_schema} sql lido com sucesso.')
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
                    logging.info(f'Database {db_name} criada com sucesso!')
                    return
            raise ValueError(f'The schema can\'t be \'{schema}\'.')
    except sqlite3.Error as e:
        logging.exception(f'Erro ao criar banco de dados: {e}')
        raise
    except Exception as e:
        logging.exception(f'Erro inexperado: {e}')
        raise


if __name__ == '__main__':
    # test = _open_schema()
    # print(test)
    init_db('products.db', _open_schema())
