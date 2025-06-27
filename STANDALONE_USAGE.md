# Running Vector Embedding Without Modal

This guide shows you how to run the vector embedding functionality locally from the command line without using Modal.

## 🔧 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in your project root:
```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
```

Or export directly:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Prepare Data
Ensure your VTT transcript files are in the `data/` directory:
```
data/
├── WS1-workshop-transcript.vtt
├── WS2-another-workshop.vtt
└── ...
```

## 🚀 Usage

### Check Database Status
```bash
python standalone_vector_emb.py --action status
```

This will show:
- Database connection status
- Number of chunks stored
- List of workshops in database

### Populate Vector Database
```bash
python standalone_vector_emb.py --action populate
```

This will:
- Discover all VTT files in `data/` directory
- Process and chunk the transcripts
- Generate embeddings using OpenAI API
- Store everything in ChromaDB (local `chroma_db/` folder)

### Query Database (Search Only)
```bash
python standalone_vector_emb.py --action query --question "What is Modal?"
```

This will:
- Search for relevant chunks
- Show matching workshop sections
- Display metadata (workshop ID, position, speaker, etc.)
- **No LLM response**, just raw search results

### Get AI Answer
```bash
python standalone_vector_emb.py --action answer --question "How does chunking work?"
```

This will:
- Search for relevant chunks
- Generate an AI response using GPT-4o-mini
- Show token usage statistics
- Include source workshop information

## 🔍 Example Workflows

### Initial Setup and Population
```bash
# Check if database exists and is populated
python standalone_vector_emb.py --action status

# If empty, populate it
python standalone_vector_emb.py --action populate

# Verify population worked
python standalone_vector_emb.py --action status
```

### Research Workflow
```bash
# First, search for relevant content
python standalone_vector_emb.py --action query --question "deployment strategies"

# Then get an AI-generated answer
python standalone_vector_emb.py --action answer --question "What are the best deployment strategies mentioned in the workshops?"
```

### Debugging Workflow
```bash
# Check what's in the database
python standalone_vector_emb.py --action status

# Search for specific workshop content
python standalone_vector_emb.py --action query --question "WS1"

# Test AI responses
python standalone_vector_emb.py --action answer --question "Summarize the main points from WS1"
```

## 📂 What Gets Created

When you run the standalone script, it creates:

```
your-project/
├── chroma_db/           # Local ChromaDB storage
│   ├── chroma.sqlite3   # Database file
│   └── ...              # Index files
├── .env                 # Your API keys
└── standalone_vector_emb.py  # The script
```

## 🎛️ Configuration

The script uses the same configuration as the Modal version:

- **Chunk size**: ~1000 tokens per chunk
- **Embedding model**: `text-embedding-3-small`
- **LLM model**: `gpt-4o-mini`
- **Max chunks per query**: 10
- **Max context tokens**: 12,000

You can modify these in `src/vector_emb.py`:
```python
DEFAULT_MAX_TOKENS = 12000      # Max context for LLM
DEFAULT_MAX_CHUNKS = 10         # Chunks retrieved per query
EMBEDDING_MODEL = "text-embedding-3-small"
COMPLETION_MODEL = "gpt-4o-mini"
```

## 🔄 Direct Python Usage

You can also import and use the functions directly in Python:

```python
from src.vector_emb import (
    discover_workshops, 
    process_all_workshops, 
    answer_question,
    get_context_for_question
)

# Populate database
workshops = discover_workshops()
processed = process_all_workshops()

# Get context for a question
context, sources, chunks = get_context_for_question("What is Modal?")

# Get AI answer
context, sources, chunks = answer_question("How does deployment work?")
```

## 🐛 Troubleshooting

### "No workshops found"
- Check that VTT files are in `data/` directory
- Ensure files have `.vtt` extension
- Check file permissions

### "OPENAI_API_KEY not found"
- Create `.env` file with your API key
- Or export the environment variable
- Ensure no extra spaces in the key

### "Database error"
- Delete `chroma_db/` folder and try again
- Check disk space
- Ensure write permissions in project directory

### "No relevant information found"
- Check if database is populated: `--action status`
- Try different search terms
- Ensure VTT files contain actual content (not just metadata)

## 🔧 Advanced Usage

### Custom Data Directory
Modify `DATA_DIR` in `src/vector_emb.py`:
```python
DATA_DIR = "/path/to/your/vtt/files"
```

### Custom ChromaDB Location
Modify `CHROMA_DB_PATH` in `src/vector_emb.py`:
```python
CHROMA_DB_PATH = "/path/to/your/chroma/db"
```

### Workshop-Specific Queries
Use the functions directly for workshop filtering:
```python
from src.vector_emb import get_context_for_question

# Only search specific workshops
context, sources, chunks = get_context_for_question(
    "What is Modal?", 
    workshop_filter=["WS1", "WS2"]
)
```

This gives you the full functionality of the Discord bot's vector embedding system without needing Modal! 