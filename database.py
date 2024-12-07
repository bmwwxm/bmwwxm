import sqlite3
from datetime import datetime, timedelta

# Подключение к базе данных SQLite
conn = sqlite3.connect("user_data.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей (если ещё не создана)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    name TEXT,
    subscription_end TIMESTAMP,
    message_count INTEGER DEFAULT 0
)
""")
conn.commit()

def save_user(chat_id, name=None, subscription_end=None, message_count=0):
    # Если подписка не указана, устанавливаем на 7 дней от текущего момента
    subscription_end = subscription_end or (datetime.now() + timedelta(days=7))
    
    cursor.execute("""
    INSERT OR REPLACE INTO users (chat_id, name, subscription_end, message_count) 
    VALUES (?, ?, ?, ?)
    """, (chat_id, name, subscription_end, message_count))
    conn.commit()

def get_user(chat_id):
    cursor.execute("SELECT chat_id, name, subscription_end, message_count FROM users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    if result:
        return {"chat_id": result[0], "name": result[1], "subscription_end": result[2], "message_count": result[3]}
    return None

def delete_user(chat_id):
    cursor.execute("DELETE FROM users WHERE chat_id = ?", (chat_id,))
    conn.commit()
