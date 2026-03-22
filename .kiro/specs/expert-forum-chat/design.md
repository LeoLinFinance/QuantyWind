# Design Document: Expert Forum Chat

## Overview

The Expert Forum Chat feature extends the existing expert forum system with intelligent conversation management capabilities. The design introduces a message-based architecture with automatic context summarization to maintain conversation quality while managing token limits. The system uses the 阶跃星辰8k (StepFun) model for conversation summarization and integrates seamlessly with existing news summary and expert analysis services.

The core innovation is the automatic context management system that monitors message count and triggers summarization when conversations exceed 10 messages, ensuring that expert responses remain contextual and efficient without unbounded context growth.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Expert Forum Chat System                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Message    │    │   Context    │    │   Intent     │  │
│  │   Manager    │───▶│ Summarizer   │    │ Recognizer   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Conversation Context Store                  │  │
│  │  - Messages (chronological)                           │  │
│  │  - Summary state                                      │  │
│  │  - Message counter                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    News      │  │   Expert     │  │    User      │
│   Summary    │  │   Analysis   │  │   Input      │
│   Service    │  │   Service    │  │   Handler    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow

1. **Message Addition Flow**:
   - User/System/Expert adds message → Message Manager validates → Store message → Increment counter → Check threshold → Trigger summarization if needed

2. **Context Retrieval Flow**:
   - Expert requests context → Check if summarized → Return summary + new messages OR full history → Apply visibility filter → Format for expert

3. **Summarization Flow**:
   - Counter reaches 10 → Collect expert-visible messages → Call StepFun API → Generate summary → Replace context → Reset counter

## Components and Interfaces

### 1. Message Manager

**Responsibility**: Manages message lifecycle, storage, and retrieval.

**Interface**:
```python
class MessageManager:
    def add_message(
        self,
        role: MessageRole,
        content: str,
        expert_type: Optional[str] = None,
        intent: Optional[str] = None
    ) -> Message:
        """Add a new message to the conversation"""
        
    def get_messages(
        self,
        include_system: bool = False,
        since_timestamp: Optional[str] = None
    ) -> List[Message]:
        """Retrieve messages with optional filtering"""
        
    def get_message_count(self, visible_only: bool = True) -> int:
        """Get count of messages (optionally excluding system messages)"""
        
    def clear_messages(self) -> None:
        """Clear all messages from the conversation"""
        
    def get_context_for_expert(self) -> str:
        """Get formatted context string for expert analysis"""
```

**Key Methods**:
- `add_message()`: Validates and stores messages with metadata
- `get_messages()`: Retrieves messages with filtering options
- `get_message_count()`: Counts messages for threshold detection
- `get_context_for_expert()`: Formats context with visibility rules applied

### 2. Context Summarizer

**Responsibility**: Generates conversation summaries using StepFun API.

**Interface**:
```python
class ContextSummarizer:
    def __init__(self, api_key: str, base_url: str):
        """Initialize with StepFun API credentials"""
        
    def should_summarize(self, message_count: int) -> bool:
        """Check if summarization threshold is reached"""
        
    def summarize_conversation(
        self,
        messages: List[Message],
        custom_prompt: Optional[str] = None
    ) -> SummaryResult:
        """Generate conversation summary using StepFun API"""
        
    def get_default_prompt(self) -> str:
        """Get default summarization prompt"""
        
    def update_prompt(self, new_prompt: str) -> None:
        """Update summarization prompt"""
```

**Key Methods**:
- `should_summarize()`: Checks if message count exceeds threshold (10)
- `summarize_conversation()`: Calls StepFun API to generate summary
- `get_default_prompt()`: Returns default prompt emphasizing key information preservation

**Summarization Prompt**:
```
你是一位专业的对话总结助手。请总结以下智者论坛的对话内容，保留关键信息：

1. 重要的市场资讯和舆情分析
2. 各位专家的核心观点和建议
3. 用户提出的问题和需求
4. 关键的投资决策和风险提示

请用简洁的语言总结，确保后续专家能够基于这个总结继续提供有价值的分析。
总结应该是连贯的叙述，而不是简单的列表。
```

