import sqlite3

DB_PATH = "demo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK(quantidade >= 0)
);
"""

def init_db():
    # cria a tabela se ainda não existir
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(SCHEMA)
        conn.commit()
    except Exception as e:
        print(f"erro ao iniciar banco: {e}")
    finally:
        if conn:
            conn.close()

def query_execute(query: str) -> bool:
    # serve pra insert, update, delete
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"erro ao executar query: {e}")
        return False
    finally:
        if conn:
            conn.close()

def query_read(query: str) -> list:
    # serve pra select e retorna lista de resultados
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        result = conn.execute(query).fetchall()
        return result
    except Exception as e:
        print(f"erro ao ler query: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
