"""
Enhanced Workshop Retrieval System
Handles both content-specific questions AND meta-questions about course structure, speakers, etc.
"""

import os
import re
from typing import List, Dict, Any, Optional, Union, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from smart_workshop_retrieval import SmartWorkshopRetrieval, WORKSHOP_TOPICS, MODEL_LIMITS
from multi_workshop_vector import (
    discover_workshops, get_chroma_client, get_or_create_collection,
    retrieve_relevant_chunks, count_tokens, get_openai_client, COLLECTION_NAME
)

# Enhanced workshop metadata with speakers and course structure
ENHANCED_WORKSHOP_INFO = {
    "course_overview": {
        "title": "Generative AI and SDLC for LLMs Course",
        "total_workshops": 8,
        "description": "A comprehensive course covering the software development lifecycle for LLM-powered applications",
        "workshops": [
            "WS1: Generative AI and SDLC for LLMs",
            "WS2: Prompt Engineering in the LLM SDLC", 
            "WS3: Evaluation and Iteration",
            "WS4: Observability and Debugging",
            "WS5: Information Retrieval -> Agents",
            "WS6: Structured Outputs, Function Calling, and Agentic Workflows",
            "WS7: Multi-Agentic Workflows",
            "WS8: Fine-tuning and Production LLM Applications"
        ]
    },
    "speakers": {
        "hugo bowne-anderson": {
            "role": "Main Instructor/Course Creator",
            "workshops": ["WS1", "WS2", "WS3", "WS4", "WS5", "WS6", "WS7", "WS8"],
            "description": "Primary instructor and course designer"
        },
        "William Horton": {
            "role": "Guest Speaker", 
            "workshops": ["WS5"],
            "topic": "Production ML Systems",
            "description": "Expert in production machine learning systems"
        },
        "Stefan": {
            "role": "Guest Speaker",
            "workshops": ["WS4"], 
            "topic": "Testing and Development Loops",
            "description": "Expert in testing and development practices"
        }
    }
}

