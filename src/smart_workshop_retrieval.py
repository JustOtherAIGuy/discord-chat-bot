import os
import json
import re
from typing import List, Dict, Any, Optional, Union, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from multi_workshop_vector import (
    discover_workshops, get_chroma_client, get_or_create_collection,
    retrieve_relevant_chunks, combine_chunks, count_tokens, 
    get_openai_client, COLLECTION_NAME, DEFAULT_MAX_CHUNKS
)

# Token limits for different models
MODEL_LIMITS = {
    "gpt-4o-mini": 8192,
    "gpt-4o": 128000,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384
}

# Workshop topic mappings from WS-Topics.md
WORKSHOP_TOPICS = {
    "WS1": {
        "title": "Generative AI and SDLC for LLMs",
        "keywords": [
            "generative ai", "sdlc", "software development lifecycle", "llm applications",
            "non-deterministic systems", "iteration", "tools", "frameworks", 
            "foundational app", "querying pdfs", "what is generative ai"
        ]
    },
    "WS2": {
        "title": "Prompt Engineering in the LLM SDLC", 
        "keywords": [
            "prompt engineering", "api knobs", "temperature", "top_p", "max_tokens",
            "system prompt", "prompt refinement", "prompt optimization", "prompting"
        ]
    },
    "WS3": {
        "title": "Evaluation and Iteration",
        "keywords": [
            "evaluation", "llm outputs", "qualitative", "quantitative", "metrics",
            "relevance", "coherence", "user satisfaction", "feedback loops",
            "thumbs up", "thumbs down", "assessment", "measuring performance"
        ]
    },
    "WS4": {
        "title": "Observability and Debugging",
        "keywords": [
            "observability", "debugging", "logging", "tracing", "monitoring",
            "performance", "hallucinations", "api failures", "production monitoring",
            "scaling observability", "troubleshooting", "errors"
        ]
    },
    "WS5": {
        "title": "Information Retrieval -> Agents",
        "keywords": [
            "embeddings", "vector stores", "information retrieval", "rag",
            "retrieval augmented generation", "semantic search", "vectors",
            "similarity search", "knowledge base", "document retrieval"
        ]
    },
    "WS6": {
        "title": "Structured Outputs, Function Calling, and Agentic Workflows",
        "keywords": [
            "structured outputs", "function calling", "agentic workflows", 
            "unstructured data", "linkedin profiles", "json responses",
            "api responses", "automate actions", "send email", "structured data"
        ]
    },
    "WS7": {
        "title": "Multi-Agentic Workflows",
        "keywords": [
            "multi-agent", "multi-agentic", "advanced prompt optimization",
            "dynamic prompts", "agent collaboration", "apis", "multiple models",
            "future trends", "open-source models", "lightweight deployment"
        ]
    },
    "WS8": {
        "title": "Fine-tuning and Production LLM Applications",
        "keywords": [
            "fine-tuning", "fine tuning", "datasets", "data collection", "data cleaning",
            "data formatting", "production", "productionizing", "reliability",
            "api scaling", "rate limits", "deployment", "training"
        ]
    }
}

