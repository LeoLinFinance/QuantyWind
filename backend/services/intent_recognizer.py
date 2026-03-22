"""
Intent Recognizer for Expert Forum Chat.

This module analyzes user input to identify intent using keyword matching.
"""

import logging
from typing import Dict, List

from models.message import Intent

logger = logging.getLogger(__name__)


class IntentRecognizer:
    """
    Analyzes user input to identify intent.
    
    Uses keyword-based matching to classify user messages into
    predefined intent categories.
    """
    
    def __init__(self):
        """Initialize intent recognizer with keyword mappings."""
        self.intent_keywords = self._initialize_keywords()
    
    def _initialize_keywords(self) -> Dict[Intent, List[str]]:
        """
        Initialize keyword mappings for each intent type.
        
        Returns:
            Dictionary mapping intents to keyword lists
        """
        return {
            Intent.STOCK_RECOMMENDATION: [
                "推荐", "买什么", "买入", "选股", "股票推荐", "哪只股票",
                "什么股", "好股", "潜力股", "牛股", "黑马"
            ],
            Intent.PORTFOLIO_ANALYSIS: [
                "持仓", "组合", "我的股票", "仓位", "配置", "资产",
                "投资组合", "持有", "分析我的"
            ],
            Intent.MARKET_OUTLOOK: [
                "市场", "大盘", "行情", "走势", "趋势", "展望", "预测",
                "后市", "未来", "看法", "观点", "怎么看"
            ],
            Intent.RISK_ASSESSMENT: [
                "风险", "危险", "安全", "止损", "回撤", "波动", "风控",
                "注意", "小心", "警惕"
            ],
            Intent.GENERAL_QUESTION: [
                "什么", "为什么", "怎么", "如何", "能否", "可以",
                "请问", "想问", "了解"
            ]
        }
    
    def recognize_intent(self, user_message: str) -> Intent:
        """
        Analyze user message and identify intent.
        
        Args:
            user_message: User's message text
            
        Returns:
            Identified intent
        """
        try:
            message_lower = user_message.lower().strip()
            
            # Check each intent's keywords
            for intent, keywords in self.intent_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        logger.debug(f"Recognized intent {intent.value} from keyword '{keyword}'")
                        return intent
            
            # Default to general question if no specific intent found
            logger.debug(f"No specific intent found, defaulting to GENERAL_QUESTION")
            return Intent.GENERAL_QUESTION
            
        except Exception as e:
            logger.warning(f"Intent recognition failed: {e}")
            return Intent.UNKNOWN
    
    def get_intent_keywords(self) -> Dict[str, List[str]]:
        """
        Get keyword mappings for each intent type.
        
        Returns:
            Dictionary mapping intent names to keyword lists
        """
        return {intent.value: keywords for intent, keywords in self.intent_keywords.items()}
