import os
import time
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import json
import glob
from process_transcript import chunk_workshop_transcript, count_tokens
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union

# Support both local and Modal paths
DATA_DIR = "/root/data" if os.path.exists("/root/data") else os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
COLLECTION_NAME = "workshop_chunks_all"  # Multi-workshop collection
CHROMA_DB_PATH = "/root/chroma_db" if os.path.exists("/root/chroma_db") else "chroma_db"
EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_MAX_TOKENS = 12000
DEFAULT_MAX_CHUNKS = 5
COMPLETION_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a helpful workshop assistant.
Answer questions based only on the workshop transcript sections provided.
If you don't know the answer or can't find it in the provided sections, say so.
When referencing information, mention which workshop(s) the information comes from."""

# === WORKSHOP DISCOVERY FUNCTIONS ===

def discover_workshops(data_dir: str = DATA_DIR) -> Dict[str, Dict[str, str]]:
    """Discover all workshop VTT files in the data directory"""
    vtt_pattern = os.path.join(data_dir, "WS*.vtt")
    workshop_files = glob.glob(vtt_pattern)
    
    workshops = {}
    for file_path in workshop_files:
        filename = os.path.basename(file_path)
        # Extract workshop ID from filename (e.g., WS1-C2.vtt -> WS1)
        workshop_id = filename.split('-')[0] if '-' in filename else filename.split('.')[0]
        workshops[workshop_id] = {
            'id': workshop_id,
            'filename': filename,
            'path': file_path
        }
    
    return workshops

def get_workshop_info() -> Dict[str, Dict[str, str]]:
    """Get information about available workshops"""
    workshops = discover_workshops()
    print(f"Found {len(workshops)} workshops:")
    for workshop_id, info in workshops.items():
        print(f"  - {workshop_id}: {info['filename']}")
    return workshops

def list_available_workshops() -> List[str]:
    """Get a list of available workshop IDs"""
    workshops = discover_workshops()
    return list(workshops.keys())

# === VECTOR STORAGE FUNCTIONS ===

def get_openai_client():
    """Initialize and return an OpenAI client with API key from environment"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    return OpenAI(api_key=api_key)

def generate_embedding(text: str) -> List[float]:
    """Generate an embedding vector for a text using OpenAI's API"""
    client = get_openai_client()
    
    # Request the embedding from OpenAI
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    
    # Extract the embedding vector from the response
    embedding = response.data[0].embedding
    
    return embedding

def get_chroma_client():
    """Initialize and return a ChromaDB client with persistence"""
    # Create the directory if it doesn't exist
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    
    # Initialize ChromaDB with persistence
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client

def get_or_create_collection(client, collection_name: str = COLLECTION_NAME):
    """Get or create a collection in ChromaDB"""
    try:
        # First try to get the existing collection
        collection = client.get_collection(name=collection_name)
        print(f"Retrieved existing collection '{collection_name}'")
    except Exception:
        # If it doesn't exist, create a new one
        print(f"Creating new collection '{collection_name}'")
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Multi-workshop transcript chunks"}
        )
    
    return collection

def clear_collection(collection_name: str = COLLECTION_NAME):
    """Deletes and re-creates a collection to ensure it's empty."""
    print(f"Attempting to clear collection '{collection_name}'...")
    try:
        client = get_chroma_client()
        client.delete_collection(name=collection_name)
        print(f"Successfully deleted collection '{collection_name}'.")
    except Exception as e:
        print(f"Collection '{collection_name}' did not exist or could not be deleted: {e}")
    
    # Re-create the collection to ensure it's fresh
    get_or_create_collection(client, collection_name)
    print(f"Collection '{collection_name}' has been cleared and is ready.")

def add_chunks_to_collection(collection, chunks: List[Dict], workshop_id: str):
    """Add multiple chunks to the collection with workshop metadata"""
    # Prepare data for storage
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    for chunk in chunks:
        # Generate embedding for this chunk
        chunk['embedding'] = generate_embedding(chunk['text'])
        
        # Create unique ID with workshop prefix
        chunk_id = f"{workshop_id}_{chunk['chunk_id']}"
        
        # Add to storage arrays
        ids.append(chunk_id)
        documents.append(chunk['text'])
        embeddings.append(chunk['embedding'])
        
        # Create metadata with workshop information
        metadata = {
            'workshop_id': workshop_id,
            'position': chunk['position'],
            'token_count': chunk['token_count'],
            'source': chunk['source'],
            'timestamp': chunk.get('timestamp', 'Unknown'),
            'speaker': chunk.get('speaker', 'Unknown'),
            'original_chunk_id': chunk['chunk_id']
        }
        metadatas.append(metadata)
    
    # Add to collection
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    return len(chunks)

