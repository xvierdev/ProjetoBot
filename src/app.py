import logging
from controller.ai_google import get_query, feedback
from model.db_access import init_db, open_schema, query_run


logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%y %H:%M:%S'
)


def main():
    init_db('products.db', open_schema('schema.sql'))
    while True:
        option = input('Command: ').strip()
        logging.debug(option)
        if option in ('quit', 'exit'):
            break
        sql_query = get_query(option) or ''
        feedback_msg = query_run('products.db', sql_query)
        msg = feedback(sql_query, str(feedback_msg))
        print(msg)


if __name__ == '__main__':
    main()
