"""
OpenAI client for handling API interactions
"""

from openai import OpenAI
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history and context"""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations = {}

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

        # Keep only recent messages
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]

    def get_conversation(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])

    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]


class OpenAIClient:
    """Client for OpenAI API interactions"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.conversation_memory = ConversationMemory()

        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)


    def query_openai_with_data_context(
        self, 
        question: str, 
        data_context: str, 
        session_id: str = "default",
        include_conversation: bool = True
    ) -> Dict[str, Any]:
        """Query OpenAI with data context"""
        try:
            # Build messages
            messages = []

            # Add system message
            system_message = """You are a data analysis expert. Analyze the provided data and answer the user's question with insights, patterns, and actionable recommendations. Be specific and data-driven in your response."""
            messages.append({"role": "system", "content": system_message})

            # Add conversation history if requested
            if include_conversation:
                conversation = self.conversation_memory.get_conversation(session_id)
                messages.extend(conversation)

            # Add current question with data context
            user_message = f"Data Context:\n{data_context}\n\nQuestion: {question}"
            messages.append({"role": "user", "content": user_message})

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )

            answer = response.choices[0].message.content

            # Store conversation
            self.conversation_memory.add_message(session_id, "user", user_message)
            self.conversation_memory.add_message(session_id, "assistant", answer)

            return {
                "success": True,
                "answer": answer,
                "tokens_used": response.usage.total_tokens,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "answer": "Sorry, I encountered an error while processing your request."
            }

    def generate_insights(self, data_summary: str) -> Dict[str, Any]:
        """Generate general insights from data summary"""
        try:
            prompt = f"""Based on the following data summary, provide key insights and recommendations:

{data_summary}

Please provide:
1. Key patterns and trends
2. Data quality observations
3. Business insights
4. Recommended next steps for analysis"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )

            return {
                "success": True,
                "insights": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "insights": "Unable to generate insights at this time."
            }
