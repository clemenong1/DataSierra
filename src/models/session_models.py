"""
Session-related data models
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class ConversationMessage:
    """Conversation message"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    total_messages: int
    user_messages: int
    assistant_messages: int
    last_message_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'total_messages': self.total_messages,
            'user_messages': self.user_messages,
            'assistant_messages': self.assistant_messages,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
