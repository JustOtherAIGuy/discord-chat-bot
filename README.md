# Discord Chat Bot

## Run locally

Git clone the RAG branch

```
git clone https://github.com/sotoblanco/discord-chat-bot.git
git checkout rag
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



A Discord bot using RAG (Retrieval-Augmented Generation) deployed on Modal to answer questions about workshop transcripts with **robust chunking strategy**.

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
├── 🎯 modal_discord_bot.py    # Main bot deployment & diagnostic functions
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
modal deploy src/modal_discord_bot.py

# Start the Discord bot
modal run src.modal_discord_bot::discord_bot_runner
```

### 3. Initialize Vector Database with Robust Chunking
```bash
# Clean and rechunk all workshops (recommended first run)
modal run src.modal_discord_bot::clean_and_rechunk_workshops

# Or populate if database is empty
modal run src.modal_discord_bot::populate_vector_database
```

## 🔧 Diagnostic & Maintenance Tools

### Diagnose Chunking Issues
```bash
# Analyze VTT files and test chunking strategies
modal run src.modal_discord_bot::diagnose_chunking_issues
```

### Analyze ChromaDB Content
```bash
# Check what's stored in the vector database
modal run src.modal_discord_bot::analyze_chromadb_content
```

### Clean & Rechunk (Fixes Imbalanced Chunks)
```bash
# Delete existing collection and rechunk with robust strategy
modal run src.modal_discord_bot::clean_and_rechunk_workshops
```

### Check Database Status
```bash
# Quick health check of vector database
modal run src.modal_discord_bot::debug_vector_database
```

## 🎯 Robust Chunking Strategy

The system uses a **4-tier fallback approach** to ensure every workshop gets properly chunked:

1. **📄 Paragraph-based**: Splits on paragraph breaks (preferred)
2. **📝 Sentence-based**: Splits on sentence boundaries (fallback #1)  
3. **🔤 Word-based**: Splits on word boundaries (fallback #2)
4. **🚑 Emergency**: Force splits into exact number of chunks (guaranteed)

**Target**: 8-15 chunks per workshop, ~1000 tokens each

**Solves**: The chunking imbalance issue where some workshops had 100+ chunks while others had only 1 chunk.

## 📊 Expected Results After Cleanup

```
WS1: 8-15 chunks ✅  (was 113 chunks)
WS2: 8-15 chunks ✅  (was 1 chunk) 
WS3: 8-15 chunks ✅  (was 1 chunk)
WS4: 8-15 chunks ✅  (was 1 chunk)
WS5: 8-15 chunks ✅  (was 106 chunks)
WS6: 8-15 chunks ✅  (was 65 chunks)
```

## 🤖 Discord Bot Usage

1. **Mention the bot**: `@DiscordBot What is Modal?`
2. **Use "bot" keyword**: `bot explain transformers`
3. **Get responses in threads**: Bot creates organized conversation threads
4. **Workshop-aware**: Responses include source workshop information

## 📝 File Descriptions

### `modal_discord_bot.py`
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
modal run src.modal_discord_bot::debug_vector_database

# Restart bot
modal app stop discord-chat-bot
modal deploy src/modal_discord_bot.py
```

### Chunking Issues
```bash
# Diagnose the problem
modal run src.modal_discord_bot::diagnose_chunking_issues

# Fix with robust rechunking
modal run src.modal_discord_bot::clean_and_rechunk_workshops
```

### Empty Database
```bash
# Populate with robust chunking
modal run src.modal_discord_bot::populate_vector_database
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

1. **Run diagnostics**: `modal run src.modal_discord_bot::diagnose_chunking_issues`
2. **Check database**: `modal run src.modal_discord_bot::analyze_chromadb_content`  
3. **Clean & rechunk**: `modal run src.modal_discord_bot::clean_and_rechunk_workshops`
4. **Verify fix**: `modal run src.modal_discord_bot::debug_vector_database`

The robust chunking system is designed to automatically handle edge cases and ensure consistent performance across all workshop transcripts.