def query_collection(collection, query_text: str, n_results: int = DEFAULT_MAX_CHUNKS, 
                    workshop_filter: Optional[Union[str, List[str]]] = None):
    """Query the collection for relevant documents with optional workshop filtering"""
    # Generate embedding for the query
    query_embedding = generate_embedding(query_text)
    
    # Prepare query parameters
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": n_results
    }
    
    # Add workshop filter if specified
    if workshop_filter:
        if isinstance(workshop_filter, str):
            query_params["where"] = {"workshop_id": workshop_filter}
        elif isinstance(workshop_filter, list):
            query_params["where"] = {"workshop_id": {"$in": workshop_filter}}
    
    # Search for similar documents
    results = collection.query(**query_params)
    
    return results

# === WORKSHOP PROCESSING FUNCTIONS ===

def process_workshop(transcript_path: str, workshop_id: str, collection_name: str = COLLECTION_NAME) -> int:
    """Process a workshop transcript and store it in the vector database"""
    if not os.path.exists(transcript_path):
        print(f"Warning: Transcript file not found: {transcript_path}")
        return 0
    
    # Create chunks from workshop transcript
    chunks = chunk_workshop_transcript(transcript_path)
    print(f"Created {len(chunks)} chunks from workshop {workshop_id}")
    
    # Initialize ChromaDB
    client = get_chroma_client()
    collection = get_or_create_collection(client, collection_name)
    
    # Check if this workshop is already processed
    try:
        existing_results = collection.query(
            query_embeddings=[[0.0] * 1536],  # Dummy embedding
            n_results=1,
            where={"workshop_id": workshop_id}
        )
        if existing_results and existing_results['ids'] and len(existing_results['ids'][0]) > 0:
            print(f"Workshop '{workshop_id}' already exists in collection")
            return 0
    except:
        # New collection or workshop, continue with adding chunks
        pass
    
    # Add all chunks to the collection with workshop metadata
    num_added = add_chunks_to_collection(collection, chunks, workshop_id)
    print(f"Added {num_added} chunks from {workshop_id} to collection '{collection_name}'")
    
    return num_added

def process_all_workshops(collection_name: str = COLLECTION_NAME) -> List[str]:
    """Process all discovered workshops and store them in the vector database"""
    workshops = discover_workshops()
    
    if not workshops:
        print("No workshop files found in the data directory")
        return []
    
    total_chunks = 0
    processed_workshops = []
    
    for workshop_id, workshop_info in workshops.items():
        print(f"\nProcessing {workshop_id}...")
        num_chunks = process_workshop(workshop_info['path'], workshop_id, collection_name)
        if num_chunks > 0:
            total_chunks += num_chunks
            processed_workshops.append(workshop_id)
        else:
            print(f"Skipped {workshop_id} (already processed or file not found)")
    
    print(f"\nCompleted processing:")
    print(f"- Workshops processed: {len(processed_workshops)}")
    print(f"- Total chunks added: {total_chunks}")
    print(f"- Processed workshops: {', '.join(processed_workshops)}")
    
    return processed_workshops

def get_collection_status(collection_name: str = COLLECTION_NAME) -> Optional[Dict]:
    """Get information about what's currently in the collection"""
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client, collection_name)
        
        total_count = collection.count()
        print(f"Collection '{collection_name}' contains {total_count} total chunks")
        
        if total_count > 0:
            # Get workshop breakdown
            workshops = discover_workshops()
            workshop_counts = {}
            
            for workshop_id in workshops.keys():
                try:
                    results = collection.query(
                        query_embeddings=[[0.0] * 1536],  # Dummy embedding
                        n_results=1000,  # Get many to count
                        where={"workshop_id": workshop_id}
                    )
                    count = len(results['ids'][0]) if results and results['ids'] else 0
                    workshop_counts[workshop_id] = count
                except:
                    workshop_counts[workshop_id] = 0
            
            print("Workshop breakdown:")
            for workshop_id, count in workshop_counts.items():
                status = "✓ Processed" if count > 0 else "✗ Not processed"
                print(f"  - {workshop_id}: {count} chunks {status}")
            
            return {
                'total_chunks': total_count,
                'workshop_counts': workshop_counts
            }
        
    except Exception as e:
        print(f"Error getting collection status: {e}")
        return None

# === RETRIEVAL FUNCTIONS ===

