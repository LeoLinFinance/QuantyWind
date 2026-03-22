"""
Conversation Context Store for Expert Forum Chat.

This module provides persistence layer for conversation state,
managing storage and retrieval of messages, summaries, and counters.
"""

import json
import os
import logging
from typing import List, Optional
from pathlib import Path
import time

from models.message import Message
from models.summary import Summary
from models.conversation_state import ConversationState

logger = logging.getLogger(__name__)


class ConversationContextStore:
    """
    Manages persistence of conversation state to JSON storage.
    
    Handles saving and loading messages, summaries, and conversation state
    with retry logic for resilience.
    """
    
    def __init__(self, storage_path: str = "data/conversations/conversation_state.json"):
        """
        Initialize the conversation store.
        
        Args:
            storage_path: Path to the JSON storage file
        """
        self.storage_path = storage_path
        self.state = ConversationState()
        self._ensure_storage_directory()
        self._load_state()
    
    def _ensure_storage_directory(self):
        """Create storage directory if it doesn't exist."""
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir:
            Path(storage_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self):
        """Load conversation state from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.state = ConversationState.from_dict(data)
                    logger.info(f"Loaded conversation state with {len(self.state.messages)} messages")
        except Exception as e:
            logger.error(f"Failed to load conversation state: {e}")
            # Initialize with empty state on error
            self.state = ConversationState()
    
    def _save_state(self, retry_count: int = 3):
        """
        Save conversation state to storage with retry logic.
        
        Args:
            retry_count: Number of retry attempts on failure
        """
        for attempt in range(retry_count):
            try:
                # Create backup of existing file
                if os.path.exists(self.storage_path):
                    backup_path = f"{self.storage_path}.backup"
                    with open(self.storage_path, 'r', encoding='utf-8') as f:
                        backup_data = f.read()
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(backup_data)
                
                # Write new state
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
                
                logger.debug(f"Saved conversation state with {len(self.state.messages)} messages")
                return
                
            except Exception as e:
                logger.warning(f"Save attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to save conversation state after {retry_count} attempts")
                    raise
    
    def save_message(self, message: Message) -> None:
        """
        Persist message to storage.
        
        Args:
            message: Message to save
        """
        self.state.messages.append(message)
        self.state.last_updated = message.timestamp
        self._save_state()
    
    def load_messages(self) -> List[Message]:
        """
        Load all messages from storage.
        
        Returns:
            List of all messages
        """
        return self.state.messages
    
    def save_summary(self, summary: Summary) -> None:
        """
        Save conversation summary.
        
        Args:
            summary: Summary to save
        """
        self.state.active_summary = summary
        self.state.last_updated = summary.created_at
        self._save_state()
    
    def get_active_summary(self) -> Optional[Summary]:
        """
        Get current active summary if exists.
        
        Returns:
            Active summary or None
        """
        return self.state.active_summary
    
    def get_message_counter(self) -> int:
        """
        Get current message count.
        
        Returns:
            Current message counter value
        """
        return self.state.message_counter
    
    def increment_counter(self) -> None:
        """Increment message counter by one."""
        self.state.message_counter += 1
        self._save_state()
    
    def reset_counter(self) -> None:
        """Reset message counter to zero."""
        self.state.message_counter = 0
        self._save_state()
    
    def clear_all(self) -> None:
        """Clear all conversation data."""
        self.state = ConversationState()
        self._save_state()
        logger.info("Cleared all conversation data")
    
    def get_state(self) -> ConversationState:
        """
        Get current conversation state.
        
        Returns:
            Current conversation state
        """
        return self.state
