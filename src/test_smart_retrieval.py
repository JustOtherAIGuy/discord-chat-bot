#!/usr/bin/env python3
"""
Test script for the Smart Workshop Retrieval System
This demonstrates how the new system solves context length issues
"""

import sys
import os
from smart_workshop_retrieval import (
    smart_answer_question, route_question, test_context_limits, 
    list_workshop_topics, SmartWorkshopRetrieval
)
from multi_workshop_vector import process_all_workshops, get_collection_status

def demo_smart_retrieval():
    """Demonstrate the smart retrieval system capabilities"""
    print("🚀 Smart Workshop Retrieval System Demo")
    print("=" * 60)
    
    # Show available workshops
    print("\n📚 Available Workshops:")
    topics = list_workshop_topics()
    for ws_id, title in topics.items():
        print(f"  {ws_id}: {title}")
    
    # Check if workshops are processed
    print("\n🔍 Checking collection status...")
    status = get_collection_status()
    
    if not status or status.get('total_chunks', 0) == 0:
        print("⚠️  No workshops found in collection. Processing all workshops...")
        processed = process_all_workshops()
        print(f"✅ Processed workshops: {', '.join(processed)}")
    else:
        print(f"✅ Collection has {status['total_chunks']} chunks")
    
    # Test questions with different complexity levels
    test_questions = [
        {
            "question": "What is prompt engineering?",
            "description": "Simple question about one specific topic"
        },
        {
            "question": "How do I evaluate the quality of my LLM outputs and debug issues?",
            "description": "Question spanning multiple workshops"
        },
        {
            "question": "What are the best practices for productionizing LLM applications with proper monitoring?",
            "description": "Complex question requiring multiple workshop content"
        }
    ]
    
    print(f"\n🧪 Testing with different question types:")
    print("-" * 60)
    
    for i, test_case in enumerate(test_questions, 1):
        question = test_case["question"]
        description = test_case["description"]
        
        print(f"\n{i}. {description}")
        print(f"   Question: {question}")
        
        # Show routing
        relevant_workshops = route_question(question, max_workshops=2)
        print(f"   🎯 Routed to: {relevant_workshops}")
        
        # Show context size test
        print(f"   📏 Context size test:")
        try:
            retrieval_system = SmartWorkshopRetrieval(model="gpt-4o-mini")
            context, sources, workshops = retrieval_system.get_smart_context(question, 2, 2)
            context_tokens = len(context.split()) * 1.3  # Rough token estimate
            print(f"      Context: ~{context_tokens:.0f} tokens, {len(sources)} chunks")
        except Exception as e:
            print(f"      Error: {e}")
        
        # Get answer
        print(f"   💬 Getting answer...")
        answer, info = smart_answer_question(question, model="gpt-4o-mini")
        
        if info.get('success', False):
            print(f"   ✅ Success! Context: {info['context_tokens']} tokens")
            print(f"      Workshops used: {', '.join(info['workshops_used'])}")
            print(f"      Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
        else:
            print(f"   ❌ Failed: {answer}")
        
        print("-" * 60)

def compare_old_vs_new():
    """Compare the old approach vs new smart approach"""
    print(f"\n🔄 Comparing Old vs New Approach")
    print("=" * 60)
    
    question = "How do I evaluate and debug my LLM applications?"
    
    print(f"Question: {question}")
    
    # Show what old approach would do (simulate)
    print(f"\n❌ Old Approach (would fail):")
    print(f"   - Retrieves 5+ chunks from ALL workshops")
    print(f"   - No intelligent filtering")
    print(f"   - Results in 23,930+ tokens (exceeds 8,192 limit)")
    print(f"   - Error: 'maximum context length exceeded'")
    
    # Show new approach
    print(f"\n✅ New Smart Approach:")
    
    # Route question
    workshops = route_question(question, max_workshops=2)
    print(f"   1. Routes to relevant workshops: {workshops}")
    
    # Get smart context
    retrieval_system = SmartWorkshopRetrieval(model="gpt-4o-mini")
    context, sources, _ = retrieval_system.get_smart_context(question, 2, 2)
    print(f"   2. Selects {len(sources)} most relevant chunks")
    print(f"   3. Builds context with strict token limits")
    
    # Answer question
    answer, info = smart_answer_question(question)
    if info.get('success'):
        print(f"   4. ✅ Successfully generates answer!")
        print(f"      📊 Tokens used: {info['context_tokens']}/{info['max_context_tokens']}")
        print(f"      📚 Workshops: {', '.join(info['workshops_used'])}")
        print(f"      💬 Answer: {answer[:300]}...")
    else:
        print(f"   4. ❌ Still failed: {answer}")

def interactive_demo():
    """Interactive demo where user can ask questions"""
    print(f"\n🎮 Interactive Demo")
    print("=" * 60)
    print("Ask questions about the workshops! Type 'quit' to exit.")
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        print(f"\n🎯 Routing question...")
        workshops = route_question(question)
        print(f"   Relevant workshops: {workshops}")
        
        print(f"🤔 Thinking...")
        answer, info = smart_answer_question(question)
        
        if info.get('success'):
            print(f"\n💡 Answer:")
            print(f"{answer}")
            print(f"\n📊 Stats: {info['context_tokens']} tokens, {info['num_chunks']} chunks, workshops: {', '.join(info['workshops_used'])}")
        else:
            print(f"\n❌ Error: {answer}")

if __name__ == "__main__":
    try:
        # Run main demo
        demo_smart_retrieval()
        
        # Compare approaches
        compare_old_vs_new()
        
        # Interactive demo
        if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
            interactive_demo()
        else:
            print(f"\n💡 Tip: Run with --interactive flag for hands-on testing!")
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 