# Course metadata for meta-questions
COURSE_METADATA = {
    "course_info": {
        "title": "Generative AI and SDLC for LLMs Course", 
        "total_workshops": 8,
        "main_instructor": "Hugo Bowne-Anderson",
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
            "topics": ["Embeddings", "Vector stores", "RAG systems", "Production ML"]
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
            "workshops": ["WS1", "WS2", "WS3", "WS5", "WS6", "WS7", "WS8"],
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

class SmartWorkshopRetrieval:
    def __init__(self, model: str = "gpt-4o-mini", max_context_tokens: int = None):
        self.model = model
        self.max_context_tokens = max_context_tokens or MODEL_LIMITS.get(model, 6000)
        # Reserve tokens for the question, system prompt, and response
        self.available_context_tokens = int(self.max_context_tokens * 0.65)  # Use 65% for context
        self.client = get_openai_client()
        
        print(f"Initialized Smart Retrieval for {model}")
        print(f"Max context tokens: {self.max_context_tokens}")
        print(f"Available for context: {self.available_context_tokens}")
        
        # Meta-question patterns
        self.meta_patterns = {
            "speakers": [
                r"\bwho (gave|presents?|presented|taught|teaches|is|are)\b",
                r"\b(speakers?|instructors?|teachers?|presenters?|hosts?)\b",
                r"\bwho.*(workshop|session)",
            ],
            "course_structure": [
                r"\b(what|which) are.*(workshops?|course|sessions?)\b",
                r"\blist.*(workshops?|course|sessions?)\b",
                r"\b(how many|number of) workshops?\b",
                r"\bcourse (structure|overview|topics|summary)\b",
                r"tell me about the course",
            ],
            "specific_workshop": [
                r"\bworkshop\s*([1-8]|one|two|three|four|five|six|seven|eight)\b",
                r"\bws\s*[1-8]\b",
                r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth) workshop\b",
                r"\b(1st|2nd|3rd|[4-8]th) workshop\b",
                r"\bwhat.*(workshop|session).*cover\b",
                r"tell me about.*workshop\b",
                r"information on.*workshop"
            ]
        }
        
    def route_question_to_workshops(self, question: str, max_workshops: int = 2) -> List[str]:
        """Route a question to the most relevant workshops using keyword matching"""
        question_lower = question.lower()
        workshop_scores = {}
        
        # Score workshops based on keyword matching
        for workshop_id, workshop_data in WORKSHOP_TOPICS.items():
            score = 0
            for keyword in workshop_data["keywords"]:
                if keyword in question_lower:
                    # Full keyword match gets more points
                    score += 2
                else:
                    # Partial matches get fewer points
                    keyword_words = keyword.split()
                    if len(keyword_words) > 1:
                        for word in keyword_words:
                            if word in question_lower and len(word) > 3:
                                score += 0.5
            
            workshop_scores[workshop_id] = score
        
        # Get top scoring workshops
        sorted_workshops = sorted(workshop_scores.items(), key=lambda x: x[1], reverse=True)
        
        # If no clear winners from keyword matching, use LLM classification
        if sorted_workshops[0][1] == 0:
            return self._llm_route_question(question, max_workshops)
        
        # Filter workshops with significant scores
        relevant_workshops = []
        for ws_id, score in sorted_workshops:
            if score > 0 and len(relevant_workshops) < max_workshops:
                relevant_workshops.append(ws_id)
        
        # If we don't have enough workshops, add the highest scoring ones
        if len(relevant_workshops) < max_workshops:
            for ws_id, score in sorted_workshops:
                if ws_id not in relevant_workshops and len(relevant_workshops) < max_workshops:
                    relevant_workshops.append(ws_id)
        
        print(f"Question: {question}")
        print(f"Routing to workshops: {relevant_workshops}")
        print(f"Workshop scores: {dict(sorted_workshops[:5])}")
        
        return relevant_workshops
    
    def _llm_route_question(self, question: str, max_workshops: int = 2) -> List[str]:
        """Use LLM to classify which workshops are most relevant when keyword matching fails"""
        workshop_descriptions = []
        for ws_id, ws_data in WORKSHOP_TOPICS.items():
            keywords_str = ", ".join(ws_data["keywords"][:5])
            workshop_descriptions.append(f"{ws_id}: {ws_data['title']} (Covers: {keywords_str})")
        
        workshops_text = "\n".join(workshop_descriptions)
        
        classification_prompt = f"""You are a course assistant. Your job is to find the most relevant workshop(s) for a user's question.

User's Question: "{question}"

Here are the available workshops and their topics:
{workshops_text}

Based on the user's question, which {max_workshops} workshops are the most likely to contain the answer?
Respond with only the workshop IDs (e.g., WS1, WS3) separated by commas. If no workshop seems relevant, respond with the single word "NONE".
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for routing
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0,
                max_tokens=50
            )
            
            response_text = response.choices[0].message.content.strip()

            if "NONE" in response_text:
                print("LLM routing found no relevant workshops.")
                return []

            workshop_ids = [ws.strip() for ws in response_text.split(",")]
            valid_workshops = [ws for ws in workshop_ids if ws in WORKSHOP_TOPICS.keys()]
            
            if valid_workshops:
                print(f"LLM routing selected workshops: {valid_workshops}")
                return valid_workshops[:max_workshops]
                
        except Exception as e:
            print(f"LLM routing failed: {e}")
        
        # Fallback if LLM fails or returns nothing valid
        print("LLM routing failed, returning empty list.")
        return []
    
    def get_smart_context(self, question: str, max_workshops: int = 2, 
                         chunks_per_workshop: int = 2) -> Tuple[str, List[Dict], List[str]]:
        """Get context for a question using smart workshop routing and strict token management"""
        
        # Route question to relevant workshops
        relevant_workshops = self.route_question_to_workshops(question, max_workshops)
        
        # Retrieve chunks from relevant workshops only
        all_chunks = []
        for workshop_id in relevant_workshops:
            chunks = retrieve_relevant_chunks(
                question=question,
                workshop_filter=workshop_id,
                n_results=chunks_per_workshop
            )
            # Add workshop priority for sorting
            for chunk in chunks:
                chunk['workshop_priority'] = relevant_workshops.index(workshop_id)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return "", [], relevant_workshops
        
        # Sort chunks by workshop priority and position
        sorted_chunks = sorted(all_chunks, key=lambda x: (
            x.get('workshop_priority', 999),
            int(x['metadata'].get('position', 999))
        ))
        
        # Build context within strict token limits
        context, used_chunks = self._build_context_within_strict_limits(sorted_chunks)
        
        # Format sources for used chunks only
        sources = []
        for chunk in used_chunks:
            metadata = chunk['metadata']
            sources.append({
                'workshop_id': metadata.get('workshop_id', 'Unknown'),
                'position': metadata.get('position', 'Unknown'),
                'timestamp': metadata.get('timestamp', 'Unknown'),
                'speaker': metadata.get('speaker', 'Unknown'),
                'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                'relevance': chunk.get('relevance', 1.0)
            })
        
        return context, sources, relevant_workshops
    
    def _build_context_within_strict_limits(self, chunks: List[Dict]) -> Tuple[str, List[Dict]]:
        """Build context from chunks while staying within strict token limits"""
        context_parts = []
        used_chunks = []
        total_tokens = 0
        
        # Reserve tokens for system prompt and question (estimate)
        reserved_tokens = 500
        available_tokens = self.available_context_tokens - reserved_tokens
        
        print(f"Building context with {available_tokens} available tokens")
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk['text']
            chunk_tokens = count_tokens(chunk_text)
            
            # Add workshop separator for readability
            workshop_id = chunk['metadata'].get('workshop_id', 'Unknown')
            separator = f"\n=== {workshop_id} Content ===\n" if not context_parts else f"\n--- {workshop_id} ---\n"
            separator_tokens = count_tokens(separator)
            
            # Check if adding this chunk would exceed limits
            if total_tokens + chunk_tokens + separator_tokens > available_tokens:
                print(f"Stopping at chunk {i}: would exceed token limit")
                break
            
            # Add the chunk
            context_parts.append(separator + chunk_text)
            used_chunks.append(chunk)
            total_tokens += chunk_tokens + separator_tokens
            
            print(f"Added chunk {i} from {workshop_id}: {chunk_tokens} tokens (total: {total_tokens})")
        
        context = "".join(context_parts)
        
        print(f"Final context: {total_tokens} tokens using {len(used_chunks)} chunks")
        
        return context, used_chunks
    
    def is_meta_question(self, question: str) -> str:
        """Determine if question is meta and what type"""
        question_lower = question.lower()
        
        for category, patterns in self.meta_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return category
        
        return "content"  # Not a meta question
    
    def answer_meta_question(self, question: str, question_type: str) -> Tuple[str, Dict]:
        """Answer meta-questions about course structure, speakers, etc."""
        
        if question_type == "speakers":
            return self._answer_speakers_question(question)
        elif question_type == "course_structure":
            return self._answer_course_structure_question(question)
        elif question_type == "specific_workshop":
            return self._answer_specific_workshop_question(question)
        else:
            return "I couldn't understand that question about the course.", {"success": False}
    
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
    
    def answer_question(self, question: str, max_workshops: int = 2, 
                       chunks_per_workshop: int = 2) -> Tuple[str, Dict]:
        """Answer a question using smart workshop routing and context management"""
        
        # First, check if this is a meta-question
        question_type = self.is_meta_question(question)
        print(f"Question type detected: {question_type}")
        
        if question_type != "content":
            # Handle meta-questions directly without content retrieval
            return self.answer_meta_question(question, question_type)
        
        # Get smart context for content questions
        context, sources, workshops_used = self.get_smart_context(
            question, max_workshops, chunks_per_workshop
        )
        
        if not context:
            return "No relevant information found in the workshop transcripts.", {}
        
        # Build system prompt
        system_prompt = f"""You are a helpful workshop assistant. Answer questions based only on the workshop transcript sections provided.

The information comes from workshops: {', '.join(workshops_used)}.
When referencing information, mention which workshop the information comes from."""
        
        # Build the user prompt
        user_prompt = f"Workshop Content:\n{context}\n\nQuestion: {question}"
        
        # Calculate final token usage
        system_tokens = count_tokens(system_prompt)
        user_tokens = count_tokens(user_prompt)
        total_prompt_tokens = system_tokens + user_tokens
        
        print(f"System prompt: {system_tokens} tokens")
        print(f"User prompt: {user_tokens} tokens") 
        print(f"Total prompt: {total_prompt_tokens} tokens")
        print(f"Model limit: {self.max_context_tokens}")
        
        if total_prompt_tokens > self.max_context_tokens * 0.8:  # Safety margin
            return f"Context too large ({total_prompt_tokens} tokens). Please ask a more specific question.", {}
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=min(1500, self.max_context_tokens - total_prompt_tokens - 100)
            )
            
            answer = response.choices[0].message.content
            
            # Context info
            context_info = {
                "workshops_used": workshops_used,
                "num_chunks": len(sources),
                "context_tokens": total_prompt_tokens,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                "model_used": self.model,
                "max_context_tokens": self.max_context_tokens,
                "success": True
            }
            
            return answer, context_info
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return error_msg, {"error": str(e), "success": False}

# Helper functions
def get_workshop_summary(workshop_id: str) -> str:
    """Get a summary of what a workshop covers"""
    if workshop_id in WORKSHOP_TOPICS:
        workshop_data = WORKSHOP_TOPICS[workshop_id]
        return f"{workshop_data['title']}: {', '.join(workshop_data['keywords'][:5])}"
    return f"Workshop {workshop_id}: Unknown"

def list_workshop_topics() -> Dict[str, str]:
    """List all workshop topics"""
    return {ws_id: data['title'] for ws_id, data in WORKSHOP_TOPICS.items()}

# Main interface functions
def smart_answer_question(question: str, model: str = "gpt-4o-mini", 
                         max_workshops: int = 2, chunks_per_workshop: int = 2) -> Tuple[str, Dict]:
    """Main function to answer questions using smart workshop routing with token management"""
    retrieval_system = SmartWorkshopRetrieval(model=model)
    return retrieval_system.answer_question(question, max_workshops, chunks_per_workshop)

def route_question(question: str, max_workshops: int = 2) -> List[str]:
    """Route a question to relevant workshops without answering it"""
    retrieval_system = SmartWorkshopRetrieval()
    return retrieval_system.route_question_to_workshops(question, max_workshops)

def test_context_limits(question: str, model: str = "gpt-4o-mini"):
    """Test function to see how much context we can fit"""
    retrieval_system = SmartWorkshopRetrieval(model=model)
    
    print(f"\nTesting context limits for: {question}")
    print("=" * 60)
    
    # Try different configurations
    configs = [
        (1, 1), (1, 2), (1, 3),
        (2, 1), (2, 2), (2, 3),
        (3, 1), (3, 2)
    ]
    
    for max_workshops, chunks_per_workshop in configs:
        try:
            context, sources, workshops = retrieval_system.get_smart_context(
                question, max_workshops, chunks_per_workshop
            )
            context_tokens = count_tokens(context)
            print(f"Config ({max_workshops}w, {chunks_per_workshop}c): {context_tokens} tokens, {len(sources)} chunks")
        except Exception as e:
            print(f"Config ({max_workshops}w, {chunks_per_workshop}c): ERROR - {e}")

if __name__ == "__main__":
    # Example usage
    print("Smart Workshop Retrieval System")
    print("=" * 50)
    
    # Show available workshops
    print("\nAvailable Workshops:")
    for ws_id, title in list_workshop_topics().items():
        print(f"  {ws_id}: {title}")
    
    # Example question routing
    test_question = "How do I evaluate the quality of my LLM outputs?"
    print(f"\nTest Question: {test_question}")
    
    # Test routing
    relevant_workshops = route_question(test_question)
    print(f"Relevant Workshops: {relevant_workshops}")
    
    # Test context limits
    test_context_limits(test_question)
    
    # Test meta-questions
    test_meta_questions()
    
    # Example answer with safe limits
    print(f"\nAnswering with safe limits...")
    answer, info = smart_answer_question(test_question)
    print(f"Answer: {answer}")
    print(f"Context Info: {info}")

def test_meta_questions():
    """Test the enhanced system with meta-questions"""
    meta_test_questions = [
        "Who gave the first workshop?",
        "What are the workshops of this course?", 
        "What are the speakers?",
        "Who taught workshop 5?",
        "What does workshop 4 cover?",
        "How many workshops are there?"
    ]
    
    print(f"\n🧪 Testing Meta Questions")
    print("=" * 50)
    
    for i, question in enumerate(meta_test_questions, 1):
        print(f"\n{i}. Testing: {question}")
        answer, info = smart_answer_question(question)
        
        if info.get('success', True):
            print(f"   ✅ Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"   📊 Type: {info.get('question_type', 'content')}")
        else:
            print(f"   ❌ Failed: {answer}")
        print("-" * 30) 