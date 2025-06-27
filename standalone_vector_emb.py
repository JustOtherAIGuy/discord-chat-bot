#!/usr/bin/env python3
"""
Standalone Vector Embedding Script

This script demonstrates how to run the vector embedding functionality 
without Modal, directly from the command line.

Usage:
    python standalone_vector_emb.py --action populate
    python standalone_vector_emb.py --action query --question "What is Modal?"
    python standalone_vector_emb.py --action answer --question "How does chunking work?"
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path so we can import our modules
src_dir = Path(__file__).parent / "src"
if src_dir.exists():
    sys.path.insert(0, str(src_dir))

from vector_emb import (
    discover_workshops, 
    process_all_workshops, 
    get_context_for_question,
    answer_question,
    llm_answer_question,
    get_openai_client,
    get_chroma_client,
    get_or_create_collection,
    COLLECTION_NAME
)
from process_transcript import chunk_transcript
from dotenv import load_dotenv

def setup_environment():
    """Setup environment variables and check requirements"""
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in a .env file or export it:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    print("✅ Environment setup complete")

def populate_database():
    """Populate the vector database with workshop transcripts"""
    print("🔄 Discovering workshops...")
    workshops = discover_workshops()
    
    if not workshops:
        print("❌ No workshop VTT files found in data directory")
        print("Please ensure your VTT files are in the ./data/ directory")
        return
    
    print(f"📚 Found {len(workshops)} workshops:")
    for workshop_id, info in workshops.items():
        print(f"  - {workshop_id}: {info['filename']}")
    
    print("\n🔄 Processing workshops and generating embeddings...")
    processed = process_all_workshops()
    
    if processed:
        print(f"✅ Successfully processed {len(processed)} workshops:")
        for workshop_id in processed:
            print(f"  - {workshop_id}")
    else:
        print("❌ No workshops were processed successfully")

def query_database(question):
    """Query the vector database for relevant chunks"""
    print(f"🔍 Searching for: '{question}'")
    
    context, sources, chunks = get_context_for_question(question)
    
    if not chunks:
        print("❌ No relevant information found")
        return
    
    print(f"\n✅ Found {len(chunks)} relevant chunks:")
    print("\n" + "="*60)
    
    for i, source in enumerate(sources, 1):
        print(f"\n📝 Chunk {i}:")
        print(f"Workshop: {source['workshop_id']}")
        print(f"Position: {source['position']}")
        print(f"Speaker: {source['speaker']}")
        print(f"Timestamp: {source['timestamp']}")
        print(f"Text preview: {source['text'][:200]}...")
        print("-" * 40)

def answer_with_llm(question):
    """Get an AI-generated answer based on workshop transcripts"""
    print(f"🤖 Generating answer for: '{question}'")
    
    # Get context from vector database
    context, sources, chunks = answer_question(question)
    
    if not chunks:
        print("❌ No relevant information found to answer the question")
        return
    
    print(f"📚 Using {len(chunks)} relevant chunks from workshops")
    
    # Generate LLM response
    client = get_openai_client()
    answer, context_info = llm_answer_question(client, context, sources, chunks, question)
    
    print("\n" + "="*60)
    print("🎯 ANSWER:")
    print("="*60)
    print(answer)
    print("\n" + "="*60)
    print("📊 CONTEXT INFO:")
    print(f"Chunks used: {context_info.get('num_chunks', 0)}")
    print(f"Context tokens: {context_info.get('context_tokens', 0)}")
    print(f"Completion tokens: {context_info.get('completion_tokens', 0)}")
    print(f"Workshops used: {', '.join(context_info.get('workshops_used', []))}")

def check_database_status():
    """Check the status of the vector database"""
    print("🔍 Checking database status...")
    
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client, COLLECTION_NAME)
        count = collection.count()
        
        print(f"✅ Database connection successful")
        print(f"📊 Total chunks in database: {count}")
        
        if count == 0:
            print("⚠️  Database is empty. Run with --action populate to add content.")
        else:
            # Get sample of workshops
            sample_results = collection.query(
                query_embeddings=[[0.0] * 1536],  # dummy embedding
                n_results=min(5, count)
            )
            
            workshops = set()
            for metadata in sample_results['metadatas'][0]:
                workshops.add(metadata.get('workshop_id', 'Unknown'))
            
            print(f"🏷️  Workshops in database: {', '.join(sorted(workshops))}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Standalone Vector Embedding Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standalone_vector_emb.py --action status
  python standalone_vector_emb.py --action populate
  python standalone_vector_emb.py --action query --question "What is Modal?"
  python standalone_vector_emb.py --action answer --question "How does chunking work?"
        """
    )
    
    parser.add_argument(
        "--action", 
        choices=["populate", "query", "answer", "status"],
        required=True,
        help="Action to perform"
    )
    
    parser.add_argument(
        "--question",
        help="Question to ask (required for query and answer actions)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.action in ["query", "answer"] and not args.question:
        print("❌ Error: --question is required for query and answer actions")
        sys.exit(1)
    
    print("🚀 Discord Chat Bot - Standalone Vector Embedding Tool")
    print("="*60)
    
    # Setup environment
    setup_environment()
    
    # Execute action
    if args.action == "populate":
        populate_database()
    elif args.action == "query":
        query_database(args.question)
    elif args.action == "answer":
        answer_with_llm(args.question)
    elif args.action == "status":
        check_database_status()
    
    print("\n✅ Operation completed!")

if __name__ == "__main__":
    main() 