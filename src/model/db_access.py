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
            logger.debug(f"Schema '{file_schema}' lido com sucesso.")
            return schema
    except FileNotFoundError as e:
        logger.error(
            f"Arquivo de schema não encontrado em '{file_schema}': {e}")
        raise


def init_db(db_name: str, schema: str):
    """
    Inicializa o banco de dados e executa o schema.

    Args:
        db_name (str): Nome do arquivo do banco de dados.
        schema (str): Script SQL para inicializar o banco.
    """
    if not schema:
        raise ValueError("O conteúdo do schema não pode ser vazio.")
    try:
        with sqlite3.connect(db_name) as conn:
            conn.executescript(schema)
            conn.commit()
            logger.info(
                f"Banco de dados '{db_name}' inicializado com sucesso.")
    except sqlite3.Error as e:
        logger.exception(
            f"Erro do SQLite ao inicializar o banco de dados '{db_name}': {e}")
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
        logger.warning(f"Tentativa de executar query não permitida: {query}")
        return "Operação não permitida."

    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            logger.debug(f"Query executada com sucesso. Resultado: {result}")
            return result
    except sqlite3.Error as e:
        logger.error(f"Erro ao executar a query '{query}': {e}")
        return f"Erro de sintaxe na sua solicitação: {e}"
