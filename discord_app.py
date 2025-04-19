from openai import OpenAI
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import webserver

load_dotenv()  # Load environment variables from .env

# --- Determine and Load Transcript File --- 
#script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct path relative to the script location
#transcript_file = os.path.join(script_dir, "../data/WS1-C2.vtt") 
transcript_file = "data/WS1-C2.vtt"

MAX_CHARS = 60000 # Approx 15k tokens (using 4 chars/token heuristic)

# basic qa
def load_vtt_content(file_path):
    """Reads a VTT file and extracts the text content, skipping metadata and timestamps."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Transcript file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        return None

    content_lines = []
    is_content = False
    for line in lines:
        line = line.strip()
        # Skip empty lines, WEBVTT header, and timestamp lines
        if not line or line == 'WEBVTT' or '-->' in line:
            is_content = False
            continue
        # Skip lines that look like metadata (e.g., NOTE, STYLE)
        if re.match(r'^[A-Z]+(\s*:.*)?$', line):
             is_content = False
             continue
        # If it's not metadata or timestamp, assume it's content
        # A simple heuristic: content often follows a timestamp line
        # A better check might be needed for complex VTTs
        # We will just append any line that doesn't match the skip conditions
        content_lines.append(line)
        
    return " ".join(content_lines)

workshop_context = load_vtt_content(transcript_file)
original_length = len(workshop_context)
if original_length > MAX_CHARS:
    workshop_context = workshop_context[:MAX_CHARS]


async def answer_question_basic(client_openai, context, question):
    """Minimal function to ask OpenAI a question based on provided context."""
    system_prompt = """
    You are a helpful assistant. Answer questions based ONLY on the provided context from the workshop transcript.
    If the answer is not in the context, say you don't know based on the provided transcript.
    Keep your answers concise.
    """

    try:
        response = client_openai.chat.completions.create(
            model="gpt-3.5-turbo-16k", # Use 16k model for potentially long transcripts
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context (Workshop Transcript):\n\n{context}\n\nQuestion: {question}"}
            ],
            temperature=0.1, 
            max_tokens=500 # Allow more tokens for answers from transcript
        )
        return response.choices[0].message.content
    except Exception as e:
        # Add more specific error handling if needed (e.g., context length) 
        return f"An error occurred interacting with OpenAI: {str(e)}"

###########################################
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

client_openai = OpenAI()


@client.event
async def on_ready():
    # Send the message "hello" to every text channel on the Discord server.
    for channel in client.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            await channel.send("hello")
    #await client.close()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content_lower = message.content.lower()

    # Bot is mentioned or called
    is_asked = (
        client.user.mention in message.content or
        any(word in content_lower for word in ["bot", "question", "hey bot", "ai", "assistant"])
    )

    if is_asked:
        # Typing indicator
        async with message.channel.typing():
            response = await answer_question_basic(client_openai, workshop_context, message.content)
            await message.channel.send(response)

def run_discord_bot():
    discord_token = os.environ["DISCORD_BOT_TOKEN"]
    if not discord_token:
        raise ValueError("DISCORD_TOKEN environment variable not set")
    print("Starting Discord bot...")
    client.run(discord_token)

if __name__ == "__main__":
    # Retrieve the token from the environment variable populated by the Modal secret
    webserver.keep_alive()  # Start the Flask server
    run_discord_bot()

