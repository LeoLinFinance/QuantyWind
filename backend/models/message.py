"""
Message data model for Expert Forum Chat.

This module defines the Message class and related enums for managing
conversation messages in the expert forum chat system.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid


class MessageRole(Enum):
    """Enum for message sender roles."""
    SYSTEM = "system"
    KIMI = "kimi"
    EXPERT = "expert"
    USER = "user"


class Intent(Enum):
    """Enum for user message intents."""
    STOCK_RECOMMENDATION = "stock_recommendation"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    MARKET_OUTLOOK = "market_outlook"
    RISK_ASSESSMENT = "risk_assessment"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """
    Represents a single message in the conversation.
    
    Attributes:
        id: Unique identifier for the message
        role: The role of the message sender (system, kimi, expert, user)
        content: The message content
        timestamp: When the message was created
        expert_type: Type of expert (if role is EXPERT)
        intent: User intent (if role is USER)
    """
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:16]}")
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    expert_type: Optional[str] = None
    intent: Optional[Intent] = None
    
    def is_visible_to_expert(self) -> bool:
        """
        Check if message should be visible to experts.
        
        Returns:
            True if message is visible to experts (not a system message)
        """
        return self.role != MessageRole.SYSTEM
    
    def to_dict(self) -> dict:
        """
        Convert message to dictionary for storage.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            'id': self.id,
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'expert_type': self.expert_type,
            'intent': self.intent.value if self.intent else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """
        Create message from dictionary.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            Message instance
        """
        return cls(
            id=data['id'],
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            expert_type=data.get('expert_type'),
            intent=Intent(data['intent']) if data.get('intent') else None
        )
