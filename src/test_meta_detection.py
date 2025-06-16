#!/usr/bin/env python3
"""
Simple test for meta-question detection logic
Tests without requiring OpenAI or other external dependencies
"""

import re

# Meta-question patterns (copied from smart_workshop_retrieval.py)
META_PATTERNS = {
    "speakers": [
        r"who (gave|presented|taught|led|is|are)", 
        r"(speakers?|instructors?|teachers?|presenters?)",
        r"who.*first workshop",
        r"who.*workshop"
    ],
    "course_structure": [
        r"what are.*(workshops?|course)",
        r"list.*(workshops?|course)",
        r"how many workshops?",
        r"course (structure|overview)",
        r"workshop (list|overview|topics)"
    ],
    "specific_workshop": [
        r"workshop\s*([1-8]|one|two|three|four|five|six|seven|eight)",
        r"ws\s*[1-8]",
        r"first workshop",
        r"what.*workshop.*cover"
    ]
}

def detect_meta_question_type(question: str) -> str:
    """Determine if question is meta and what type"""
    question_lower = question.lower()
    
    for category, patterns in META_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, question_lower):
                return category
    
    return "content"  # Not a meta question

def test_detection_logic():
    """Test the meta-question detection logic"""
    
    test_cases = [
        # User's specific failing questions
        ("who gave the first workshop", "speakers"),
        ("what are the workshops of this course", "course_structure"), 
        ("what are the speakers", "speakers"),
        
        # Additional meta-questions
        ("Who taught workshop 5?", "speakers"),
        ("What does workshop 4 cover?", "specific_workshop"),
        ("How many workshops are there?", "course_structure"),
        ("who is the instructor", "speakers"),
        ("list all workshops", "course_structure"),
        ("first workshop", "specific_workshop"),
        
        # Content questions (should be detected as content)
        ("What is prompt engineering?", "content"),
        ("How do I evaluate LLM outputs?", "content"),
        ("Explain fine-tuning", "content"),
        ("debugging llm applications", "content")
    ]
    
    print("🔍 Testing Meta-Question Detection Logic")
    print("=" * 60)
    print("This tests whether questions are correctly classified as meta vs content\n")
    
    correct = 0
    total = len(test_cases)
    
    for i, (question, expected_type) in enumerate(test_cases, 1):
        detected_type = detect_meta_question_type(question)
        is_correct = detected_type == expected_type
        
        status = "✅" if is_correct else "❌"
        if is_correct:
            correct += 1
        
        print(f"{i:2d}. {status} '{question}'")
        print(f"     Expected: {expected_type}, Detected: {detected_type}")
        
        if not is_correct:
            print(f"     ⚠️  MISMATCH!")
        print()
    
    accuracy = (correct / total) * 100
    print(f"📊 Detection Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("🎉 Excellent detection accuracy!")
    elif accuracy >= 80:
        print("👍 Good detection accuracy!")
    else:
        print("⚠️  Detection accuracy needs improvement")

def test_user_specific_questions():
    """Test specifically the user's failing questions"""
    user_questions = [
        "who gave the first workshop",
        "what are the workshops of this course", 
        "what are the speakers"
    ]
    
    print(f"\n🎯 Testing User's Specific Questions")
    print("=" * 40)
    
    for question in user_questions:
        detected_type = detect_meta_question_type(question)
        print(f"Q: '{question}'")
        print(f"   Detected as: {detected_type}")
        
        if detected_type == "content":
            print(f"   ❌ PROBLEM: This should be detected as meta-question!")
        else:
            print(f"   ✅ SUCCESS: Correctly detected as meta-question")
        print()

if __name__ == "__main__":
    # Test detection logic
    test_detection_logic()
    
    # Test user's specific questions
    test_user_specific_questions()
    
    print("\n💡 Next Steps:")
    print("1. If detection is working, the enhanced system should answer these meta-questions")
    print("2. Meta-questions bypass vector retrieval and use structured course data")
    print("3. Content questions still use the smart workshop routing system") 