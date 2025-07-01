# Discord Chat Bot

## Run locally

Git clone the repository

```
git clone https://github.com/sotoblanco/discord-chat-bot.git
```

Install dependencies

```
pip install -r requirements.txt
```

Make sure to set the environment variables in the .env file

```
export OPENAI_API_KEY=your_openai_api_key
```

```
source .env
```

Run the chat logic

```
python interactive_qa.py
```

## Feedback Database

### Viewing Locally
To view the feedback database locally, you can use any SQLite viewer. The database file is located in the `data/` directory. You can open it using a command-line tool like `sqlite3` or a GUI tool like DB Browser for SQLite.

```bash
# Using sqlite3
sqlite3 data/feedback.db
```

### Viewing in Modal
To view the feedback database in Modal, you can use the following command to run a diagnostic tool that outputs the database content:

```bash
modal run src.modal_discord::view_feedback_database
```

## System Overview

The Discord Chat Bot is designed to provide intelligent responses to questions about workshop transcripts using a Retrieval-Augmented Generation (RAG) approach. It integrates with Discord to respond to mentions and create organized conversation threads. The system uses a robust chunking strategy to ensure balanced distribution of transcript chunks, which are stored in a ChromaDB vector database for fast semantic search. The bot leverages OpenAI's GPT-4o-mini for generating responses and is deployed on Modal for scalability and persistence.

Key Features:
- **Robust Chunking**: Ensures balanced chunk distribution with multiple fallback strategies.
- **Discord Integration**: Responds to mentions and organizes conversations in threads.
- **ChromaDB Vector Search**: Provides fast semantic search across transcripts.
- **OpenAI Integration**: Uses GPT-4o-mini for intelligent responses.
- **Persistent Storage**: Data persists across deployments using Modal Volumes.
- **Auto-restart**: Bot automatically restarts every 55 minutes to prevent timeouts.

The system also includes diagnostic tools to analyze and fix chunking issues, and a logging mechanism to track interactions and performance metrics.

## ✨ Features

- **Robust Chunking**: Automatically ensures balanced chunk distribution (8-15 chunks per workshop)
- **Multiple Fallback Strategies**: Paragraph → Sentence → Word → Emergency chunking
- **Diagnostic Tools**: Built-in functions to analyze and fix chunking issues
- **Discord Integration**: Responds to mentions and creates threads for organized conversations
- **ChromaDB Vector Search**: Fast semantic search across workshop transcripts
- **OpenAI Integration**: Uses GPT-4o-mini for intelligent responses
- **Persistent Storage**: Data persists across deployments using Modal Volumes
- **Auto-restart**: Bot automatically restarts every 55 minutes to prevent timeouts

## 🏗️ Core Architecture

```
📁 src/
├── 🎯 modal_discord.py    # Main bot deployment & diagnostic functions
├── 🔧 process_transcript.py   # Robust chunking with multiple fallback strategies  
├── 💾 vector_emb.py          # Vector embeddings & retrieval with cleanup functions
├── 🗄️ database.py           # Interaction logging
└── 📊 eval.py               # LLM evaluation system

📁 data/                      # Workshop VTT transcript files
📁 chroma_db/                 # Persistent vector database
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key"
export DISCORD_BOT_TOKEN="your_discord_bot_token"
```

### 2. Deploy to Modal
```bash
# Deploy the entire application
modal deploy src.modal_discord.py

# Start the Discord bot
modal run src.modal_discord::discord_bot_runner
```

### 3. Initialize Vector Database with Robust Chunking
```bash
# Clean and rechunk all workshops (recommended first run)
modal run src.modal_discord::clean_and_rechunk_workshops

# Or populate if database is empty
modal run src.modal_discord::populate_vector_database
```

## 🔧 Diagnostic & Maintenance Tools

### Diagnose Chunking Issues
```bash
# Analyze VTT files and test chunking strategies
modal run src.modal_discord::diagnose_chunking_issues
```

### Analyze ChromaDB Content
```bash
# Check what's stored in the vector database
modal run src.modal_discord::analyze_chromadb_content
```

### Clean & Rechunk (Fixes Imbalanced Chunks)
```bash
# Delete existing collection and rechunk with robust strategy
modal run src.modal_discord::clean_and_rechunk_workshops
```

### Check Database Status
```bash
# Quick health check of vector database
modal run src.modal_discord::debug_vector_database
```

## 🤖 Discord Bot Usage

1. **Mention the bot**: `@DiscordBot What is Modal?`
2. **Use "bot" keyword**: `bot explain transformers`
3. **Get responses in threads**: Bot creates organized conversation threads
4. **Workshop-aware**: Responses include source workshop information

## 📝 File Descriptions

### `modal_discord.py`
- **Discord bot runner** with auto-restart functionality
- **Diagnostic functions** for chunking analysis
- **API endpoints** for health checks and bot info
- **Clean architecture** with organized function sections

### `process_transcript.py` 
- **Robust chunking algorithm** with 4-tier fallback system
- **VTT file processing** with clean text extraction
- **Token counting** using tiktoken for accuracy
- **Metadata generation** for each chunk

### `vector_emb.py`
- **ChromaDB integration** with persistent storage
- **OpenAI embeddings** with automatic text splitting for large chunks
- **Vector retrieval** with optional workshop filtering
- **Cleanup functions** for database maintenance

### `database.py`
- **SQLite logging** of all bot interactions
- **Performance tracking** with token usage metrics
- **Query history** for evaluation and debugging

### `eval.py`
- **LLM evaluation system** for response quality assessment
- **Jupyter notebook support** for analysis (`llm_judge_eval.ipynb`)

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
# Diagnose the problem
modal run src.modal_discord::diagnose_chunking_issues

# Fix with robust rechunking
modal run src.modal_discord::clean_and_rechunk_workshops
```

### Empty Database
```bash
# Populate with robust chunking
modal run src.modal_discord::populate_vector_database
```

## 🎛️ Configuration

### Key Constants (`vector_emb.py`)
- `TARGET_CHUNK_TOKEN_COUNT = 1000` - Target tokens per chunk
- `EMBEDDING_MAX_TOKENS = 8000` - Max tokens for embedding model
- `DEFAULT_MAX_CHUNKS = 5` - Chunks retrieved per query
- `DEFAULT_MAX_TOKENS = 12000` - Max context tokens for LLM

### Chunking Parameters (`process_transcript.py`)
- **Min chunks per workshop**: 8
- **Max chunks per workshop**: 15  
- **Fallback threshold**: < 3 chunks triggers next strategy

## 📈 Performance Improvements

- **⚡ Faster Retrieval**: Balanced chunks improve search quality
- **🎯 Better Relevance**: Consistent chunk sizes improve semantic matching
- **🔧 Self-Healing**: Diagnostic tools prevent and fix issues automatically
- **📊 Monitoring**: Built-in analysis tools for maintenance

## 🆘 Support

For issues with chunking imbalance or bot functionality:

1. **Run diagnostics**: `modal run src.modal_discord::diagnose_chunking_issues`
2. **Check database**: `modal run src.modal_discord::analyze_chromadb_content`  
3. **Clean & rechunk**: `modal run src.modal_discord::clean_and_rechunk_workshops`
4. **Verify fix**: `modal run src.modal_discord::debug_vector_database`

The robust chunking system is designed to automatically handle edge cases and ensure consistent performance across all workshop transcripts.
