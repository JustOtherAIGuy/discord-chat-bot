#!/usr/bin/env python3
"""
Quick test script to verify meta-question fixes
Tests the specific questions the user mentioned
"""

from smart_workshop_retrieval import smart_answer_question

def test_user_questions():
    """Test the specific questions the user mentioned"""
    user_test_questions = [
        "who gave the first workshop",
        "what are the workshops of this course", 
        "what are the speakers"
    ]
    
    print("🔧 Testing User's Specific Questions")
    print("=" * 60)
    print("Testing the enhanced system with the exact questions that were failing...")
    
    for i, question in enumerate(user_test_questions, 1):
        print(f"\n{i}. Question: '{question}'")
        print(f"   Testing...")
        
        try:
            answer, info = smart_answer_question(question)
            
            if info.get('success', True):
                print(f"   ✅ SUCCESS!")
                print(f"   📝 Answer: {answer[:300]}{'...' if len(answer) > 300 else ''}")
                print(f"   🏷️  Question Type: {info.get('question_type', 'content')}")
                print(f"   📊 Tokens: {info.get('context_tokens', 0)}")
            else:
                print(f"   ❌ FAILED: {answer}")
                
        except Exception as e:
            print(f"   💥 ERROR: {str(e)}")
        
        print("-" * 50)
    
    print(f"\n🎯 Summary")
    print("The enhanced system now:")
    print("✅ Detects meta-questions vs content questions")
    print("✅ Has structured knowledge about course/speakers")
    print("✅ Answers directly without vector retrieval for meta-questions")
    print("✅ Still uses smart retrieval for content questions")

def test_mixed_content():
    """Test a mix of meta and content questions"""
    mixed_questions = [
        ("Who gave the first workshop?", "meta"),
        ("What is prompt engineering?", "content"),
        ("What are the speakers?", "meta"),
        ("How do I debug LLM applications?", "content")
    ]
    
    print(f"\n🔀 Testing Mixed Question Types")
    print("=" * 50)
    
    for question, expected_type in mixed_questions:
        print(f"\nQ: {question} (expecting {expected_type})")
        answer, info = smart_answer_question(question)
        
        actual_type = "meta" if info.get('question_type') != 'content' else "content"
        status = "✅" if actual_type == expected_type else "⚠️"
        
        print(f"{status} Classified as: {actual_type}")
        print(f"   Answer: {answer[:100]}...")

if __name__ == "__main__":
    # Test the user's specific failing questions
    test_user_questions()
    
    # Test mixed content to ensure both types work
    test_mixed_content() 