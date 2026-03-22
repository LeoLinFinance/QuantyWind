"""
Conversation State data model for Expert Forum Chat.

This module defines the ConversationState class for managing the overall
conversation state including messages, summaries, and counters.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from models.message import Message, MessageRole
from models.summary import Summary


@dataclass
class ConversationState:
    """
    Represents the complete state of a conversation.
    
    Attributes:
        messages: List of all messages in the conversation
        active_summary: Current active summary (if any)
        message_counter: Count of messages since last summarization
        last_updated: Timestamp of last update
    """
    messages: List[Message] = field(default_factory=list)
    active_summary: Optional[Summary] = None
    message_counter: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_expert_visible_messages(self) -> List[Message]:
        """
        Get messages visible to experts (excludes system messages).
        
        Returns:
            List of messages visible to experts
        """
        return [msg for msg in self.messages if msg.is_visible_to_expert()]
    
    def get_context_string(self) -> str:
        """
        Format context as string for expert analysis.
        
        Returns:
            Formatted context string with role labels
        """
        if self.active_summary:
            # Include summary + new messages
            context_parts = [f"[对话总结]\n{self.active_summary.content}\n"]
            new_messages = self.messages[self.active_summary.messages_summarized:]
            for msg in new_messages:
                if msg.is_visible_to_expert():
                    role_label = self._get_role_label(msg)
                    context_parts.append(f"[{role_label}] {msg.content}")
            return "\n\n".join(context_parts)
        else:
            # Return full history
            context_parts = []
            for msg in self.get_expert_visible_messages():
                role_label = self._get_role_label(msg)
                context_parts.append(f"[{role_label}] {msg.content}")
            return "\n\n".join(context_parts)
    
    def _get_role_label(self, msg: Message) -> str:
        """
        Get display label for message role.
        
        Args:
            msg: Message to get label for
            
        Returns:
            Display label string
        """
        if msg.role == MessageRole.KIMI:
            return "KimiClaw资讯"
        elif msg.role == MessageRole.EXPERT:
            return msg.expert_type or "专家"
        elif msg.role == MessageRole.USER:
            return "用户"
        else:
            return "系统"
    
    def to_dict(self) -> dict:
        """
        Convert conversation state to dictionary for storage.
        
        Returns:
            Dictionary representation of the conversation state
        """
        return {
            'messages': [msg.to_dict() for msg in self.messages],
            'active_summary': self.active_summary.to_dict() if self.active_summary else None,
            'message_counter': self.message_counter,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationState':
        """
        Create conversation state from dictionary.
        
        Args:
            data: Dictionary containing conversation state data
            
        Returns:
            ConversationState instance
        """
        return cls(
            messages=[Message.from_dict(msg_data) for msg_data in data.get('messages', [])],
            active_summary=Summary.from_dict(data['active_summary']) if data.get('active_summary') else None,
            message_counter=data.get('message_counter', 0),
            last_updated=datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else datetime.now()
        )
