"""
Workshop Bot Integration Example
This shows how to integrate the smart workshop retrieval system into your Discord bot or any application.
"""

from smart_workshop_retrieval import smart_answer_question, route_question
from multi_workshop_vector import get_collection_status, process_all_workshops

class WorkshopBot:
    """Example bot class that uses the smart workshop retrieval system"""
    
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.ensure_workshops_loaded()
    
    def ensure_workshops_loaded(self):
        """Ensure all workshops are processed and available"""
        status = get_collection_status()
        if not status or status.get('total_chunks', 0) == 0:
            print("🔄 Loading workshops for the first time...")
            processed = process_all_workshops()
            print(f"✅ Loaded {len(processed)} workshops")
        else:
            print(f"✅ {status['total_chunks']} workshop chunks ready")
    
    def answer_question(self, question: str, user_id: str = None) -> dict:
        """
        Answer a question about the workshops
        Returns a dict with answer, metadata, and success status
        """
        try:
            # Log the question (optional)
            if user_id:
                print(f"Question from {user_id}: {question}")
            
            # Use smart retrieval system
            answer, context_info = smart_answer_question(
                question=question,
                model=self.model,
                max_workshops=2,  # Limit to 2 most relevant workshops
                chunks_per_workshop=2  # 2 chunks per workshop max
            )
            
            # Return structured response
            return {
                "success": context_info.get('success', True),
                "answer": answer,
                "workshops_used": context_info.get('workshops_used', []),
                "context_tokens": context_info.get('context_tokens', 0),
                "model_used": context_info.get('model_used', self.model),
                "num_chunks": context_info.get('num_chunks', 0),
                "error": context_info.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "error": str(e)
            }
    
    def preview_routing(self, question: str) -> dict:
        """Preview which workshops would be used for a question"""
        try:
            workshops = route_question(question, max_workshops=3)
            return {
                "question": question,
                "relevant_workshops": workshops,
                "success": True
            }
        except Exception as e:
            return {
                "question": question,
                "error": str(e),
                "success": False
            }

# Simple function-based interface (for easy integration)
def answer_workshop_question(question: str, model: str = "gpt-4o-mini") -> str:
    """
    Simple function to answer workshop questions
    Returns just the answer text (for easy integration)
    """
    try:
        answer, context_info = smart_answer_question(question, model=model)
        if context_info.get('success', True):
            return answer
        else:
            return f"I couldn't find relevant information about that topic. Please try asking a more specific question about the workshops."
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Example usage patterns
def example_usage():
    """Show different ways to use the system"""
    
    print("🤖 Workshop Bot Integration Examples")
    print("=" * 50)
    
    # Method 1: Using the bot class
    print("\n1. Using Bot Class:")
    bot = WorkshopBot()
    
    result = bot.answer_question("What is prompt engineering?", user_id="user123")
    if result['success']:
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Used workshops: {result['workshops_used']}")
        print(f"Tokens: {result['context_tokens']}")
    else:
        print(f"Error: {result['answer']}")
    
    # Method 2: Using simple function
    print("\n2. Using Simple Function:")
    answer = answer_workshop_question("How do I evaluate LLM outputs?")
    print(f"Answer: {answer[:200]}...")
    
    # Method 3: Preview routing
    print("\n3. Preview Workshop Routing:")
    routing = bot.preview_routing("How do I debug hallucinations in production?")
    print(f"Question would route to: {routing['relevant_workshops']}")

# Discord bot integration example
async def discord_bot_command(ctx, *, question):
    """
    Example Discord bot command handler
    Usage: !ask How do I evaluate my LLM outputs?
    """
    # Use the simple function for Discord
    answer = answer_workshop_question(question)
    
    # Discord has a 2000 character limit
    if len(answer) > 1900:
        answer = answer[:1900] + "..."
    
    await ctx.send(f"**Question:** {question}\n\n**Answer:** {answer}")

# FastAPI integration example
def fastapi_endpoint_example():
    """Example FastAPI endpoint"""
    from fastapi import FastAPI
    from pydantic import BaseModel
    
    app = FastAPI()
    bot = WorkshopBot()
    
    class QuestionRequest(BaseModel):
        question: str
        user_id: str = None
    
    @app.post("/ask")
    async def ask_question(request: QuestionRequest):
        result = bot.answer_question(request.question, request.user_id)
        return result
    
    return app

if __name__ == "__main__":
    example_usage() 