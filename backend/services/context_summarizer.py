"""
Context Summarizer for Expert Forum Chat.

This module generates conversation summaries using StepFun API (阶跃星辰8k).
"""

import logging
import os
from typing import List, Optional
from openai import OpenAI

from models.message import Message
from models.summary import Summary

logger = logging.getLogger(__name__)


class ContextSummarizer:
    """
    Generates conversation summaries using StepFun API.
    
    Monitors message count and triggers summarization when threshold
    is exceeded, using the 阶跃星辰8k model.
    """
    
    SUMMARIZATION_THRESHOLD = 10
    DEFAULT_MODEL = "step-1-8k"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize context summarizer with StepFun API credentials.
        
        Args:
            api_key: StepFun API key (defaults to dedicated key for conversation summary)
            base_url: StepFun API base URL (defaults to STEPFUN_BASE_URL env var)
        """
        # 使用对话总结专用API Key（与资讯总结共用）
        self.api_key = api_key or "4oZN16sWiAKwBEQvnb6nxr0mX31kJ1MsDqZBiuzly1UOPsXaDHgFKyo7QNSfvaC4"
        self.base_url = base_url or os.getenv("STEPFUN_BASE_URL", "https://api.stepfun.com/v1")
        
        if not self.api_key:
            logger.warning("StepFun API key not configured, summarization will be disabled")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key, 
                base_url=self.base_url,
                timeout=60.0  # 设置60秒HTTP超时
            )
            logger.info("✅ Context Summarizer initialized with dedicated API key")
        
        self.custom_prompt = None
    
    def should_summarize(self, message_count: int) -> bool:
        """
        Check if summarization threshold is reached.
        
        Args:
            message_count: Current message count
            
        Returns:
            True if summarization should be triggered
        """
        return message_count > self.SUMMARIZATION_THRESHOLD
    
    def get_default_prompt(self) -> str:
        """
        Get default summarization prompt.
        
        Returns:
            Default prompt emphasizing key information preservation
        """
        return """你是一位专业的对话总结助手。请总结以下智者论坛的对话内容，保留关键信息：

1. 重要的市场资讯和舆情分析
2. 各位专家的核心观点和建议
3. 用户提出的问题和需求
4. 关键的投资决策和风险提示

请用简洁的语言总结，确保后续专家能够基于这个总结继续提供有价值的分析。
总结应该是连贯的叙述，而不是简单的列表。"""
    
    def update_prompt(self, new_prompt: str) -> None:
        """
        Update summarization prompt.
        
        Args:
            new_prompt: New custom prompt to use
        """
        self.custom_prompt = new_prompt
        logger.info("Updated summarization prompt")
    
    def summarize_conversation(
        self,
        messages: List[Message],
        custom_prompt: Optional[str] = None
    ) -> Optional[Summary]:
        """
        Generate conversation summary using StepFun API.
        
        Args:
            messages: List of messages to summarize
            custom_prompt: Optional custom prompt (overrides stored custom_prompt)
            
        Returns:
            Summary object or None if summarization fails
        """
        if not self.client:
            logger.error("StepFun API client not initialized, cannot summarize")
            return None
        
        if not messages:
            logger.warning("No messages to summarize")
            return None
        
        try:
            # Format messages for summarization
            conversation_text = self._format_messages_for_summary(messages)
            
            # Get prompt
            prompt = custom_prompt or self.custom_prompt or self.get_default_prompt()
            
            # Call StepFun API
            response = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请总结以下对话：\n\n{conversation_text}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            summary_content = response.choices[0].message.content.strip()
            
            if not summary_content:
                logger.error("Received empty summary from API")
                return None
            
            # Create summary object
            summary = Summary(
                content=summary_content,
                messages_summarized=len(messages),
                original_message_ids=[msg.id for msg in messages]
            )
            
            logger.info(f"Generated summary for {len(messages)} messages")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None
    
    def _format_messages_for_summary(self, messages: List[Message]) -> str:
        """
        Format messages into text for summarization.
        
        Args:
            messages: List of messages to format
            
        Returns:
            Formatted conversation text
        """
        formatted_lines = []
        for msg in messages:
            if msg.is_visible_to_expert():
                role_label = self._get_role_label(msg)
                formatted_lines.append(f"[{role_label}] {msg.content}")
        
        return "\n\n".join(formatted_lines)
    
    def _get_role_label(self, msg: Message) -> str:
        """Get display label for message role."""
        from models.message import MessageRole
        
        if msg.role == MessageRole.KIMI:
            return "KimiClaw资讯"
        elif msg.role == MessageRole.EXPERT:
            return msg.expert_type or "专家"
        elif msg.role == MessageRole.USER:
            return "用户"
        else:
            return "系统"
