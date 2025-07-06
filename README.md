# Discord Chat Bot

A Discord bot that provides intelligent responses to questions about workshop transcripts using Retrieval-Augmented Generation (RAG). The bot integrates with Discord to respond to mentions, creates organized conversation threads, and uses ChromaDB for fast semantic search with OpenAI's GPT-4o-mini for generating responses.

## 🚀 Quick Start

### 1. Local Setup
```bash
# Clone the repository
git clone https://github.com/sotoblanco/discord-chat-bot.git
cd discord-chat-bot

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key"
```

### 2. Run Locally
```bash
# For local testing without Discord
python interactive_qa.py
```

## 📊 Evaluate Multiple Queries

Create a JSON file with questions:
```json
[
    {
      "id": "test_1",
      "question": "What are some best practices for prompt engineering?"
    }
]
```

Run evaluation:
```bash
python eval/test_retrieval.py
```


### 3. Discord Bot Setup
1. **Create a Discord Application**:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Under the "Bot" tab, add a bot to your application
   - Copy the bot token and set it as `DISCORD_BOT_TOKEN`

Set the bot token:
```bash
export DISCORD_BOT_TOKEN="your_discord_bot_token"
```

### 4. Deploy to Modal
```bash
# Deploy the entire application
modal deploy src.modal_discord.py

# Start the Discord bot
modal run src.modal_discord::discord_bot_runner

# Initialize vector database (first run)
modal run src.modal_discord::clean_and_rechunk_workshops
```
### 5. Deploy database to Modal
This is a datasette database that stores the question-answer pairs and the feedback from the users.

```bash
modal deploy src.modal_datasette
```

## ✨ Key Features

- **Chunking**: Balanced chunk distribution with multiple fallback strategies
- **Discord Integration**: Responds to mentions and creates organized conversation threads
- **ChromaDB Vector Search**: Fast semantic search across workshop transcripts
- **OpenAI Integration**: Uses GPT-4o-mini for intelligent responses
- **Persistent Storage**: Data persists across deployments using Modal Volumes
- **Auto-restart**: Bot automatically restarts every 55 minutes to prevent timeouts
- **Diagnostic Tools**: Built-in functions to analyze and fix chunking issues

## 🏗️ Core Architecture

```
📁 src/
├── modal_discord.py      # Main bot deployment & diagnostic functions
├── modal_datasette.py    # Datasette database deployment
├── process_transcript.py # Robust chunking with fallback strategies  
├── vector_emb.py         # Vector embeddings & retrieval
├── database.py          # Interaction logging

📁 eval/
├── evaluate_system.py    # LLM evaluation system
├── test_retrieval.py     # Test retrieval system
├── questions.json        # Questions for evaluation
├── eval_progress.json    # Progress tracking


📁 data/                     # Workshop VTT transcript files
📁 chroma_db/                # Persistent vector database
```

## 🤖 Discord Bot Usage

1. **Mention the bot**: `@DiscordBot What are debugging practice for RAG applications?`
2. **Use "bot" keyword**: `bot explain evaluation systems for AI applications`
3. **Get responses in threads**: Bot creates organized conversation threads
4. **Workshop-aware**: Responses include source workshop information

## 🔧 Diagnostic & Maintenance Tools

```bash
# Analyze VTT files and test chunking strategies
modal run src.modal_discord::diagnose_chunking_issues

# Check what's stored in the vector database
modal run src.modal_discord::analyze_chromadb_content

# Delete existing collection and rechunk with robust strategy
modal run src.modal_discord::clean_and_rechunk_workshops

# Quick health check of vector database
modal run src.modal_discord::debug_vector_database
```

## 🔍 Troubleshooting

### Bot Not Responding
```bash
# Check bot status
modal run src.modal_discord::debug_vector_database

# Restart bot
modal app stop discord-chat-bot
modal deploy src.modal_discord.py
```

### Chunking Issues
```bash
# Diagnose and fix
modal run src.modal_discord::diagnose_chunking_issues
modal run src.modal_discord::clean_and_rechunk_workshops
```

## 📝 Feedback Database

### Viewing Locally
```bash
# Using sqlite3
sqlite3 data/feedback.db
```

### Viewing in Modal
```bash
modal run src.modal_discord::view_feedback_database
```

## 🎛️ Configuration

### Key Constants (`vector_emb.py`)
- `DEFAULT_MAX_TOKENS = 12000` - Max context tokens for LLM
- `EMBEDDING_MAX_TOKENS = 7000` - Max tokens for embedding model  
- `DEFAULT_MAX_CHUNKS = 10` - Chunks retrieved per query

### Chunking Parameters (`process_transcript.py`)
- `CHUNK_SIZE = 1000` - Target tokens per chunk
- `MIN_CHUNK_SIZE = 200` - Minimum tokens required per chunk
- `CHUNK_OVERLAP = 100` - Token overlap between chunks

## 🆘 Support

For issues with chunking imbalance or bot functionality:

1. **Run diagnostics**: `modal run src.modal_discord::diagnose_chunking_issues`
2. **Check database**: `modal run src.modal_discord::analyze_chromadb_content`  
3. **Clean & rechunk**: `modal run src.modal_discord::clean_and_rechunk_workshops`
4. **Verify fix**: `modal run src.modal_discord::debug_vector_database`

