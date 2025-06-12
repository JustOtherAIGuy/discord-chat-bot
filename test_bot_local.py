#!/usr/bin/env python3
"""
Local test script for Discord bot logic

This script tests the bot's mention detection and response logic locally
before deploying to Modal.
"""

import os
import sys
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, 'src')

def test_mention_detection():
    """Test the bot_is_mentioned function"""
    from modal_discord_bot import bot_is_mentioned
    
    # Mock client user
    mock_client_user = MagicMock()
    mock_client_user.mention = "<@123456789>"
    
    test_cases = [
        ("hey bot, what's up?", True),
        ("Bot help me", True), 
        ("Can you help, bot?", True),
        ("bot", True),
        ("BOT", True),
        ("<@123456789> hello", True),
        ("Hello <@123456789>", True),
        ("Ask the bot a question", True),
        ("Both are good.", False),
        ("This is about robotics", False),
        ("Just a normal message", False),
        ("The chatbot is useful", False),
        ("", False),
    ]
    
    print("🧪 Testing mention detection...")
    passed = 0
    failed = 0
    
    for content, expected in test_cases:
        result = bot_is_mentioned(content, mock_client_user)
        if result == expected:
            print(f"✅ '{content}' -> {result}")
            passed += 1
        else:
            print(f"❌ '{content}' -> {result} (expected {expected})")
            failed += 1
    
    print(f"\n📊 Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_vector_search():
    """Test vector search functionality"""
    print("\n🔍 Testing vector search...")
    
    try:
        from vector_emb import answer_question
        
        # Test question
        question = "What is Modal?"
        
        print(f"Question: {question}")
        context, sources, chunks = answer_question(question)
        
        print(f"✅ Retrieved {len(chunks)} chunks")
        print(f"✅ Context length: {len(context)} characters")
        print(f"✅ Sources: {len(sources)}")
        
        if chunks:
            print(f"✅ First chunk: {chunks[0]['text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 Testing OpenAI connection...")
    
    try:
        from vector_emb import get_openai_client
        
        client = get_openai_client()
        print("✅ OpenAI client created successfully")
        
        # Test a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test' if you can hear me"}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI API response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Local Bot Testing")
    print("===================")
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")
    
    # Run tests
    tests = [test_mention_detection]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 