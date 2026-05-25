import sqlite3
import json
from typing import Dict, Any, List

class StateMachineDB:
    def __init__(self, db_path: str = "speckit_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dag_nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data TEXT,
                    dependencies TEXT,
                    error TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def set_system_state(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)", (key, value))

    def get_system_state(self, key: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
            res = cursor.fetchone()
            return res[0] if res else None

    def upsert_node(self, node_id: str, node_type: str, status: str, data: dict = None, dependencies: List[str] = None, error: str = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dag_nodes (id, type, status, data, dependencies, error)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node_id, 
                node_type, 
                status, 
                json.dumps(data) if data else "{}", 
                json.dumps(dependencies) if dependencies else "[]", 
                error
            ))

    def get_node(self, node_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, type, status, data, dependencies, error FROM dag_nodes WHERE id = ?", (node_id,))
            res = cursor.fetchone()
            if res:
                return {
                    "id": res[0],
                    "type": res[1],
                    "status": res[2],
                    "data": json.loads(res[3]),
                    "dependencies": json.loads(res[4]),
                    "error": res[5]
                }
            return None

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, type, status, data, dependencies, error FROM dag_nodes")
            return [
                {
                    "id": row[0],
                    "type": row[1],
                    "status": row[2],
                    "data": json.loads(row[3]),
                    "dependencies": json.loads(row[4]),
                    "error": row[5]
                } for row in cursor.fetchall()
            ]

    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM dag_nodes")
            conn.execute("DELETE FROM system_state")
