import json
import logging
from ollama import Client
import config

logger = logging.getLogger(__name__)

# Inicializa o cliente Ollama.
# Ele se conectará ao serviço Ollama rodando localmente
# (http://localhost:11434) por padrão.
client = Client()


def _get_prompt(file_name: str) -> str:
    """Lê um arquivo de prompt. (Função auxiliar idêntica à do ai_google.py)"""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Arquivo de prompt '{file_name}' não foi encontrado.")
        raise


def get_query_action(user_request: str, product_context: str) -> dict:
    """
    Analisa a solicitação do usuário usando Ollama, com contexto, e retorna uma ação.
    Esta função é um substituto direto para a versão do ai_google.py.
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

        # Usamos o prompt com contexto como a "instrução de sistema" para o modelo
        response = client.generate(
            model=config.OLLAMA_MODEL,
            system=prompt_with_context,
            prompt=f"\n\nRequest: {user_request}\nResponse:",
            options={'temperature': 0.0},
            stream=False  # Garante que a resposta venha de uma só vez
        )

        # A resposta do Ollama está na chave 'response'
        raw_text = response.get('response', "")
        clean_json_string = raw_text.strip().replace("```json", "").replace("```", "")

        if not clean_json_string:
            return error_response

        return json.loads(clean_json_string)

    except json.JSONDecodeError:
        logger.error(
            f"Failed to decode JSON from Ollama AI: {clean_json_string}")
        return error_response
    except FileNotFoundError:
        return {
            "action": "user_message",
            "payload": "Critical Error: Prompt configuration file not found."
        }
    except Exception as e:
        logger.exception(
            f"Unexpected error while generating action with Ollama: {e}")
        return error_response


def feedback(original_query: str, db_result) -> str | None:
    """
    Gera uma resposta em linguagem natural com Ollama.
    """
    try:
        prompt_template = _get_prompt(config.PROMPT_FEEDBACK_ANALYSIS_FILE)

        # Cria o contexto que será injetado no prompt
        context = (
            f"The SQL query was: '{original_query}'.\n"
            f"The database result was: '{str(db_result)}'."
        )

        # Injeta o contexto no placeholder do novo prompt
        final_prompt = prompt_template.replace(
            '{query_and_result_context}', context)

        response = client.generate(
            model=config.OLLAMA_MODEL,
            prompt=final_prompt,  # Usa o prompt completo com os dados já inseridos
            options={'temperature': 0.2},
            stream=False
        )
        # Limpa a resposta para garantir que não venha com texto extra
        summary = response.get(
            'response', "Could not generate feedback.").strip()
        return summary

    except Exception as e:
        logger.exception(f"Erro ao gerar feedback da IA com Ollama: {e}")
        return "Não foi possível gerar um feedback para o resultado."
