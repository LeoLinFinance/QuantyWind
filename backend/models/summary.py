"""
Summary data model for Expert Forum Chat.

This module defines the Summary class for managing conversation summaries.
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass
class Summary:
    """
    Represents a conversation summary.
    
    Attributes:
        summary_id: Unique identifier for the summary
        content: The summary text content
        created_at: When the summary was created
        messages_summarized: Number of messages that were summarized
        original_message_ids: List of message IDs that were summarized
    """
    summary_id: str = field(default_factory=lambda: f"sum_{uuid.uuid4().hex[:16]}")
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    messages_summarized: int = 0
    original_message_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """
        Convert summary to dictionary for storage.
        
        Returns:
            Dictionary representation of the summary
        """
        return {
            'summary_id': self.summary_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'messages_summarized': self.messages_summarized,
            'original_message_ids': self.original_message_ids
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Summary':
        """
        Create summary from dictionary.
        
        Args:
            data: Dictionary containing summary data
            
        Returns:
            Summary instance
        """
        return cls(
            summary_id=data['summary_id'],
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            messages_summarized=data['messages_summarized'],
            original_message_ids=data['original_message_ids']
        )
