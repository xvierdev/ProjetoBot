import logging
import os
from faster_whisper import WhisperModel
import config
import telebot
from config import BOT_KEY
# from controller.ai_google import get_query_action, feedback
from controller.ai_ollama import get_query_action, feedback
from model.db_access import init_db, open_schema, query_run

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    filename='projetoBot.log',
    encoding='utf-8'
)

WHISPER_MODEL_SIZE = "small"
try:
    logging.info(f"Loading Whisper Model ({WHISPER_MODEL_SIZE}) for CPU...")
    # 'int8' é crucial para otimizar velocidade e RAM na CPU
    WHISPER_PROCESSOR = WhisperModel(
        WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
except Exception as e:
    logging.critical(f"Failed to load Faster-Whisper model: {e}")
    exit()

logger = logging.getLogger(__name__)

logger.info("Starting Database Assistant (MCP)...")
try:
    schema_content = open_schema(config.DB_SCHEMA_FILE)
    init_db(config.DB_NAME, schema_content)
except Exception as e:
    logger.critical(f"Failed to initialize the database: {e}")
    exit()


def main():
    if BOT_KEY:
        bot = telebot.TeleBot(BOT_KEY)

        @bot.message_handler(content_types=['voice'])
        def handle_voice_prompts(message):
            chat_id = message.chat.id
            file_info = None
            ogg_path = None
            
            try:
                # 1. Download do áudio (geralmente .ogg/opus)
                bot.send_message(chat_id, "🎙️ Mensagem de voz recebida! Iniciando transcrição local...")
                
                # Obtém informações do arquivo (pelo id do arquivo de voz)
                file_info = bot.get_file(message.voice.file_id)
                # OGG é o formato padrão para mensagens de voz no Telegram
                ogg_path = os.path.join(config.TEMP_DIR, f"{file_info.file_id}.ogg") 
                
                # Baixa o arquivo para o caminho temporário
                downloaded_file = bot.download_file(file_info.file_path)
                with open(ogg_path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                
                logger.info(f"Audio downloaded to: {ogg_path}")

                # 2. Transcrição com faster-whisper (CPU)
                bot.send_message(chat_id, "🧠 Transcrevendo com Whisper (CPU)...")
                
                # O faster-whisper aceita o arquivo OGG/Opus diretamente
                segments, info = WHISPER_PROCESSOR.transcribe(
                    ogg_path, 
                    language="pt", 
                    vad_filter=True 
                )
                
                # Junta os segmentos
                transcricao = " ".join([segment.text for segment in segments]).strip()

                if transcricao:
                    bot.send_message(chat_id, f"✅ **Transcrição:**\n_{transcricao}_", parse_mode='Markdown')
                    
                    # 3. Processamento com Ollama/IA (reutiliza a lógica existente)
                    process_prompt(bot, chat_id, transcricao)
                else:
                    bot.send_message(chat_id, "Desculpe, não consegui transcrever o áudio.")

            except Exception as e:
                logger.exception(f"Error processing voice message: {e}")
                bot.send_message(chat_id, "Ocorreu um erro ao processar sua mensagem de voz. Verifique os logs.")
            
            finally:
                # 4. Limpeza
                if ogg_path and os.path.exists(ogg_path):
                    os.remove(ogg_path)
                    logger.info(f"Cleaned up temporary file: {ogg_path}")

        # teste - executar query diretamente
        @bot.message_handler(['sql'])
        def direct_sql(message):
            result = query_run(
                config.DB_NAME, message.text.replace('/sql', '').strip())
            bot.send_message(message.chat.id, f'Query result: {result}')

        # comando de ajuda
        @bot.message_handler(commands=['help'])
        def send_welcome(message):
            bot.send_message(
                message.chat.id, "Hello! I'm the Database Assistant. Send me your question about the products.")
            logging.info(f'Received command: {message.text}')

        # tratador da conversar com mcp
        @bot.message_handler(func=lambda message: message.text is not None and message.text[0] != '/')
        def handle_all_text_prompts(message):
            try:
                user_prompt = message.text
                logger.info(f"Received Prompt from User: {user_prompt}")

                # contexto de produtos
                product_list_tuples = query_run(
                    config.DB_NAME, "SELECT name FROM products;")

                if isinstance(product_list_tuples, list):
                    product_context = ", ".join(
                        item[0] for item in product_list_tuples)
                else:
                    product_context = "No products found."

                logger.info(f"Injecting context: [{product_context}]")

                # chamada à I.A.
                ia_action = get_query_action(user_prompt, product_context)

                action_type = ia_action.get("action")
                payload = ia_action.get("payload")

                if action_type == "database_query":
                    sql_query = payload

                    if sql_query:
                        if not isinstance(sql_query, str) or not sql_query:
                            logger.warning(
                                "AI returned a query action with invalid payload.")
                            bot.send_message(
                                message.chat.id, "AI: Desculpe, não consegui gerar uma query SQL válida.")
                            return

                        logger.info(f"AI Action: Execute Query -> {sql_query}")
                        bot.send_message(
                            message.chat.id, f"Generated Query: `{sql_query}`", parse_mode='Markdown')

                        db_result = query_run(config.DB_NAME, sql_query)
                        logger.info(f"DB Result: {db_result}")

                        final_response = feedback(sql_query, db_result)
                        bot.send_message(
                            message.chat.id, f"AI: {final_response}")

                    else:
                        raise RuntimeError('The AI did not return a query.')

                elif action_type == "user_message":
                    logger.info(f"AI Action: User Message -> {payload}")
                    bot.send_message(message.chat.id, f"IA: {payload}")

                else:
                    logger.warning(
                        f"Unknown action received from AI: {action_type}")
                    bot.send_message(
                        message.chat.id, "AI: Sorry, I didn't understand the action to be taken.")

            except Exception as e:
                logger.exception(
                    f"An unexpected error occurred in the main loop: {e}")
                # Usando message.chat.id
                bot.send_message(
                    message.chat.id, "A critical error occurred. Please check the logs.")

        @bot.message_handler(func=lambda message: message.text.startswith('/'))
        def generic_message(message):
            bot.send_message(message.chat.id, f'echo: {message.text}')

        print('Bot started successfully...')
        bot.polling()


if __name__ == '__main__':
    main()
