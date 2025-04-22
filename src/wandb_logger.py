import wandb
import os
from dotenv import load_dotenv

load_dotenv()

def init_wandb():
    """Initialize W&B with project configuration"""
    wandb.init(
        project="discord-bot-interactions-production",
        config={
            "bot_version": "1.0.1",
            "model": "gpt-4"
        }
    )

def log_interaction(user_id, channel_id, question, response, thread_id=None, feedback=None):
    """Log a bot interaction to W&B"""
    wandb.log({
        "interaction": {
            "user_id": str(user_id),
            "channel_id": str(channel_id),
            "question": question,
            "response": response,
            "thread_id": str(thread_id) if thread_id else None,
            "feedback": feedback
        }
    })