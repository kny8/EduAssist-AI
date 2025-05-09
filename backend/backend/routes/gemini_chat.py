from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from google import genai
import random

from database.database import get_db
from utils.auth import get_current_user

# Set up Google API key - ensure this is set in your environment variables
GOOGLE_API_KEY =  "AIzaSyC778ZovoyzU79mA0BWSDUrw6KA3B-Mhx4"

router = APIRouter()

# Fallback responses in case the API has issues
FALLBACK_RESPONSES: Dict[str, List[str]] = {
    "general": [
        "I'm a helpful assistant for your software engineering course. How can I help you today?",
        "I can provide information about software engineering concepts. What would you like to know?",
        "I'm here to assist with your software engineering questions. Please let me know what you're curious about."
    ],
    "wireframe": [
        "Wireframes are simplified visual representations of your interface design. Focus on layout and structure rather than visual design. Use simple shapes, consistent elements, and include navigation patterns.",
        "When creating wireframes, remember to keep them simple and focus on functionality first. They should represent the skeletal framework of your interface."
    ],
    "software_engineering": [
        "Software engineering involves designing, developing, testing, and maintaining software systems using engineering principles. Key aspects include requirements analysis, system design, coding standards, testing methodologies, and project management.",
        "Software engineering combines engineering principles with software development practices to build reliable, scalable, and maintainable systems."
    ],
    "testing": [
        "Software testing is crucial for quality assurance. Common types include unit testing, integration testing, system testing, and acceptance testing.",
        "Effective testing strategies include test-driven development (TDD), continuous integration, and automated testing frameworks."
    ],
    "design_patterns": [
        "Design patterns are reusable solutions to common software design problems. They include creational patterns (like Factory and Singleton), structural patterns (like Adapter and Decorator), and behavioral patterns (like Observer and Strategy).",
        "Learning design patterns helps you write more maintainable and flexible code by applying proven solutions to common design challenges."
    ],
    "agile": [
        "Agile methodologies focus on iterative development, collaboration, and responding to change. Popular frameworks include Scrum and Kanban.",
        "Agile practices emphasize delivering working software frequently, close collaboration with stakeholders, and the ability to adapt to changing requirements."
    ]
}


class GeminiChatRequest(BaseModel):
    message: str
    context: Optional[str] = "general"


class GeminiChatResponse(BaseModel):
    response: str
    is_fallback: bool = False


@router.post("/gemini", response_model=GeminiChatResponse)
async def chat_with_gemini(
        request: GeminiChatRequest,
        currentUser=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Process a chat request to the Gemini API and return a response.
    This is a simplified version for the dashboard mini-chat.
    """
    # Validate inputs
    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Attempt to use the Gemini API
        if not GOOGLE_API_KEY:
            # Fall back to a predefined response if API key is missing
            return get_fallback_response(request.message, "API key missing")

        try:
            # Create a client with the API key
            client = genai.Client(api_key=GOOGLE_API_KEY)
            
            # Build system prompt based on context
            system_prompt = "You are Gemini, a helpful AI assistant for a software engineering course. "

            if request.context == "dashboard_quick_chat":
                system_prompt += "You are providing quick, concise answers on the student's dashboard. Keep responses brief and focused on software engineering concepts. If a question requires detailed explanation, suggest using the full Study with GenAI feature."
            else:
                system_prompt += "Provide helpful, accurate information about software engineering topics."

            # Try first with gemini-1.5-pro-latest
            try:
                # Create a chat session
                chat = client.chat(model='gemini-1.5-pro-latest')
                
                # Add the system message
                chat.send_message(system_prompt)
                
                # Send the user's question and get a response
                response = chat.send_message(request.message)
                
                return {"response": response.text, "is_fallback": False}
                
            except Exception as model_error:
                print(f"Could not use gemini-1.5-pro-latest, trying gemini-pro: {str(model_error)}")
                
                # Try with gemini-pro as fallback
                try:
                    chat = client.chat(model='gemini-pro')
                    chat.send_message(system_prompt)
                    response = chat.send_message(request.message)
                    
                    return {"response": response.text, "is_fallback": False}
                except Exception as model_error2:
                    print(f"Could not use gemini-pro: {str(model_error2)}")
                    return get_fallback_response(request.message, "Model initialization failed")
            
        except Exception as client_error:
            print(f"Error with Gemini client: {str(client_error)}")
            return get_fallback_response(request.message, str(client_error))

    except Exception as e:
        print(f"Error in Gemini chat: {str(e)}")
        # Return a fallback response instead of throwing an error
        return get_fallback_response(request.message, str(e))


def get_fallback_response(message: str, error_reason: str = None):
    """Provides a fallback response when the API is not available"""
    print(f"Using fallback response due to: {error_reason}")
    
    # Log the original message for debugging
    print(f"Original user message: {message}")
    
    message_lower = message.lower()
    
    # Determine the most relevant category for the message
    if any(term in message_lower for term in ["wireframe", "ui", "interface", "sketch"]):
        category = "wireframe"
    elif any(term in message_lower for term in ["test", "testing", "debug", "quality"]):
        category = "testing"
    elif any(term in message_lower for term in ["pattern", "design pattern", "architecture"]):
        category = "design_patterns"
    elif any(term in message_lower for term in ["agile", "scrum", "sprint", "kanban"]):
        category = "agile"
    elif any(term in message_lower for term in ["software engineering", "development", "coding", "programming"]):
        category = "software_engineering"
    else:
        category = "general"
    
    # Pick a random response from the appropriate category
    responses = FALLBACK_RESPONSES.get(category, FALLBACK_RESPONSES["general"])
    selected_response = random.choice(responses)
    
    # Add a note that this is a fallback response
    if error_reason:
        note = "\n\n(Note: This is a pre-generated response while the AI service is being updated. For more detailed assistance, please try the full Study with GenAI feature.)"
        selected_response += note
    
    return {"response": selected_response, "is_fallback": True}