def retrieve_relevant_chunks(question: str, collection_name: str = COLLECTION_NAME, 
                           n_results: int = DEFAULT_MAX_CHUNKS, 
                           workshop_filter: Optional[Union[str, List[str]]] = None) -> List[Dict]:
    """Retrieve chunks from vector database for a given question with optional workshop filtering"""
    # Initialize client and get collection
    client = get_chroma_client()
    collection = get_or_create_collection(client, collection_name)
    
    # Query the collection
    results = query_collection(collection, question, n_results=n_results, workshop_filter=workshop_filter)
    
    # Process the results
    chunks = []
    if results and 'documents' in results and results['documents'] and len(results['documents'][0]) > 0:
        # Format chunks
        for i in range(len(results['documents'][0])):
            chunk = {
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'id': results['ids'][0][i],
                'relevance': 1.0  # Default relevance since we don't have distances
            }
            chunks.append(chunk)
    
    return chunks

def combine_chunks(chunks: List[Dict], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Combine multiple chunks into a single context, respecting token limit"""
    if not chunks:
        return ""
    
    # Sort chunks by position if available
    sorted_chunks = sorted(chunks, key=lambda x: int(x['metadata'].get('position', 0)))
    
    combined_text = ""
    total_tokens = 0
    
    for chunk in sorted_chunks:
        chunk_text = chunk['text']
        chunk_tokens = int(chunk['metadata'].get('token_count', 0))
        
        # If no token count in metadata, calculate it
        if chunk_tokens == 0:
            chunk_tokens = count_tokens(chunk_text)
        
        # Check if adding this chunk would exceed the token limit
        if total_tokens + chunk_tokens > max_tokens:
            break
        
        # Add separator between chunks if needed
        if combined_text:
            combined_text += "\n\n--- Next Section ---\n\n"
        
        # Add the chunk text
        combined_text += chunk_text
        total_tokens += chunk_tokens
    
    return combined_text

def format_sources(sources: List[Dict]) -> str:
    """Format source information into a readable string with workshop information"""
    if not sources:
        return "No source information available."
    
    formatted = "Sources (most similar first, lower distance = more similar):\n"
    for i, source in enumerate(sources):
        # Start with the source number and distance score
        source_header = f"{i+1}. "
        if source.get('relevance') is not None:
            source_header += f"[Distance: {source['relevance']:.4f}] "
        
        # Add workshop information
        workshop_id = source.get('workshop_id', 'Unknown')
        source_header += f"[{workshop_id}] "
        
        # Add position information
        position = source.get('position', 'Unknown')
        source_header += f"[Chunk {position}] "
        
        # Add speaker information if available
        speaker = source.get('speaker', 'Unknown')
        if speaker != 'Unknown':
            source_header += f"Speaker: {speaker}. "
        
        formatted += source_header + "\n"
        
        # Add the content with better formatting
        text = source.get('text', '')
        if text:
            # Format the text with proper indentation
            text_lines = text.split('\n')
            indented_text = '\n    '.join(text_lines)  # Indent continuation lines
            formatted += f"    {indented_text}\n\n"
    
    return formatted

def get_context_for_question(question: str, collection_name: str = COLLECTION_NAME, 
                           max_chunks: int = DEFAULT_MAX_CHUNKS, 
                           workshop_filter: Optional[Union[str, List[str]]] = None) -> tuple:
    """Get relevant context from the vector database for a question with optional workshop filtering"""
    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(question, collection_name, max_chunks, workshop_filter)
    
    # Format source information
    sources = []
    for chunk in chunks:
        metadata = chunk['metadata']
        text = chunk['text']
        
        # Extract information from metadata
        timestamp = metadata.get('timestamp', "Unknown")
        speaker = metadata.get('speaker', "Unknown")
        workshop_id = metadata.get('workshop_id', "Unknown")
        
        source = {
            'position': metadata.get('position', 'Unknown'),
            'timestamp': timestamp,
            'speaker': speaker,
            'workshop_id': workshop_id,
            'text': text,
            'relevance': chunk.get('relevance')
        }
        sources.append(source)
    
    # Combine chunks
    context = combine_chunks(chunks)
    
    return context, sources, chunks  # Return the raw chunks as well for logging

# === QUESTION ANSWERING FUNCTIONS ===

def answer_question(question: str, workshop_filter: Optional[Union[str, List[str]]] = None) -> tuple:
    """
    Answers a question based on workshop transcripts with optional workshop filtering
    workshop_filter can be:
    - None: search all workshops
    - str: search specific workshop (e.g., "WS1")
    - list: search multiple workshops (e.g., ["WS1", "WS2"])
    """
    # Initialize ChromaDB and ensure collection exists
    client = get_chroma_client()
    collection = get_or_create_collection(client, COLLECTION_NAME)
    
    # Check if collection is empty and populate if needed
    count = collection.count()
    if count == 0:
        print("Collection is empty, processing all workshop transcripts...")
        process_all_workshops(COLLECTION_NAME)
    
    # Get relevant context from the vector database
    context, sources, chunks = get_context_for_question(
        question=question,
        collection_name=COLLECTION_NAME,
        max_chunks=DEFAULT_MAX_CHUNKS,
        workshop_filter=workshop_filter
    )
    
    # Log information about the context
    context_tokens = count_tokens(context)
    num_chunks = len(sources)
    workshops_used = list(set([source.get('workshop_id', 'Unknown') for source in sources]))
    
    print(f"Retrieved {context_tokens} tokens of relevant context")
    print(f"Retrieved {num_chunks} source chunks")
    print(f"Workshops referenced: {', '.join(workshops_used)}")
    
    return context, sources, chunks  # Return sources for further processing

def llm_answer_question(context: str, sources: List[Dict], chunks: List[Dict], question: str) -> tuple:
    """Enhanced LLM answer function with workshop awareness"""
    num_chunks = len(sources)
    workshops_used = list(set([source.get('workshop_id', 'Unknown') for source in sources]))
    
    client = get_openai_client()
    try:
        # Enhanced system prompt with workshop context
        enhanced_system_prompt = SYSTEM_PROMPT + f"\n\nThe information provided comes from workshops: {', '.join(workshops_used)}."
        
        # Make the API call
        response = client.chat.completions.create(
            model=COMPLETION_MODEL,
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": f"Workshop Transcript Sections:\n{context}\n\nQuestion: {question}"}
            ],
            temperature=0
        )
        
        message = response.choices[0].message.content
        
        # Get token usage
        completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
        prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else count_tokens(context)
        
        # Record metrics with workshop information
        context_info = {
             "num_chunks": num_chunks,
             "context_tokens": prompt_tokens,
             "completion_tokens": completion_tokens,
             "embedding_tokens": num_chunks * 1536,  # Estimate based on embedding dimensions
             "workshops_used": workshops_used,
             "chunks": chunks
         }

        print(f"Context Information: {context_info}")
        
        return message, context_info

    except Exception as e:
        error_message = f"Sorry, an error occurred: {str(e)}"
        return error_message, {}

def full_answer_question(question: str, workshop_filter: Optional[Union[str, List[str]]] = None) -> tuple:
    """Complete pipeline to answer a question using LLM with workshop context"""
    # Get context and sources
    context, sources, chunks = answer_question(question, workshop_filter)
    
    if not context:
        return "No relevant information found in the workshop transcripts.", {}
    
    # Generate LLM response
    answer, context_info = llm_answer_question(context, sources, chunks, question)
    
    return answer, context_info

# === UTILITY FUNCTIONS ===

def search_workshops_by_topic(topic: str, max_results: int = 10) -> Dict[str, List[Dict]]:
    """Search all workshops for content related to a specific topic"""
    workshops = discover_workshops()
    results = {}
    
    for workshop_id in workshops.keys():
        chunks = retrieve_relevant_chunks(
            question=topic,
            workshop_filter=workshop_id,
            n_results=max_results
        )
        if chunks:
            results[workshop_id] = chunks
    
    return results

def compare_workshops_on_topic(topic: str, workshop_ids: List[str], max_chunks_per_workshop: int = 3) -> Dict[str, List[Dict]]:
    """Compare how different workshops address a specific topic"""
    results = {}
    
    for workshop_id in workshop_ids:
        chunks = retrieve_relevant_chunks(
            question=topic,
            workshop_filter=workshop_id,
            n_results=max_chunks_per_workshop
        )
        if chunks:
            results[workshop_id] = chunks
    
    return results

if __name__ == "__main__":
    # Example usage
    print("Multi-Workshop Vector System")
    print("=" * 40)
    
    # Show available workshops
    workshops = get_workshop_info()
    
    # Show collection status
    print("\nCollection Status:")
    get_collection_status()
    
    # Example: Process all workshops
    print("\nProcessing all workshops...")
    processed = process_all_workshops()
    
    # Example: Ask a question across all workshops
    print("\nExample: Asking a question across all workshops...")
    answer, context_info = full_answer_question("What is machine learning?")
    print(f"Answer: {answer}") 