import json
import logging
from google import genai
import config

logger = logging.getLogger(__name__)

if not config.API_KEY:
    logger.critical("API_KEY não encontrada nas variáveis de ambiente.")
    raise ValueError("API_KEY não foi encontrada. Verifique o arquivo .env.")

client = genai.Client(api_key=config.API_KEY)


def _get_prompt(file_name: str) -> str:
    """Lê um arquivo de prompt."""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Arquivo de prompt '{file_name}' não foi encontrado.")
        raise


def get_query_action(user_request: str, product_context: str) -> dict:
    """
    Analisa a solicitação do usuário, usando um contexto fornecido,
    e retorna uma ação.

    Args:
        user_request (str): A solicitação do usuário em linguagem natural.
        product_context (str): Uma string com a lista de produtos disponíveis.

    Returns:
        dict: Um dicionário com as chaves 'action' e 'payload'.
    """
    error_response = {
        "action": "user_message",
        "payload": "Sorry, an error occurred while communicating with the AI. Please try again."
    }

    if not user_request:
        return {"action": "user_message", "payload": ""}

    clean_json_string = ""
    try:
        prompt_template = _get_prompt(config.PROMPT_QUERY_GENERATION_FILE)

        # Injeta a lista de produtos no placeholder {product_list} do prompt
        prompt_with_context = prompt_template.replace(
            '{product_list}', product_context)

        # Mantendo sua implementação da API intacta
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt_with_context + "\n\nRequest: " + user_request + "\nResponse:"
        )

        raw_text = response.text or ""
        clean_json_string = raw_text.strip().replace("```json", "").replace("```", "")
        logger.debug(f"JSON received from AI: {clean_json_string}")

        if not clean_json_string:
            logger.warning("The AI returned an empty response.")
            return error_response

        return json.loads(clean_json_string)

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from AI: {clean_json_string}")
        return error_response
    except FileNotFoundError:
        return {
            "action": "user_message",
            "payload": "Critical Error: Prompt configuration file not found."
        }
    except Exception as e:
        logger.exception(f"Unexpected error while generating action: {e}")
        return error_response


def feedback(original_query: str, db_result) -> str | None:
    """
    Gera uma resposta em linguagem natural baseada no resultado da query.
    (Esta função permanece a mesma)
    """
    try:
        prompt_template = _get_prompt(config.PROMPT_FEEDBACK_ANALYSIS_FILE)
        context = (
            f"\nThe original SQL query was: '{original_query}'.\n"
            f"The database result was: '{str(db_result)}'."
        )

        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt_template + context
        )
        return response.text
    except Exception as e:
        logger.exception(f"Erro ao gerar feedback da IA: {e}")
        return "Não foi possível gerar um feedback para o resultado."
