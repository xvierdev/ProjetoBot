import logging
import config
# from controller.ai_google import get_query_action, feedback
from controller.ai_ollama import get_query_action, feedback
from model.db_access import init_db, open_schema, query_run

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """
    Função principal que atua como MCP (Model-Context-Protocol),
    orquestrando o fluxo entre o usuário, a IA e o banco de dados.
    """
    logger.info("Starting Database Assistant (MCP)...")
    try:
        schema_content = open_schema(config.DB_SCHEMA_FILE)
        init_db(config.DB_NAME, schema_content)
    except Exception as e:
        logger.critical(f"Failed to initialize the database: {e}")
        return

    print("\nWelcome to the Database Assistant!")
    print("Enter your query or 'exit' to close.")

    while True:
        try:
            user_input = input("\nCommand: ").strip()
            if user_input.lower() in ('quit', 'exit', 'sair'):
                break
            if not user_input:
                continue

            product_list_tuples = query_run(
                config.DB_NAME, "SELECT name FROM products;")

            if isinstance(product_list_tuples, list):
                product_context = ", ".join(item[0]
                                            for item in product_list_tuples)
            else:
                product_context = "No products found."

            logger.info(f"Injecting context: [{product_context}]")

            ia_action = get_query_action(user_input, product_context)
            action_type = ia_action.get("action")
            payload = ia_action.get("payload")

            if action_type == "database_query":
                sql_query = payload

                if not isinstance(sql_query, str) or not sql_query:
                    logger.warning(
                        "AI returned a query action with invalid payload.")
                    print("AI: Sorry, I could not generate a valid query.")
                    continue

                logger.info(f"AI Action: Execute Query -> {sql_query}")
                print(f"SQL Generated: {sql_query}")

                db_result = query_run(config.DB_NAME, sql_query)
                logger.info(f"DB Result: {db_result}")

                final_response = feedback(sql_query, db_result)
                print(f"AI: {final_response}")

            elif action_type == "user_message":
                logger.info(f"AI Action: User Message -> {payload}")
                print(f"IA: {payload}")

            else:
                logger.warning(
                    f"Unknown action received from AI: {action_type}")
                print("AI: Sorry, I did not understand the action to be taken.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred in the main loop: {e}")
            print("A critical error occurred. Please check the logs.")

    print("\nGoodbye!")


if __name__ == '__main__':
    main()
