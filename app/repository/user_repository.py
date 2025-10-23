import logging
from datetime import datetime
from psycopg2.extras import RealDictCursor
from app.core.singleton.postgres import get_postgres_instance
from app.schemas.users import UserBaseDto

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class UserRepository:
    def __init__(self, table_name: str = "users"):
        self.table_name = table_name
        self.conn = get_postgres_instance()

    def create_user(self, data: UserBaseDto):
        extra_data = {
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        extra_data.update(data.model_dump())
        columns = ", ".join(extra_data.keys())
        values_placeholders = ", ".join([f"%({k})s" for k in extra_data.keys()])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({values_placeholders})"
        with self.conn.cursor() as cur:
            cur.execute(query, extra_data)
        self.conn.commit()

    def user_exist_by_email(self, email: str):
        query = f"SELECT 1 FROM {self.table_name} WHERE email=%s LIMIT 1"
        with self.conn.cursor() as cur:
            cur.execute(query, (email,))
            return bool(cur.fetchone())

    def get_user(self, id: str):
        query = f"SELECT * FROM {self.table_name} WHERE id=%s"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (id,))
            return cur.fetchone()

    def get_users(self):
        query = f"SELECT * FROM {self.table_name}"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def update_user(self, id: str, data: UserBaseDto):
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_user(id)
        set_clause = ", ".join([f"{k} = %({k})s" for k in update_data.keys()])
        update_data["id"] = id
        query = f"UPDATE {self.table_name} SET {set_clause}, updated_at = NOW() WHERE id = %(id)s RETURNING *"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, update_data)
            self.conn.commit()
            return cur.fetchone()

    def delete_user(self, id: str):
        query = f"DELETE FROM {self.table_name} WHERE id=%s"
        with self.conn.cursor() as cur:
            cur.execute(query, (id,))
            self.conn.commit()
            return cur.rowcount > 0
