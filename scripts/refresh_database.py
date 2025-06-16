#!/usr/bin/env python3
"""
Orchestration script to refresh the vector database.

This script performs two critical actions:
1. Clears the existing ChromaDB collection to remove any old or corrupted data.
2. Reprocesses all workshop transcripts from the data directory and stores
   the embeddings and metadata correctly in the fresh collection.

Running this script is essential to fix data corruption issues, such as all
chunks being incorrectly associated with a single workshop.
"""

import sys
import os

# Add src to path to be able to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.multi_workshop_vector import clear_collection, process_all_workshops, get_collection_status, COLLECTION_NAME

def main():
    """Main function to execute the database refresh."""
    print("--- Starting Vector Database Refresh ---")
    
    # --- Step 1: Clear the existing collection ---
    print("\n[Phase 1/2] Clearing the collection to ensure a fresh start.")
    clear_collection(COLLECTION_NAME)
    print("[Phase 1/2] Collection cleared successfully.")
    
    # Verify the collection is empty
    print("\nVerifying collection status after clearing...")
    get_collection_status(COLLECTION_NAME)
    
    # --- Step 2: Reprocess all workshops ---
    print("\n[Phase 2/2] Processing all workshops and ingesting into the database.")
    processed_workshops = process_all_workshops(COLLECTION_NAME)
    
    if processed_workshops:
        print(f"\nSuccessfully processed {len(processed_workshops)} workshops: {', '.join(processed_workshops)}")
    else:
        print("\nNo new workshops were processed. The database may be up to date or source files are missing.")

    # --- Step 3: Final Verification ---
    print("\n--- Refresh Complete ---")
    print("Verifying final collection status:")
    final_status = get_collection_status(COLLECTION_NAME)
    if final_status and final_status.get('total_chunks', 0) > 0:
        print("\n✅ The vector database has been successfully refreshed with new data.")
    else:
        print("\n⚠️  Warning: The vector database is still empty after the refresh process.")

if __name__ == "__main__":
    main() 