### 3. Intent Recognizer

**Responsibility**: Analyzes user input to identify intent.

**Interface**:
```python
class IntentRecognizer:
    def recognize_intent(self, user_message: str) -> Intent:
        """Analyze user message and identify intent"""
        
    def get_intent_keywords(self) -> Dict[str, List[str]]:
        """Get keyword mappings for each intent type"""
```

**Intent Types**:
- `STOCK_RECOMMENDATION`: User asks for stock picks
- `PORTFOLIO_ANALYSIS`: User asks about current holdings
- `MARKET_OUTLOOK`: User asks about market trends
- `RISK_ASSESSMENT`: User asks about risks
- `GENERAL_QUESTION`: General inquiry
- `UNKNOWN`: Cannot determine intent

**Recognition Strategy**:
- Keyword matching for common patterns
- Context-aware analysis using simple heuristics
- Fallback to GENERAL_QUESTION for ambiguous cases

### 4. Conversation Context Store

**Responsibility**: Persists conversation state and manages context lifecycle.

**Interface**:
```python
class ConversationContextStore:
    def save_message(self, message: Message) -> None:
        """Persist message to storage"""
        
    def load_messages(self) -> List[Message]:
        """Load all messages from storage"""
        
    def save_summary(self, summary: Summary) -> None:
        """Save conversation summary"""
        
    def get_active_summary(self) -> Optional[Summary]:
        """Get current active summary if exists"""
        
    def get_message_counter(self) -> int:
        """Get current message count"""
        
    def reset_counter(self) -> None:
        """Reset message counter to zero"""
        
    def clear_all(self) -> None:
        """Clear all conversation data"""
```

**Storage Format** (JSON):
```json
{
  "messages": [
    {
      "id": "msg_1234567890",
      "role": "user",
      "content": "请分析一下当前市场",
      "timestamp": "2024-01-15T10:30:00Z",
      "intent": "MARKET_OUTLOOK"
    },
    {
      "id": "msg_1234567891",
      "role": "expert",
      "expert_type": "首席经济学家",
      "content": "当前市场...",
      "timestamp": "2024-01-15T10:30:15Z"
    }
  ],
  "summary": {
    "content": "对话总结内容...",
    "created_at": "2024-01-15T10:35:00Z",
    "messages_summarized": 10,
    "summary_id": "sum_1234567892"
  },
  "message_counter": 3,
  "last_updated": "2024-01-15T10:40:00Z"
}
```

### 5. Chat Service Integration

**Responsibility**: Integrates chat functionality with existing expert forum service.

**Interface**:
```python
class ExpertForumChatService:
    def __init__(
        self,
        message_manager: MessageManager,
        context_summarizer: ContextSummarizer,
        intent_recognizer: IntentRecognizer,
        context_store: ConversationContextStore
    ):
        """Initialize with all required components"""
        
    async def add_user_message(self, content: str) -> Message:
        """Process and add user message"""
        
    async def add_news_summary(self, summary_content: str) -> Message:
        """Add news summary to conversation"""
        
    async def add_expert_response(
        self,
        expert_type: str,
        content: str
    ) -> Message:
        """Add expert analysis to conversation"""
        
    async def get_context_for_expert(self) -> str:
        """Get formatted context for expert analysis"""
        
    async def reset_conversation(self) -> None:
        """Reset conversation state"""
        
    async def get_conversation_history(self) -> List[Message]:
        """Get full conversation history for display"""
```

## Data Models

### Message Model

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class MessageRole(Enum):
    SYSTEM = "system"
    KIMI = "kimi"
    EXPERT = "expert"
    USER = "user"

class Intent(Enum):
    STOCK_RECOMMENDATION = "stock_recommendation"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    MARKET_OUTLOOK = "market_outlook"
    RISK_ASSESSMENT = "risk_assessment"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"

