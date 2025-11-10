import logging
import sqlite3
from typing import List, Any, Tuple

# Configura um logger específico para este módulo
logger = logging.getLogger(__name__)


def open_schema(file_schema: str) -> str:
    """
    Lê o conteúdo de um arquivo de schema SQL.

    Args:
        file_schema (str): Caminho para o arquivo .sql.

    Returns:
        str: O conteúdo do script SQL.

    Raises:
        FileNotFoundError: Se o arquivo de schema não for encontrado.
    """
    try:
        with open(file_schema, 'r', encoding='utf-8') as file:
            schema = file.read()
            logger.debug(f"Schema '{file_schema}' was read successfully.")
            return schema
    except FileNotFoundError as e:
        logger.error(
            f"Schema file not found in '{file_schema}': {e}")
        raise


def init_db(db_name: str, schema: str):
    """
    Inicializa o banco de dados e executa o schema.

    Args:
        db_name (str): Nome do arquivo do banco de dados.
        schema (str): Script SQL para inicializar o banco.
    """
    if not schema:
        raise ValueError("The schema content cannot be empty.")
    try:
        with sqlite3.connect(db_name) as conn:
            conn.executescript(schema)
            conn.commit()
            logger.info(
                f"Database '{db_name}' initialized successfully.")
    except sqlite3.Error as e:
        logger.exception(
            f"SQLite error when initializing the database '{db_name}': {e}")
        raise


def query_run(db_name: str, query: str) -> List[Tuple[Any, ...]] | str:
    """
    Executa uma query de LEITURA (SELECT) de forma segura.
    Retorna os resultados como uma lista de tuplas ou uma mensagem de erro.

    Args:
        db_name (str): Nome do arquivo do banco de dados.
        query (str): A query SQL a ser executada.

    Returns:
        List[Tuple[Any, ...]]: Uma lista de tuplas com os resultados
        da consulta.
        str: Uma mensagem de erro se a query falhar ou não for permitida.
    """

    # Outras operações (UPDATE, INSERT) devem ter funções específicas
    # se necessárias.
    if not query.strip().lower().startswith("select"):
        logger.warning(f"Attempt to execute query not allowed: {query}")
        return "Operation not permitted."

    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            logger.debug(f"Query executed successfully. Result: {result}")
            return result
    except sqlite3.Error as e:
        logger.error(f"Error executing the query. '{query}': {e}")
        return f"There is a syntax error in your request: {e}"
