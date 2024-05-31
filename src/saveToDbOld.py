import os
import json
import boto3
from discord import Message
from botocore.exceptions import ClientError


# Create a session using your AWS credentials
s3 = boto3.resource(
    's3',
    region_name='nyc3',
    endpoint_url='https://ctac-discord-ta-bot.nyc3.digitaloceanspaces.com/',
    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

def upload_message_to_spaces(message: Message, user_message:str, response: str):
    bucket = "ctac-discord-ta-bot"
    # path = "https://ctac-discord-ta-bot.nyc3.digitaloceanspaces.com/"
    if not message:
        raise ValueError("Message, bucket, and path cannot be None")

    # Convert the message to a dictionary
    message_dict = {
        "id": str(message.id),
        "channel_id": str(message.channel.id),
        "guild_id": str(message.guild.id),
        "user_id": str(message.user.id),
        "user_name": str(message.user),
        "user_message": user_message,
        "bot_response": response,
        "timestamp": message.created_at.isoformat(),
    }

    # Convert the dictionary to JSON and encode it to bytes
    data = json.dumps(message_dict).encode()

    # Upload the data to S3
    obj = s3.Object(bucket, f"{message.channel.name}.json")
    try:
        response = obj.get()
        existing_data = response['Body'].read().decode('utf-8') 
        messages = json.loads(existing_data)
         # Ensure that messages is a list
        if type(messages) is not list:
            messages = []
    except ClientError as e:
        # If the file doesn't exist, start with an empty list
        if e.response['Error']['Code'] == 'NoSuchKey':
            messages = []
        else:
            # If another error occurred, re-raise the exception
            raise

    # Add the new message to the list of messages
    messages.append(message_dict)

    # Convert the list to JSON and encode it to bytes
    data = json.dumps(messages).encode()

    # Upload the updated list back to the Space
    try:
        obj.put(Body=data)
    except Exception as e:
        # Handle any errors that occur during the upload
        print(f"An error occurred while uploading to Space: {e}")