@dataclass
class Message:
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    expert_type: Optional[str] = None
    intent: Optional[Intent] = None
    
    def is_visible_to_expert(self) -> bool:
        """Check if message should be visible to experts"""
        return self.role != MessageRole.SYSTEM
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
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
        """Create from dictionary"""
        return cls(
            id=data['id'],
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            expert_type=data.get('expert_type'),
            intent=Intent(data['intent']) if data.get('intent') else None
        )
```

### Summary Model

```python
@dataclass
class Summary:
    summary_id: str
    content: str
    created_at: datetime
    messages_summarized: int
    original_message_ids: List[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'summary_id': self.summary_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'messages_summarized': self.messages_summarized,
            'original_message_ids': self.original_message_ids
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Summary':
        """Create from dictionary"""
        return cls(
            summary_id=data['summary_id'],
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            messages_summarized=data['messages_summarized'],
            original_message_ids=data['original_message_ids']
        )
```

### Conversation State Model

```python
@dataclass
class ConversationState:
    messages: List[Message]
    active_summary: Optional[Summary]
    message_counter: int
    last_updated: datetime
    
    def get_expert_visible_messages(self) -> List[Message]:
        """Get messages visible to experts"""
        return [msg for msg in self.messages if msg.is_visible_to_expert()]
    
    def get_context_string(self) -> str:
        """Format context as string for expert analysis"""
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
        """Get display label for message role"""
        if msg.role == MessageRole.KIMI:
            return "KimiClaw资讯"
        elif msg.role == MessageRole.EXPERT:
            return msg.expert_type or "专家"
        elif msg.role == MessageRole.USER:
            return "用户"
        else:
            return "系统"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Message Creation Completeness
*For any* message created by the system, the message SHALL have a unique identifier, timestamp, role type, and non-empty content.
**Validates: Requirements 1.1**

### Property 2: Message Persistence Round-Trip
*For any* message stored in the Chat_Message_Store, retrieving the message SHALL return all original metadata including sender role, expert type (if applicable), timestamp, and content unchanged.
**Validates: Requirements 1.2, 11.2**

### Property 3: Chronological Message Ordering
*For any* set of messages added to the conversation in any order, retrieving the messages SHALL return them sorted by timestamp in ascending chronological order.
**Validates: Requirements 1.3**

### Property 4: Expert Message Metadata
*For any* message with role "expert", the message SHALL include a non-empty expert_type identifier.
**Validates: Requirements 1.5, 8.2**

### Property 5: Message Visibility Filtering
*For any* set of messages in the conversation, when constructing context for experts, only messages with roles "kimi", "expert", or "user" SHALL be included, and all messages with role "system" SHALL be excluded.
**Validates: Requirements 2.1, 2.3**

### Property 6: Message Counter Increment
*For any* message added to the conversation (excluding system messages), the message counter SHALL increase by exactly one.
**Validates: Requirements 3.1**

### Property 7: Visible Message Counting
*For any* conversation state, the message count SHALL equal the number of messages visible to experts (excluding system messages).
**Validates: Requirements 3.2**

### Property 8: Summarization Trigger
*For any* conversation where the visible message count exceeds 10, the Context_Summarizer SHALL be triggered to generate a summary.
**Validates: Requirements 3.4**

### Property 9: Counter Reset After Summarization
*For any* conversation, after summarization completes successfully, the message counter SHALL be reset to zero.
**Validates: Requirements 3.5**

### Property 10: Summary Input Completeness
*For any* summarization request, the input to the Context_Summarizer SHALL include all and only expert-visible messages (messages with roles kimi, expert, user).
**Validates: Requirements 4.2**

### Property 11: Summary Output Non-Empty
*For any* successful summarization, the Context_Summarizer SHALL return a non-empty summary text string.
**Validates: Requirements 4.4**

### Property 12: Context Replacement After Summarization
*For any* conversation, after a summary is generated, the conversation context SHALL contain the summary text and the summary SHALL be accessible as part of the conversation state.
**Validates: Requirements 5.1, 5.2**

### Property 13: Post-Summarization Context Composition
*For any* conversation with an active summary, when experts request context, the returned context SHALL include the summary content followed by all messages added after the summary was created.
**Validates: Requirements 5.3, 10.1**

### Property 14: Re-Summarization Trigger
*For any* conversation with an active summary, when the count of new messages added after summarization reaches 10, the system SHALL trigger re-summarization.
**Validates: Requirements 5.5**

### Property 15: User Message Intent Tagging
*For any* user message processed by the system, the message SHALL be tagged with an intent value (one of: stock_recommendation, portfolio_analysis, market_outlook, risk_assessment, general_question, or unknown).
**Validates: Requirements 6.3**

### Property 16: Intent Inclusion in Context
*For any* user message with an identified intent, when the message is included in expert context, the intent information SHALL be present in the context representation.
**Validates: Requirements 6.5**

### Property 17: News Summary Message Role
*For any* news summary added to the conversation, the message SHALL have role "kimi" and SHALL include timestamp and stock symbols metadata.
**Validates: Requirements 7.1, 7.2**

### Property 18: Recent News in Context
*For any* conversation containing news summary messages, when experts request context, the context SHALL include the most recently added news summary message.
**Validates: Requirements 7.3**

### Property 19: News Message Counting
*For any* news summary message added to the conversation, the message counter SHALL increment by one.
**Validates: Requirements 7.4**

### Property 20: Expert Response Message Role
*For any* expert analysis added to the conversation, the message SHALL have role "expert" and SHALL include the expert type identifier.
**Validates: Requirements 8.1, 8.2**

### Property 21: Expert Message Ordering
*For any* set of expert messages added to the conversation, retrieving the messages SHALL return them in the chronological order they were added.
**Validates: Requirements 8.3**

### Property 22: Expert Messages in Context
*For any* conversation containing expert messages, when experts request context, the context SHALL include all previous expert messages that are visible to experts.
**Validates: Requirements 8.4**

### Property 23: Expert Message Counting
*For any* expert message added to the conversation, the message counter SHALL increment by one.
**Validates: Requirements 8.5**

### Property 24: User Input Message Role
*For any* user input submitted to the system, the created message SHALL have role "user".
**Validates: Requirements 9.1**

### Property 25: Empty Input Rejection
*For any* user input that is empty or contains only whitespace, the system SHALL reject the input and SHALL NOT create a message.
**Validates: Requirements 9.2**

### Property 26: Context Formatting with Role Indicators
*For any* context string generated for experts, each message in the context SHALL be formatted with a clear role indicator label (e.g., "[KimiClaw资讯]", "[专家]", "[用户]").
**Validates: Requirements 10.4**

### Property 27: Immediate Message Persistence
*For any* message added to the conversation, the message SHALL be persisted to storage before the add operation completes.
**Validates: Requirements 11.1**

### Property 28: Conversation State Round-Trip
*For any* conversation state (messages, counter, summary), after saving to storage and restoring from storage, the restored state SHALL be equivalent to the original state.
**Validates: Requirements 11.2**

### Property 29: JSON Storage Format
*For any* conversation data saved to storage, the data SHALL be valid JSON and SHALL be parseable back into the conversation state structure.
**Validates: Requirements 11.5**

### Property 30: Prompt Update Persistence
*For any* custom summarization prompt configured in the system, after updating the prompt, subsequent summarization requests SHALL use the new prompt instead of the default.
**Validates: Requirements 13.5**

### Property 31: Message Display Formatting
*For any* message formatted for display, the formatted output SHALL include a role label, timestamp, and (for expert messages) the expert type name.
**Validates: Requirements 14.1, 14.2, 14.3**

### Property 32: Conversation Reset Completeness
*For any* conversation, after a reset operation, the conversation SHALL have zero messages, a message counter of zero, no active summary, and all expert configurations SHALL remain unchanged.
**Validates: Requirements 15.1, 15.2, 15.3, 15.4**

## Error Handling

### Error Scenarios and Responses

1. **Summarization API Failure**:
   - **Scenario**: StepFun API is unavailable or returns an error
   - **Response**: Log error, continue using full context without summarization, notify user of degraded functionality
   - **Recovery**: Retry on next threshold trigger

2. **Message Storage Failure**:
   - **Scenario**: File system error or permission issue when persisting messages
   - **Response**: Retry up to 3 times with exponential backoff (1s, 2s, 4s)
   - **Fallback**: If all retries fail, log critical error and continue in-memory only
   - **Recovery**: Attempt to persist on next message addition

3. **Intent Recognition Failure**:
   - **Scenario**: Intent recognizer encounters unexpected input or internal error
   - **Response**: Tag message with "unknown" intent, log warning, continue processing
   - **Impact**: Minimal - experts still receive the message content

4. **Context Retrieval Failure**:
   - **Scenario**: Error when loading messages from storage
   - **Response**: Return empty context with error indicator, log error
   - **Recovery**: Attempt reload on next context request

5. **Invalid Message Data**:
   - **Scenario**: Message missing required fields or invalid role type
   - **Response**: Reject message, return validation error to caller
   - **Prevention**: Use strong typing and validation at API boundaries

6. **Storage Corruption**:
   - **Scenario**: JSON file is corrupted or unparseable
   - **Response**: Log critical error, backup corrupted file, initialize fresh conversation state
   - **Recovery**: Manual intervention may be required to recover data

### Error Logging Strategy

All errors SHALL be logged with:
- Timestamp
- Error type and message
- Stack trace (for exceptions)
- Relevant context (message ID, conversation state, etc.)
- Severity level (WARNING, ERROR, CRITICAL)

### Graceful Degradation

The system SHALL continue operating with reduced functionality when:
- Summarization is unavailable → Use full context
- Storage is unavailable → Operate in-memory only
- Intent recognition fails → Use "unknown" intent

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Specific message creation scenarios
- API integration with StepFun
- Error handling paths
- Configuration management
- UI component behavior

**Property-Based Tests**: Verify universal properties across all inputs
- Message management properties (creation, storage, retrieval)
- Context filtering and formatting
- Counter behavior and summarization triggers
- State persistence and restoration
- All correctness properties defined above

### Property-Based Testing Configuration

**Framework**: Use `hypothesis` for Python (backend) and `fast-check` for TypeScript (frontend)

**Test Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: `Feature: expert-forum-chat, Property {number}: {property_text}`
- Custom generators for Message, ConversationState, and other domain objects

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st
import pytest

@pytest.mark.property_test
@pytest.mark.tags("Feature: expert-forum-chat, Property 1: Message Creation Completeness")
@given(
    role=st.sampled_from([MessageRole.USER, MessageRole.EXPERT, MessageRole.KIMI]),
    content=st.text(min_size=1),
    expert_type=st.one_of(st.none(), st.text(min_size=1))
)
def test_message_creation_completeness(role, content, expert_type):
    """Property 1: For any message created, it SHALL have required fields"""
    message = message_manager.add_message(role, content, expert_type)
    
    assert message.id is not None and len(message.id) > 0
    assert message.timestamp is not None
    assert message.role == role
    assert message.content == content
    if role == MessageRole.EXPERT:
        assert message.expert_type is not None
```

### Unit Test Coverage

**Critical Unit Tests**:
1. Message creation with each role type (system, kimi, expert, user)
2. Empty context handling
3. Exactly 10 messages triggering summarization
4. StepFun API integration (with mocking)
5. Storage file creation and permissions
6. Intent recognition for each intent type
7. Error handling for each error scenario
8. Configuration prompt updates
9. Conversation reset confirmation

### Integration Testing

**Integration Test Scenarios**:
1. Full conversation flow: user message → expert response → news summary → summarization
2. Multi-expert conversation with context sharing
3. Summarization and re-summarization cycle
4. Application restart and state restoration
5. Concurrent message additions (if applicable)

### Test Data Generators

**Custom Generators for Property Tests**:
```python
# Message generator
@st.composite
def message_strategy(draw):
    role = draw(st.sampled_from(list(MessageRole)))
    content = draw(st.text(min_size=1, max_size=500))
    expert_type = draw(st.one_of(
        st.none(),
        st.sampled_from(["选股分析师", "产业链分析师", "市场分析师"])
    )) if role == MessageRole.EXPERT else None
    intent = draw(st.one_of(
        st.none(),
        st.sampled_from(list(Intent))
    )) if role == MessageRole.USER else None
    
    return {
        'role': role,
        'content': content,
        'expert_type': expert_type,
        'intent': intent
    }

# Conversation state generator
@st.composite
def conversation_state_strategy(draw):
    num_messages = draw(st.integers(min_value=0, max_value=20))
    messages = [draw(message_strategy()) for _ in range(num_messages)]
    has_summary = draw(st.booleans())
    summary = draw(summary_strategy()) if has_summary else None
    counter = draw(st.integers(min_value=0, max_value=10))
    
    return ConversationState(
        messages=messages,
        active_summary=summary,
        message_counter=counter,
        last_updated=datetime.now()
    )
```

### Test Execution

**Running Tests**:
```bash
# Run all tests
pytest tests/

# Run only property tests
pytest -m property_test

# Run with coverage
pytest --cov=services/expert_forum_chat_service tests/

# Run specific property test
pytest -k "test_message_creation_completeness"
```

### Continuous Integration

All tests SHALL run on:
- Every commit to feature branch
- Pull request creation
- Merge to main branch

Property tests SHALL run with minimum 100 iterations in CI environment.

## Implementation Notes

### File Structure

```
backend/
├── services/
│   ├── expert_forum_chat_service.py      # Main chat service
│   ├── message_manager.py                # Message management
│   ├── context_summarizer.py             # Summarization logic
│   ├── intent_recognizer.py              # Intent recognition
│   └── conversation_store.py             # Persistence layer
├── models/
│   ├── message.py                        # Message data model
│   ├── summary.py                        # Summary data model
│   └── conversation_state.py             # State model
├── routers/
│   └── expert_forum_chat.py              # API endpoints
└── tests/
    ├── test_message_manager.py
    ├── test_context_summarizer.py
    ├── test_intent_recognizer.py
    ├── test_conversation_store.py
    └── property_tests/
        ├── test_message_properties.py
        ├── test_context_properties.py
        └── test_persistence_properties.py

frontend/
├── src/
│   ├── services/
│   │   └── expertForumChatService.ts     # Frontend service
│   ├── components/
│   │   ├── ChatMessageList.tsx           # Message display
│   │   ├── ChatInput.tsx                 # User input
│   │   └── ConversationControls.tsx      # Reset, config
│   └── types/
│       └── chat.ts                       # TypeScript types
└── tests/
    └── expertForumChat.test.ts

data/
├── conversations/
│   └── conversation_state.json           # Persisted state
└── config/
    └── summarization_prompt.txt          # Custom prompt
```

### Integration Points

1. **Existing Expert Forum Service**: Extend `ExpertForumService` to use `ExpertForumChatService`
2. **News Summary Service**: Call `add_news_summary()` when news is fetched
3. **Expert Analysis**: Call `add_expert_response()` when expert generates analysis
4. **Frontend**: Update `ExpertForumPage.tsx` to use new chat components

### Performance Considerations

- **Message Storage**: Use append-only writes for performance
- **Context Retrieval**: Cache formatted context string until new message added
- **Summarization**: Async operation, don't block message additions
- **Storage**: Consider using SQLite for better query performance if message volume grows

### Security Considerations

- **Input Validation**: Sanitize all user input to prevent injection attacks
- **API Keys**: Store StepFun API key securely (environment variables)
- **File Permissions**: Ensure conversation data files have appropriate permissions
- **Rate Limiting**: Implement rate limiting on message additions to prevent abuse
