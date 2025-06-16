"""
Meta-Question Handler for Workshop Course
Handles questions about course structure, speakers, and workshop organization
"""

import re
from typing import Dict, List, Tuple
from smart_workshop_retrieval import WORKSHOP_TOPICS, count_tokens

# Enhanced course metadata
COURSE_METADATA = {
    "course_info": {
        "title": "Generative AI and SDLC for LLMs Course", 
        "total_workshops": 8,
        "instructor": "Hugo Bowne-Anderson",
        "description": "A comprehensive course covering the software development lifecycle for LLM-powered applications"
    },
    "workshops": {
        "WS1": {
            "title": "Generative AI and SDLC for LLMs",
            "instructor": "Hugo Bowne-Anderson",
            "topics": ["What is Generative AI?", "SDLC for LLM applications", "Non-deterministic systems", "Tools and frameworks"]
        },
        "WS2": {
            "title": "Prompt Engineering in the LLM SDLC",
            "instructor": "Hugo Bowne-Anderson", 
            "topics": ["API parameters", "Prompt engineering basics", "Iterative refinement"]
        },
        "WS3": {
            "title": "Evaluation and Iteration",
            "instructor": "Hugo Bowne-Anderson",
            "topics": ["LLM output evaluation", "Metrics for success", "Feedback loops"]
        },
        "WS4": {
            "title": "Observability and Debugging", 
            "instructor": "Stefan",
            "topics": ["Logging and tracing", "Debugging LLM issues", "Production monitoring"]
        },
        "WS5": {
            "title": "Information Retrieval -> Agents",
            "instructor": "Hugo Bowne-Anderson",
            "guest_speaker": "William Horton",
            "topics": ["Embeddings", "Vector stores", "RAG systems"]
        },
        "WS6": {
            "title": "Structured Outputs, Function Calling, and Agentic Workflows",
            "instructor": "Hugo Bowne-Anderson",
            "topics": ["Structured outputs", "Function calling", "Agentic workflows"]
        },
        "WS7": {
            "title": "Multi-Agentic Workflows", 
            "instructor": "Hugo Bowne-Anderson",
            "topics": ["Advanced prompt optimization", "Multi-agent collaboration"]
        },
        "WS8": {
            "title": "Fine-tuning and Production LLM Applications",
            "instructor": "Hugo Bowne-Anderson", 
            "topics": ["Fine-tuning basics", "Dataset preparation", "Production deployment"]
        }
    },
    "speakers": {
        "Hugo Bowne-Anderson": {
            "role": "Main Instructor & Course Creator",
            "workshops": ["WS1", "WS2", "WS3", "WS4", "WS5", "WS6", "WS7", "WS8"],
            "bio": "Primary instructor and course designer"
        },
        "Stefan": {
            "role": "Guest Expert - Testing & Development",
            "workshops": ["WS4"],
            "specialty": "Testing, development loops, and production practices"
        },
        "William Horton": {
            "role": "Guest Expert - Production ML",
            "workshops": ["WS5"],
            "specialty": "Production machine learning systems and deployment"
        }
    }
}

