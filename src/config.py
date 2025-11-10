"""
Módulo para centralizar as configurações da aplicação.
Constrói caminhos absolutos para garantir que os arquivos sejam encontrados.
"""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, '.env'))


# --- Configurações do Banco de Dados ---
DB_NAME = os.path.join(BASE_DIR, "products.db")
DB_SCHEMA_FILE = os.path.join(BASE_DIR, "src", "model", "schema.sql")


# --- Configurações da IA (Google Gemini) ---
API_KEY = os.getenv("API_KEY")
MODEL_NAME = "gemini-2.5-flash"
PROMPT_QUERY_GENERATION_FILE = os.path.join(
    BASE_DIR, "prompts", "generate_query.prompt")
PROMPT_FEEDBACK_ANALYSIS_FILE = os.path.join(
    BASE_DIR, "prompts", "analyse_result.prompt")

# --- Configurações da IA (Ollama) ---
OLLAMA_MODEL = "gemma3:4b"

# --- Configurações de Segurança ---
ALLOWED_QUERY_STARTERS = ("select",)
