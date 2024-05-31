import os
import json
import psycopg2
from discord import Message

# Database connection parameters
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def connect_to_db():
    return psycopg2.connect(**db_params)

def upload_message_to_db(message: Message, user_message: str, response: str):
    if not message:
        raise ValueError("Message cannot be None")

    # Convert the message to a dictionary
    message_dict = {
        "message_id": message.id,
        "channel_id": message.channel.id,
        "guild_id": message.guild.id,
        "user_id": message.user.id,
        "user_name": str(message.user),
        "user_message": user_message,
        "bot_response": response,
        "timestamp": message.created_at
    }

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO discord_messages (message_id, channel_id, guild_id, user_id, user_name, user_message, bot_response, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            message_dict["message_id"],
            message_dict["channel_id"],
            message_dict["guild_id"],
            message_dict["user_id"],
            message_dict["user_name"],
            message_dict["user_message"],
            message_dict["bot_response"],
            message_dict["timestamp"]
        ))

        conn.commit()
        cursor.close()
        conn.close()
        print("Message stored in the database successfully")
    except Exception as e:
        print(f"An error occurred while inserting into the database: {e}")

# Example usage
# message = ...  # Assume you have a Discord Message object
# user_message = "Example user message"
# response = "Example bot response"
# upload_message_to_db(message, user_message, response)