class MetaQuestionHandler:
    """Handles meta-questions about course structure, speakers, workshops"""
    
    def __init__(self):
        self.meta_patterns = {
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
    
    def is_meta_question(self, question: str) -> str:
        """Determine if question is meta and what type"""
        question_lower = question.lower()
        
        for category, patterns in self.meta_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return category
        
        return "content"  # Not a meta question
    
    def answer_meta_question(self, question: str) -> Tuple[str, Dict]:
        """Answer meta-questions about the course"""
        question_type = self.is_meta_question(question)
        
        if question_type == "speakers":
            return self._answer_speakers_question(question)
        elif question_type == "course_structure":
            return self._answer_course_structure_question(question)
        elif question_type == "specific_workshop":
            return self._answer_specific_workshop_question(question)
        else:
            return "I couldn't understand that meta-question.", {"success": False}
    
    def _answer_speakers_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions about speakers and instructors"""
        question_lower = question.lower()
        
        # Check if asking specifically about first workshop
        if "first" in question_lower:
            first_ws = COURSE_METADATA["workshops"]["WS1"]
            answer = f"The first workshop '{first_ws['title']}' was given by **{first_ws['instructor']}**, who is the main instructor and course creator."
            
            context_info = {
                "question_type": "speakers_first",
                "success": True,
                "context_tokens": count_tokens(answer)
            }
            return answer, context_info
        
        # General speakers question
        answer_parts = ["**Course Speakers and Instructors:**\n"]
        
        for speaker, info in COURSE_METADATA["speakers"].items():
            answer_parts.append(f"**{speaker}** - {info['role']}")
            if info.get('specialty'):
                answer_parts.append(f"  • Specialty: {info['specialty']}")
            if info.get('workshops'):
                workshops = ", ".join(info['workshops'])
                answer_parts.append(f"  • Workshops: {workshops}")
            answer_parts.append("")
        
        answer = "\n".join(answer_parts)
        context_info = {
            "question_type": "speakers",
            "success": True,
            "context_tokens": count_tokens(answer)
        }
        
        return answer, context_info
    
    def _answer_course_structure_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions about course structure and workshop list"""
        course_info = COURSE_METADATA["course_info"]
        
        answer_parts = [
            f"**{course_info['title']}**\n",
            f"This course contains **{course_info['total_workshops']} workshops** covering {course_info['description']}.\n",
            "**Complete Workshop List:**\n"
        ]
        
        for ws_id, ws_info in COURSE_METADATA["workshops"].items():
            instructor = ws_info["instructor"]
            if ws_info.get("guest_speaker"):
                instructor += f" (with guest {ws_info['guest_speaker']})"
            answer_parts.append(f"**{ws_id}**: {ws_info['title']}")
            answer_parts.append(f"  • Instructor: {instructor}")
            answer_parts.append("")
        
        answer = "\n".join(answer_parts)
        context_info = {
            "question_type": "course_structure",
            "success": True,
            "context_tokens": count_tokens(answer)
        }
        
        return answer, context_info
    
    def _answer_specific_workshop_question(self, question: str) -> Tuple[str, Dict]:
        """Answer questions about specific workshops"""
        question_lower = question.lower()
        
        # Extract workshop number/identifier
        workshop_id = None
        
        # Check for workshop number
        number_match = re.search(r'workshop\s*([1-8])', question_lower)
        if number_match:
            workshop_id = f"WS{number_match.group(1)}"
        
        # Check for WS format
        ws_match = re.search(r'ws\s*([1-8])', question_lower)
        if ws_match:
            workshop_id = f"WS{ws_match.group(1)}"
        
        # Check for "first workshop"
        if "first" in question_lower:
            workshop_id = "WS1"
        
        if workshop_id and workshop_id in COURSE_METADATA["workshops"]:
            ws_info = COURSE_METADATA["workshops"][workshop_id]
            
            answer_parts = [
                f"**{workshop_id}: {ws_info['title']}**\n",
                f"**Instructor**: {ws_info['instructor']}"
            ]
            
            if ws_info.get("guest_speaker"):
                answer_parts.append(f"**Guest Speaker**: {ws_info['guest_speaker']}")
            
            answer_parts.append("\n**Topics Covered:**")
            for topic in ws_info["topics"]:
                answer_parts.append(f"• {topic}")
            
            answer = "\n".join(answer_parts)
            context_info = {
                "question_type": "specific_workshop",
                "workshop_id": workshop_id,
                "success": True,
                "context_tokens": count_tokens(answer)
            }
            
            return answer, context_info
        
        # Couldn't identify specific workshop
        return "I couldn't identify which workshop you're asking about. Please specify a workshop number (1-8) or say 'first workshop'.", {"success": False}

# Simple interface functions
def handle_meta_question(question: str) -> Tuple[str, Dict]:
    """Handle meta-questions about the course"""
    handler = MetaQuestionHandler()
    return handler.answer_meta_question(question)

def is_meta_question(question: str) -> bool:
    """Check if a question is about course structure/meta information"""
    handler = MetaQuestionHandler()
    return handler.is_meta_question(question) != "content"

def test_meta_questions():
    """Test the meta question handler"""
    test_questions = [
        "Who gave the first workshop?",
        "What are the workshops of this course?", 
        "What are the speakers?",
        "Who taught workshop 5?",
        "What does workshop 4 cover?",
        "How many workshops are there?",
        "Who is the instructor?"
    ]
    
    print("🧪 Testing Meta Question Handler")
    print("=" * 50)
    
    handler = MetaQuestionHandler()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        question_type = handler.is_meta_question(question)
        print(f"   Type: {question_type}")
        
        if question_type != "content":
            answer, info = handler.answer_meta_question(question)
            if info.get('success'):
                print(f"   ✅ Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            else:
                print(f"   ❌ Failed: {answer}")
        else:
            print(f"   ➡️ Would route to content retrieval")
        
        print("-" * 30)

if __name__ == "__main__":
    test_meta_questions() 