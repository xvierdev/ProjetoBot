import os
import logging
import tempfile
import telebot
import config

from config import BOT_KEY
from typing import Dict, Any, List, Tuple, Union
from faster_whisper import WhisperModel

try:
    from controller.ai_ollama import get_query_action, feedback
    from model.db_access import init_db, open_schema, query_run
except ImportError as e:
    print(f"Erro Crítico: Não foi possível importar um módulo necessário: {e}")
    exit()

# --- Inicialização & Configuração ---

# Configuração do logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler('database_assistant.log', encoding='utf-8'),
        logging.StreamHandler()  # ## MELHORIA: Adiciona log no console também
    ]
)
logger = logging.getLogger(__name__)

# Configuração do Modelo Whisper
WHISPER_MODEL_SIZE = "small"
WHISPER_PROCESSOR = None
try:
    logger.info(
        f"Carregando Modelo Faster-Whisper ({WHISPER_MODEL_SIZE}) para CPU...")
    # 'int8' é crucial para otimizar velocidade e RAM na CPU
    WHISPER_PROCESSOR = WhisperModel(
        WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
except Exception as e:
    logger.critical(f"Falha ao carregar o modelo Faster-Whisper: {e}")
    exit()

# Configuração do Banco de Dados
logger.info("Iniciando o Assistente de Banco de Dados...")
try:
    schema_content = open_schema(config.DB_SCHEMA_FILE)
    init_db(config.DB_NAME, schema_content)
    logger.info("Banco de dados inicializado com sucesso.")
except Exception as e:
    logger.critical(f"Falha ao inicializar o banco de dados: {e}")
    exit()


# --- Funções Auxiliares ---
def get_product_context() -> str:
    """Busca nomes de produtos no banco de dados para usar como contexto"""
    try:
        product_list_tuples: Union[List[Tuple[str]], str] = query_run(
            config.DB_NAME, "SELECT name FROM products;")

        if isinstance(product_list_tuples, list):
            # Filtra itens vazios ou malformados com mais segurança
            product_names = [
                item[0] for item in product_list_tuples if item and isinstance(item[0], str)]
            product_context = ", ".join(
                product_names) if product_names else "Nenhum produto encontrado."
        else:
            product_context = "Nenhum produto encontrado."
            logger.warning(
                f"Não foi possível recuperar o contexto de produtos: {product_list_tuples}")

        return product_context
    except Exception as e:
        logger.error(f"Erro ao buscar o contexto de produtos: {e}")
        return "Nenhum produto encontrado."


def handle_ai_interaction(bot: telebot.TeleBot, message, user_prompt: str):
    """
    Função principal para processar prompts do usuário (texto ou voz transcrita)
    e executar a ação correspondente da IA (query no BD ou mensagem direta).
    """
    chat_id = message.chat.id
    logger.info(
        f"Processando prompt: '{user_prompt}' para o chat ID {chat_id}")

    try:
        bot.send_message(
            chat_id, "🧠 Entendi. Consultando a IA para determinar a melhor ação...")

        # 1. Injetar Contexto
        product_context = get_product_context()
        logger.info(f"Injetando contexto: [{product_context}]")

        # 2. Chamar a IA para determinar a ação
        ia_action: Dict[str, Any] = get_query_action(
            user_prompt, product_context)

        # Validação robusta da resposta da IA
        if not isinstance(ia_action, dict) or "action" not in ia_action or "payload" not in ia_action:
            logger.error(f"A resposta da IA está mal formatada: {ia_action}")
            bot.send_message(
                chat_id, "AI: Desculpe, não consegui processar a estrutura da resposta da IA. Tente novamente.")
            return

        action_type = ia_action.get("action")
        payload = ia_action.get("payload")

        if action_type == "database_query":
            sql_query = payload

            if not sql_query or not isinstance(sql_query, str):
                logger.warning(
                    f"A IA retornou uma ação de query com um payload inválido: {sql_query}")
                bot.send_message(
                    chat_id, "AI: Desculpe, não consegui gerar uma consulta SQL válida.")
                return

            # 3. Executar a Query
            logger.info(f"Ação da IA: Executar Query -> {sql_query}")
            bot.send_message(
                chat_id, f"🔍 Query gerada:\n`{sql_query}`", parse_mode='Markdown')

            db_result = query_run(config.DB_NAME, sql_query)
            logger.info(f"Resultado do BD: {db_result}")

            bot.send_message(
                chat_id, "📝 Gerando a resposta final com base nos resultados...")

            # 4. Obter a Resposta Final
            final_response = feedback(sql_query, db_result)
            bot.send_message(
                chat_id, f"AI: {final_response}")

        elif action_type == "user_message":
            logger.info(f"Ação da IA: Mensagem para o usuário -> {payload}")
            bot.send_message(chat_id, f"AI: {payload}")

        else:
            logger.warning(
                f"Ação desconhecida recebida da IA: {action_type}. Payload: {payload}")
            bot.send_message(
                chat_id, "AI: Desculpe, não entendi a ação que preciso executar.")

    except Exception as e:
        logger.exception(
            f"Ocorreu um erro inesperado durante a interação com a IA: {e}")
        bot.send_message(
            chat_id, "Ocorreu um erro crítico ao processar sua solicitação. Verifique os logs.")


# --- Handlers do Telegram ---
def main():
    if not BOT_KEY:
        logger.critical("A chave do bot (BOT_KEY) não está definida. Encerrando.")
        return

    bot = telebot.TeleBot(BOT_KEY)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        """Lida com os comandos /start e /help."""
        logger.info(f'Recebido comando help/start do usuário {message.chat.id}')
        bot.send_message(
            message.chat.id,
            "Olá! Eu sou o Assistente de Banco de Dados. Envie sua pergunta "
            "sobre os produtos por texto ou mensagem de voz. "
            "Use /sql seguido de um comando para executar SQL diretamente."
        )

    @bot.message_handler(commands=['sql'])
    def direct_sql(message):
        """Lida com a execução direta de comandos SQL."""
        try:
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                bot.send_message(message.chat.id, "Por favor, forneça um comando SQL após /sql. Ex: `/sql SELECT * FROM products`", parse_mode='Markdown')
                return

            sql_command = parts[1].strip()

            logger.info(f"Recebido comando SQL direto: {sql_command}")
            db_result = query_run(config.DB_NAME, sql_command)

            # Formata a resposta para ser mais legível
            if db_result:
                response_text = f'Resultado da query:\n```\n{db_result}\n```'
            else:
                response_text = 'Query executada com sucesso, mas não retornou resultados.'

            # Limita o tamanho da mensagem para evitar erros do Telegram
            if len(response_text) > 4096:
                response_text = response_text[:4090] + "\n...`"

            bot.send_message(message.chat.id, response_text,
                             parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Erro ao executar SQL direto: {e}")
            bot.send_message(message.chat.id, f'Erro ao executar a query: `{e}`', parse_mode='Markdown')

    @bot.message_handler(content_types=['voice'])
    def handle_voice_prompts(message):
        """Lida com mensagens de voz, transcrevendo-as antes de processar."""
        chat_id = message.chat.id

        # Garante que o modelo de ASR foi carregado
        if WHISPER_PROCESSOR is None:
            logger.error("O modelo Whisper não está disponível.")
            bot.send_message(chat_id, "Desculpe, o serviço de transcrição de áudio não está operacional.")
            return

        try:
            bot.send_message(chat_id, "🎙️ Mensagem de voz recebida! Iniciando a transcrição local...")

            with tempfile.TemporaryDirectory() as temp_dir:
                file_info = bot.get_file(message.voice.file_id)

                if not file_info.file_path:
                    raise FileNotFoundError('Caminho do arquivo não disponível para download.')

                downloaded_file = bot.download_file(file_info.file_path)
                ogg_path = os.path.join(
                    temp_dir, f"{message.voice.file_unique_id}.ogg")

                with open(ogg_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                logger.info(f"Áudio baixado para: {ogg_path}")

                bot.send_message(chat_id, "🧠 Transcrevendo com Whisper (CPU)... Pode levar um momento.")

                segments, _ = WHISPER_PROCESSOR.transcribe(ogg_path, language="en", vad_filter=True)

                transcription = " ".join([segment.text for segment in segments]).strip()

                if transcription:
                    bot.send_message(
                        chat_id, f"✅ **Transcrição:**\n_{transcription}_",
                        parse_mode='Markdown'
                    )
                    # 3. Processar com a IA (lógica unificada)
                    handle_ai_interaction(bot, message, transcription)
                else:
                    bot.send_message(chat_id, "Desculpe, não consegui extrair texto do áudio. Tente falar mais claramente.")

        except Exception as e:
            logger.exception(f"Erro ao processar a mensagem de voz: {e}")
            bot.send_message(
                chat_id, "Ocorreu um erro ao processar sua mensagem de voz. Verifique os logs."
            )

    @bot.message_handler(func=lambda message: message.text is not None and not message.text.startswith('/'))
    def handle_all_text_prompts(message):
        """Lida com todas as mensagens de texto que não são comandos."""
        handle_ai_interaction(bot, message, message.text)

    logger.info('Bot iniciado com sucesso, aguardando mensagens...')
    bot.polling(non_stop=True) # Reiniciar automaticamente em caso de erros.


if __name__ == '__main__':
    main()
