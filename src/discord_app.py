import discord
from discord.ext import commands
import os
import re

from webserver import keep_alive
from database import init_db, log_interaction, store_feedback
from wandb_logger import init_wandb, log_interaction as wandb_log_interaction
from vector_emb import llm_answer_question

# Initialize the database and wandb
# init_db()
# --- Determine and Load Transcript File --- 

transcript_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "WS1-C2.vtt")

MAX_CHARS = 60000 # Approx 15k tokens (using 4 chars/token heuristic)

# init_wandb()

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


async def answer_question_basic(context, question):
    """Minimal function to ask OpenAI a question based on provided context."""
    client_openai = OpenAI()
    system_prompt = """
    You are a helpful assistant. Answer questions based ONLY on the provided context from the workshop transcript.
    If the answer is not in the context, say you don't know based on the provided transcript.
    Answer in a 2-3 sentences only. Be thorough, but concise.
    """

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4.1",
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
def discord_setup():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    return discord.Client(intents=intents)

client = discord_setup()

def bot_is_mentioned(content: str, client_user) -> bool:
    """Checks if the bot is mentioned or addressed in the message content."""
    # Use word boundaries (\b) to avoid matching parts of other words
    return (
        client_user.mention in content
        or re.search(r"\bbot\b", content, re.IGNORECASE) is not None
    )

def bot_is_mentioned(content: str, client_user) -> bool:
    """Checks if the bot is mentioned or addressed in the message content."""
    # Use word boundaries (\b) to avoid matching parts of other words
    return (
        client_user.mention in content
        or re.search(r"\bbot\b", content, re.IGNORECASE) is not None
    )
  
@client.event
async def on_ready():
    # Send the message "hello" only to the general channel
    for guild in client.guilds:
        general_channel = discord.utils.get(guild.text_channels, name='random')
        if general_channel:
            await general_channel.send("Hello! I'm here to assist you with the workshop transcript. Ask me anything by mentioning me (@bot)!")

async def handle_feedback(message, thread_name):
    try:
        interaction_id = int(thread_name.split('-')[1]) if '-' in thread_name else None
        if not interaction_id:
            return
            
        feedback = message.content
        store_feedback(interaction_id, feedback)
        
        # Get the original bot response from the thread
        original_response = None
        async for msg in message.channel.history(limit=10):
            if msg.author == client.user and not msg.content.startswith(("Was this response helpful?", "Thank you for your feedback!")):
                original_response = msg.content
                break
        
        # Update W&B with feedback
        wandb_log_interaction(
            message.author.id,
            message.channel.id,
            "",  # No need to include question for feedback
            original_response,  # Include the original response
            message.channel.id,
            feedback
        )
        await message.channel.send("Thank you for your feedback!")
        await message.channel.edit(archived=True)
        return True
    except Exception as e:
        print(f"Error storing feedback: {e}")
        return False

async def create_and_handle_thread(message, question):
    try:
        thread = await message.create_thread(
            name=f"q-{message.id}",
            auto_archive_duration=60
        )
        
        async with thread.typing():
            #workshop_context = get_context(context_file)
            response =  llm_answer_question(question)
            await thread.send(response)
            
            # Log interaction to both database and wandb
            interaction_id = log_interaction(
                message.author.id,
                message.channel.id,
                question,
                response,
                thread.id
            )
            
            wandb_log_interaction(
                message.author.id,
                message.channel.id,
                question,
                response,
                thread.id
            )
            
            await thread.edit(name=f"question-{interaction_id}")
            await thread.send("Was this response helpful? (Please reply with Yes/No and optionally add more details)")
            
    except Exception as e:
        await message.channel.send(f"Error: {str(e)}")

def is_bot_mentioned(message, client):
    return client.user.mention in message.content

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check if it's a feedback response in a thread
    if isinstance(message.channel, discord.Thread) and message.channel.owner_id == client.user.id:
        feedback_handled = await handle_feedback(message, message.channel.name)
        if feedback_handled:
            return

    # Bot is mentioned or called
    if is_bot_mentioned(message, client):
        await create_and_handle_thread(message, message.content)


def run_discord_bot():
    discord_token = os.environ["DISCORD_BOT_TOKEN"]
    if not discord_token:
        raise ValueError("DISCORD_TOKEN environment variable not set")
    print("Starting Discord bot...")
    client.run(discord_token)

if __name__ == "__main__":
    init_wandb()
    # Retrieve the token from the environment variable populated by the Modal secret
    keep_alive()  # Start the Flask server
    run_discord_bot()

