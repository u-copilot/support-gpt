import psycopg2
from datetime import datetime

# Database connection parameters
DB_NAME = "template1"
DB_USER = "owner"
DB_PASSWORD = ""
DB_HOST = "localhost"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        host=DB_HOST
    )
    
def create_table(tenantid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            tenantid INTEGER,
            message_text TEXT NOT NULL UNIQUE,
            timestamp TIMESTAMP NOT NULL,
            frequency INTEGER NOT NULL DEFAULT 1,
            response VARCHAR
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def insert_or_update_message(tenantid, message_text, all_messages):
    conn = connect_db()
    cur = conn.cursor()
    
    # Attempt to update the frequency if the message already exists
    cur.execute("""
        UPDATE chat_messages SET frequency = frequency + 1, timestamp = %s
        WHERE message_text = %s RETURNING *;
    """, (datetime.now(), message_text))
    
    # Check if the update affected any rows
    if cur.rowcount == 0:
        # If no rows were updated, insert the new message
        cur.execute("""
            INSERT INTO chat_messages (tenantid, message_text, timestamp, response)
            VALUES (%s, %s, %s, %s);
        """, (tenantid, message_text, datetime.now(), all_messages))
    
    conn.commit()
    cur.close()
    conn.close()

def retrieve_messages(tenantid):
    conn = connect_db()
    cur = conn.cursor()
    # Retrieve messages
    try:
        query = """
            SELECT id, message_text, timestamp, frequency 
            FROM chat_messages 
            WHERE tenantid = %s 
            ORDER BY timestamp DESC;
        """
        cur.execute(query, (tenantid,))
        messages = cur.fetchall()
    except Exception as e:
        print(f"error={e}")
        messages = []
    cur.close()
    conn.close()
    return messages