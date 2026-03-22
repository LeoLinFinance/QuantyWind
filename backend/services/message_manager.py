"""
Message Manager for Expert Forum Chat.

This module manages message lifecycle, storage, and retrieval with
visibility filtering and context formatting.
"""

import logging
from typing import List, Optional
from datetime import datetime

from models.message import Message, MessageRole, Intent
from services.conversation_store import ConversationContextStore

logger = logging.getLogger(__name__)


class MessageManager:
    """
    Manages message lifecycle, storage, and retrieval.
    
    Handles message creation, validation, filtering, and context formatting
    for expert analysis.
    """
    
    def __init__(self, store: ConversationContextStore):
        """
        Initialize message manager.
        
        Args:
            store: Conversation context store for persistence
        """
        self.store = store
    
    def add_message(
        self,
        role: MessageRole,
        content: str,
        expert_type: Optional[str] = None,
        intent: Optional[Intent] = None
    ) -> Message:
        """
        Add a new message to the conversation.
        
        Args:
            role: Role of the message sender
            content: Message content
            expert_type: Type of expert (if role is EXPERT)
            intent: User intent (if role is USER)
            
        Returns:
            Created message
            
        Raises:
            ValueError: If message validation fails
        """
        # Validate content
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")
        
        # Validate expert type for expert messages
        if role == MessageRole.EXPERT and not expert_type:
            raise ValueError("Expert messages must include expert_type")
        
        # Create message
        message = Message(
            role=role,
            content=content.strip(),
            timestamp=datetime.now(),
            expert_type=expert_type,
            intent=intent
        )
        
        # Save to store
        self.store.save_message(message)
        
        # Increment counter for non-system messages
        if message.is_visible_to_expert():
            self.store.increment_counter()
        
        logger.info(f"Added {role.value} message: {message.id}")
        return message
    
    def get_messages(
        self,
        include_system: bool = False,
        since_timestamp: Optional[datetime] = None
    ) -> List[Message]:
        """
        Retrieve messages with optional filtering.
        
        Args:
            include_system: Whether to include system messages
            since_timestamp: Only return messages after this timestamp
            
        Returns:
            List of filtered messages in chronological order
        """
        messages = self.store.load_messages()
        
        # Filter by visibility
        if not include_system:
            messages = [msg for msg in messages if msg.is_visible_to_expert()]
        
        # Filter by timestamp
        if since_timestamp:
            messages = [msg for msg in messages if msg.timestamp > since_timestamp]
        
        # Sort by timestamp (should already be sorted, but ensure it)
        messages.sort(key=lambda m: m.timestamp)
        
        return messages
    
    def get_message_count(self, visible_only: bool = True) -> int:
        """
        Get count of messages.
        
        Args:
            visible_only: If True, only count expert-visible messages
            
        Returns:
            Message count
        """
        if visible_only:
            return len([msg for msg in self.store.load_messages() if msg.is_visible_to_expert()])
        return len(self.store.load_messages())
    
    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        self.store.clear_all()
        logger.info("Cleared all messages")
    
    def get_context_for_expert(self) -> str:
        """
        Get formatted context string for expert analysis.
        
        Returns:
            Formatted context with role labels and visibility filtering applied
        """
        state = self.store.get_state()
        return state.get_context_string()