class EnhancedWorkshopRetrieval(SmartWorkshopRetrieval):
    """Enhanced retrieval system that handles both content and meta-questions"""
    
    def __init__(self, model: str = "gpt-4o-mini", max_context_tokens: int = None):
        super().__init__(model, max_context_tokens)
        self.meta_question_patterns = self._build_meta_patterns()
    
    def _build_meta_patterns(self) -> Dict[str, List[str]]:
        """Build patterns to identify meta-questions about course structure"""
        return {
            "speakers": [
                "who gave", "who presented", "who taught", "who is the instructor",
                "who led", "speakers", "instructors", "teachers", "presenters"
            ],
            "course_structure": [
                "what are the workshops", "list workshops", "course structure",
                "workshop topics", "workshop list", "how many workshops",
                "course overview", "workshop overview"
            ],
            "first_workshop": [
                "first workshop", "workshop 1", "initial workshop", "starting workshop"
            ],
            "specific_workshop": [
                "workshop [0-9]", "ws[0-9]", "which workshop covers", "workshop about"
            ]
        }
    
    def classify_question_type(self, question: str) -> str:
        """Classify if this is a meta-question or content-question"""
        question_lower = question.lower()
        
        for question_type, patterns in self.meta_question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return question_type
        
        return "content"
    
    def answer_meta_question(self, question: str, question_type: str) -> Tuple[str, Dict]:
        """Answer meta-questions about course structure, speakers, etc."""
        
        if question_type == "speakers":
            return self._answer_speaker_question(question)
        elif question_type == "course_structure":
            return self._answer_course_structure_question(question)
        elif question_type == "first_workshop":
            return self._answer_first_workshop_question(question)
        elif question_type == "specific_workshop":
            return self._answer_specific_workshop_question(question)
        else:
            return "I couldn't understand that question about the course structure.", {}
    
    def _answer_speaker_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions about speakers and instructors"""
        speakers_info = ENHANCED_WORKSHOP_INFO["speakers"]
        
        answer_parts = []
        answer_parts.append("Here are the speakers and instructors for this course:\n")
        
        for speaker, info in speakers_info.items():
            answer_parts.append(f"**{speaker.title()}**: {info['role']}")
            if info.get('workshops'):
                workshops_list = ", ".join(info['workshops'])
                answer_parts.append(f"  - Taught: {workshops_list}")
            if info.get('topic'):
                answer_parts.append(f"  - Specialty: {info['topic']}")
            if info.get('description'):
                answer_parts.append(f"  - {info['description']}")
            answer_parts.append("")
        
        # Check if asking about first workshop specifically
        if "first" in question.lower():
            answer_parts.append("\nThe first workshop (WS1) was given by **Hugo Bowne-Anderson**, who is the main instructor and course creator.")
        
        context_info = {
            "question_type": "speakers",
            "workshops_used": [],
            "context_tokens": count_tokens(" ".join(answer_parts)),
            "success": True
        }
        
        return "\n".join(answer_parts), context_info
    
    def _answer_course_structure_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions about course structure and workshop list"""
        course_info = ENHANCED_WORKSHOP_INFO["course_overview"]
        
        answer_parts = []
        answer_parts.append(f"**{course_info['title']}**\n")
        answer_parts.append(f"This course contains {course_info['total_workshops']} workshops covering {course_info['description']}.\n")
        answer_parts.append("**Workshop List:**")
        
        for workshop in course_info["workshops"]:
            answer_parts.append(f"• {workshop}")
        
        answer_parts.append(f"\n{course_info['description']}")
        
        context_info = {
            "question_type": "course_structure", 
            "workshops_used": ["ALL"],
            "context_tokens": count_tokens(" ".join(answer_parts)),
            "success": True
        }
        
        return "\n".join(answer_parts), context_info
    
    def _answer_first_workshop_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions specifically about the first workshop"""
        ws1_info = WORKSHOP_TOPICS["WS1"]
        speaker_info = ENHANCED_WORKSHOP_INFO["speakers"]["hugo bowne-anderson"]
        
        answer_parts = []
        answer_parts.append("**First Workshop Information:**\n")
        answer_parts.append(f"**Workshop 1**: {ws1_info['title']}")
        answer_parts.append(f"**Instructor**: Hugo Bowne-Anderson ({speaker_info['role']})")
        answer_parts.append(f"\n**Topics Covered:**")
        
        # Get key topics from the workshop
        key_topics = [
            "What is Generative AI?",
            "Overview of the Software Development Lifecycle (SDLC) for LLM-powered applications", 
            "Non-deterministic systems and why iteration is critical",
            "Key tools and frameworks for LLM-based applications",
            "Setting up foundational applications"
        ]
        
        for topic in key_topics:
            answer_parts.append(f"• {topic}")
        
        context_info = {
            "question_type": "first_workshop",
            "workshops_used": ["WS1"],
            "context_tokens": count_tokens(" ".join(answer_parts)),
            "success": True
        }
        
        return "\n".join(answer_parts), context_info
    
    def _answer_specific_workshop_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions about specific workshops"""
        # Extract workshop number from question
        workshop_match = re.search(r'workshop\s*([0-9]+)|ws\s*([0-9]+)', question.lower())
        
        if workshop_match:
            workshop_num = workshop_match.group(1) or workshop_match.group(2)
            workshop_id = f"WS{workshop_num}"
            
            if workshop_id in WORKSHOP_TOPICS:
                ws_info = WORKSHOP_TOPICS[workshop_id]
                answer_parts = []
                answer_parts.append(f"**{workshop_id}**: {ws_info['title']}\n")
                answer_parts.append("**Key Topics:**")
                
                for keyword in ws_info['keywords'][:8]:  # Show top 8 keywords
                    answer_parts.append(f"• {keyword.title()}")
                
                # Add speaker info if available
                for speaker, info in ENHANCED_WORKSHOP_INFO["speakers"].items():
                    if workshop_id in info.get('workshops', []):
                        answer_parts.append(f"\n**Instructor**: {speaker.title()} ({info['role']})")
                        if info.get('topic'):
                            answer_parts.append(f"**Specialty**: {info['topic']}")
                
                context_info = {
                    "question_type": "specific_workshop",
                    "workshops_used": [workshop_id],
                    "context_tokens": count_tokens(" ".join(answer_parts)),
                    "success": True
                }
                
                return "\n".join(answer_parts), context_info
        
        return "I couldn't identify which specific workshop you're asking about. Please specify a workshop number (1-8).", {}
    
    def extract_speakers_from_transcripts(self) -> Dict[str, List[str]]:
        """Extract speaker information from actual transcript files"""
        speakers_by_workshop = {}
        workshops = discover_workshops()
        
        speaker_pattern = r'^([a-zA-Z ]+):'
        
        for workshop_id, workshop_info in workshops.items():
            try:
                with open(workshop_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                speakers = set()
                for line in content.split('\n'):
                    match = re.match(speaker_pattern, line.strip())
                    if match:
                        speaker_name = match.group(1).strip().lower()
                        # Filter out timestamps and other non-speaker content
                        if not re.match(r'^\d+:\d+:\d+', speaker_name) and len(speaker_name) > 3:
                            speakers.add(speaker_name)
                
                speakers_by_workshop[workshop_id] = list(speakers)
                
            except Exception as e:
                print(f"Error reading {workshop_id}: {e}")
                speakers_by_workshop[workshop_id] = []
        
        return speakers_by_workshop
    
    def answer_question(self, question: str, max_workshops: int = 2, 
                       chunks_per_workshop: int = 2) -> Tuple[str, Dict]:
        """Enhanced answer method that handles both meta and content questions"""
        
        # First, classify the question type
        question_type = self.classify_question_type(question)
        
        print(f"Question type: {question_type}")
        
        if question_type != "content":
            # Handle meta-questions directly
            return self.answer_meta_question(question, question_type)
        else:
            # Use the standard smart retrieval for content questions
            return super().answer_question(question, max_workshops, chunks_per_workshop)

# Enhanced interface functions
def enhanced_answer_question(question: str, model: str = "gpt-4o-mini") -> Tuple[str, Dict]:
    """
    Enhanced function that handles both content and meta-questions
    """
    retrieval_system = EnhancedWorkshopRetrieval(model=model)
    return retrieval_system.answer_question(question)

def test_meta_questions():
    """Test the system with meta-questions"""
    test_questions = [
        "Who gave the first workshop?",
        "What are the workshops of this course?", 
        "What are the speakers?",
        "Who is the instructor?",
        "How many workshops are there?",
        "What does workshop 5 cover?",
        "Who taught workshop 4?"
    ]
    
    print("🧪 Testing Enhanced Workshop Retrieval with Meta-Questions")
    print("=" * 70)
    
    retrieval_system = EnhancedWorkshopRetrieval()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        question_type = retrieval_system.classify_question_type(question)
        print(f"   Type: {question_type}")
        
        answer, info = retrieval_system.answer_question(question)
        
        if info.get('success', True):
            print(f"   ✅ Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
        else:
            print(f"   ❌ Failed: {answer}")
        
        print("-" * 50)

def test_mixed_questions():
    """Test with a mix of meta and content questions"""
    mixed_questions = [
        ("Who gave the first workshop?", "meta"),
        ("What is prompt engineering?", "content"), 
        ("What are all the workshops?", "meta"),
        ("How do I evaluate LLM outputs?", "content"),
        ("Who are the speakers?", "meta")
    ]
    
    print("\n🔄 Testing Mixed Question Types")
    print("=" * 50)
    
    for question, expected_type in mixed_questions:
        print(f"\nQuestion: {question} (expected: {expected_type})")
        answer, info = enhanced_answer_question(question)
        
        actual_type = info.get('question_type', 'content')
        print(f"Classified as: {actual_type}")
        
        if info.get('success', True):
            print(f"✅ Answer: {answer[:150]}...")
        else:
            print(f"❌ Failed: {answer}")

if __name__ == "__main__":
    # Test meta-questions
    test_meta_questions()
    
    # Test mixed questions
    test_mixed_questions()
    
    # Test speaker extraction
    print("\n🔍 Extracting speakers from transcripts...")
    retrieval_system = EnhancedWorkshopRetrieval()
    speakers = retrieval_system.extract_speakers_from_transcripts()
    print("Speakers found:")
    for ws, speaker_list in speakers.items():
        if speaker_list:
            print(f"  {ws}: {', '.join(speaker_list)}")
        else:
            print(f"  {ws}: No speakers found") 