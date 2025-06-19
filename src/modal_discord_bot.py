import os
import sys
import time
import re
from typing import Dict, Any
import logfire
import modal

# Add the src directory to Python path for Modal environment
sys.path.append("/root/src")

# Modal app setup
app = modal.App("discord-chat-bot")

# Define the Docker image with all dependencies
image = modal.Image.debian_slim().pip_install(
    "discord.py>=2.3.0",
    "openai>=1.0.0",
    "chromadb",
    "tiktoken",
    "python-dotenv",
    "logfire"
).add_local_dir("src", "/root/src").add_local_dir("data", "/root/data")

# Define secrets
secrets = [
    modal.Secret.from_name("openai-secret"),
    modal.Secret.from_name("discord-secret-2"),
    modal.Secret.from_name("logfire-secret")
]

# Define Modal volumes for persistence
discord_bot_volume = modal.Volume.from_name("discord-bot-volume", create_if_missing=True)
chroma_volume = modal.Volume.from_name("chroma-db-volume", create_if_missing=True)

volume_mounts = {
    "/data/db": discord_bot_volume,
    "/root/chroma_db": chroma_volume
}

def bot_is_mentioned(content: str, client_user) -> bool:
    """Checks if the bot is mentioned or addressed in the message content."""
    return (
        client_user.mention in content
        or re.search(r"\bbot\b", content, re.IGNORECASE) is not None
    )

@app.function(
    image=image, 
    secrets=secrets,
    volumes=volume_mounts,
    timeout=300
)
def fetch_api(question: str) -> Dict[str, Any]:
    """Get answer from OpenAI using context from vector database"""
    
    # Configure Logfire
    logfire.configure()
    
    with logfire.span("fetch_api", question=question) as span:
        from database import init_db, log_track_interaction
        from vector_emb import answer_question, llm_answer_question, get_openai_client
        
        start_time = time.time()
        
        try:
            with logfire.span("database_init"):
                init_db()
            
            with logfire.span("answer_question") as answer_span:
                context, sources, chunks = answer_question(question)
                answer_span.set_attributes({
                    "num_sources": len(sources),
                    "num_chunks": len(chunks),
                    "context_length": len(context),
                    "question": question
                })
            
            with logfire.span("llm_call") as llm_span:
                client = get_openai_client()
                response, context_info = llm_answer_question(client, context, sources, chunks, question)
                llm_span.set_attributes({
                    "model": "gpt-4o-mini",
                    "completion_tokens": context_info.get("completion_tokens", 0),
                    "context_tokens": context_info.get("context_tokens", 0),
                    "workshops_used": context_info.get("workshops_used", []),
                    "response": response
                })
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            span.set_attributes({
                "success": True,
                "processing_time": processing_time,
                "response_length": len(response)
            })
            
            logfire.info(
                "Question answered successfully",
                question=question[:100],
                processing_time=processing_time,
                workshops_used=context_info.get("workshops_used", []),
                num_chunks=len(chunks)
            )
            
            log_id = log_track_interaction(
                question=question,
                response=response,
                context_info=context_info,
                model="gpt-4o-mini",
                start_time=start_time,
                end_time=end_time,
                success=True
            )
            
            return {
                "answer": response,
                "log_id": log_id,
                "context_info": context_info
            }
            
        except Exception as e:
            end_time = time.time()
            error_msg = f"Error generating response: {str(e)}"
            
            span.set_attributes({
                "success": False,
                "error": str(e),
                "processing_time": end_time - start_time
            })
            
            logfire.error(
                "Error processing question",
                question=question[:100],
                error=str(e),
                processing_time=end_time - start_time
            )
            
            log_track_interaction(
                question=question,
                response=error_msg,
                context_info={"error": str(e)},
                model="gpt-4o-mini", 
                start_time=start_time,
                end_time=end_time,
                success=False
            )
            
            return {"answer": error_msg, "log_id": None, "context_info": {}}

@app.function(
    image=image,
    secrets=secrets,
    volumes=volume_mounts,
    timeout=0,
)
async def start_discord_bot():
    """Start the Discord bot"""
    import discord
    from discord.ext import commands
    
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected to Discord!')
        print(f'Bot is in {len(bot.guilds)} guilds')
    
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        if bot_is_mentioned(message.content, bot.user):
            try:
                print(f"Processing question: {message.content}")
                
                # Extract the actual question (remove mentions)
                question = re.sub(r'<@!?\d+>', '', message.content).strip()
                if question.lower().startswith('bot'):
                    question = question[3:].strip()
                
                if not question:
                    await message.reply("Please ask me a question about the workshops!")
                    return
                
                # Create a thread for the response
                thread = await message.create_thread(name=f"Q: {question[:50]}...")
                
                # Get response from the API
                response_data = fetch_api.remote(question)
                
                # Send the response in the thread
                answer = response_data.get("answer", "I couldn't generate an answer.")
                
                # Split long responses
                if len(answer) > 2000:
                    chunks = [answer[i:i+2000] for i in range(0, len(answer), 2000)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await thread.send(f"**Answer:**\n{chunk}")
                        else:
                            await thread.send(chunk)
                else:
                    await thread.send(f"**Answer:**\n{answer}")
                
                print(f"Successfully responded to question in thread")
                
            except Exception as e:
                print(f"Error processing message: {e}")
                await message.reply(f"Sorry, I encountered an error: {str(e)}")
        
        await bot.process_commands(message)
    
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        raise ValueError("DISCORD_BOT_TOKEN not found")
    
    print("Starting Discord bot...")
    await bot.start(discord_token)

@app.local_entrypoint()
def main():
    """Local entrypoint to start the Discord bot"""
    print("Starting Discord Chat Bot on Modal...")
    start_discord_bot.remote()
    print("Discord bot is now running on Modal!") 