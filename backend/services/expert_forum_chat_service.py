"""
Expert Forum Chat Service.

This module integrates all chat components to provide a complete
conversation management system for the expert forum.
"""

import logging
from typing import List, Optional

from models.message import Message, MessageRole, Intent
from services.message_manager import MessageManager
from services.context_summarizer import ContextSummarizer
from services.intent_recognizer import IntentRecognizer
from services.conversation_store import ConversationContextStore

logger = logging.getLogger(__name__)


class ExpertForumChatService:
    """
    Main chat service integrating all conversation management components.
    
    Coordinates message management, context summarization, intent recognition,
    and persistence for the expert forum chat system.
    """
    
    def __init__(
        self,
        message_manager: Optional[MessageManager] = None,
        context_summarizer: Optional[ContextSummarizer] = None,
        intent_recognizer: Optional[IntentRecognizer] = None,
        context_store: Optional[ConversationContextStore] = None
    ):
        """
        Initialize chat service with all required components.
        
        Args:
            message_manager: Message management component
            context_summarizer: Context summarization component
            intent_recognizer: Intent recognition component
            context_store: Conversation persistence component
        """
        # Initialize components
        self.store = context_store or ConversationContextStore()
        self.message_manager = message_manager or MessageManager(self.store)
        self.context_summarizer = context_summarizer or ContextSummarizer()
        self.intent_recognizer = intent_recognizer or IntentRecognizer()
    
    async def add_user_message(self, content: str) -> Message:
        """
        Process and add user message.
        
        Args:
            content: User message content
            
        Returns:
            Created message
            
        Raises:
            ValueError: If content is empty
        """
        # Validate input
        if not content or not content.strip():
            raise ValueError("User message cannot be empty")
        
        # Recognize intent
        intent = self.intent_recognizer.recognize_intent(content)
        
        # Add message
        message = self.message_manager.add_message(
            role=MessageRole.USER,
            content=content,
            intent=intent
        )
        
        # Check if summarization is needed
        await self._check_and_summarize()
        
        logger.info(f"Added user message with intent: {intent.value}")
        return message
    
    async def add_news_summary(self, summary_content: str, stock_symbols: Optional[List[str]] = None) -> Message:
        """
        Add news summary to conversation.
        
        Args:
            summary_content: News summary content
            stock_symbols: Related stock symbols (optional)
            
        Returns:
            Created message
        """
        # Format content with stock symbols if provided
        if stock_symbols:
            content = f"{summary_content}\n\n相关股票: {', '.join(stock_symbols)}"
        else:
            content = summary_content
        
        # Add message
        message = self.message_manager.add_message(
            role=MessageRole.KIMI,
            content=content
        )
        
        # Check if summarization is needed
        await self._check_and_summarize()
        
        logger.info("Added news summary message")
        return message
    
    async def add_expert_response(self, expert_type: str, content: str) -> Message:
        """
        Add expert analysis to conversation.
        
        Args:
            expert_type: Type of expert (e.g., "选股分析师")
            content: Expert analysis content
            
        Returns:
            Created message
        """
        # Add message
        message = self.message_manager.add_message(
            role=MessageRole.EXPERT,
            content=content,
            expert_type=expert_type
        )
        
        # Check if summarization is needed
        await self._check_and_summarize()
        
        logger.info(f"Added expert response from {expert_type}")
        return message
    
    async def get_context_for_expert(self) -> str:
        """
        Get formatted context for expert analysis.
        
        Returns:
            Formatted context string with summary and/or messages
        """
        return self.message_manager.get_context_for_expert()
    
    async def reset_conversation(self) -> None:
        """Reset conversation state."""
        self.message_manager.clear_messages()
        logger.info("Reset conversation")
    
    async def get_conversation_history(self) -> List[Message]:
        """
        Get full conversation history for display.
        
        Returns:
            List of all messages (excluding system messages)
        """
        return self.message_manager.get_messages(include_system=False)
    
    async def _check_and_summarize(self) -> None:
        """
        Check if summarization is needed and trigger if threshold exceeded.
        """
        message_count = self.store.get_message_counter()
        
        if self.context_summarizer.should_summarize(message_count):
            logger.info(f"Message count ({message_count}) exceeded threshold, triggering summarization")
            
            # Get expert-visible messages
            messages = self.message_manager.get_messages(include_system=False)
            
            # Get messages since last summary
            active_summary = self.store.get_active_summary()
            if active_summary:
                messages_to_summarize = messages[active_summary.messages_summarized:]
            else:
                messages_to_summarize = messages
            
            # Generate summary
            summary = self.context_summarizer.summarize_conversation(messages_to_summarize)
            
            if summary:
                # Save summary
                self.store.save_summary(summary)
                
                # Reset counter
                self.store.reset_counter()
                
                logger.info("Summarization completed and counter reset")
            else:
                logger.warning("Summarization failed, continuing with full context")
    
    def get_message_count(self) -> int:
        """
        Get current message count.
        
        Returns:
            Number of messages since last summarization
        """
        return self.store.get_message_counter()
    
    def has_active_summary(self) -> bool:
        """
        Check if there is an active summary.
        
        Returns:
            True if active summary exists
        """
        return self.store.get_active_summary() is not None
