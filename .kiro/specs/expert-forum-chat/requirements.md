# Requirements Document: Expert Forum Chat

## Introduction

The Expert Forum Chat feature enhances the existing expert forum system by adding intelligent conversation management capabilities. The system enables multi-party conversations between users, AI experts, and news summary services, with automatic context summarization to maintain conversation quality and manage token limits. This feature ensures that expert responses remain relevant and contextual while preventing conversation history from growing unbounded.

## Glossary

- **Expert_Forum_System**: The existing intelligent trading platform forum where AI experts provide market analysis
- **Chat_Message**: A single message in the conversation, which can be from a user, expert, news service, or system
- **Conversation_Context**: The collection of messages that experts use to generate responses
- **Context_Summarizer**: The AI service (阶跃星辰8k model) that condenses conversation history
- **Message_Visibility_Filter**: The component that controls which messages each participant can see
- **User_Intent**: The recognized purpose or request extracted from user input
- **Expert_Agent**: An AI agent configured with specific expertise (e.g., stock analyst, industry analyst)
- **News_Summary_Service**: The AI service that generates market news summaries using StepFun API
- **Message_Counter**: The component that tracks the number of messages to trigger summarization
- **Summary_Threshold**: The message count limit (10 messages) that triggers context summarization

## Requirements

### Requirement 1: Message Management and Storage

**User Story:** As a system, I want to manage and store all conversation messages, so that the conversation history can be maintained and retrieved.

#### Acceptance Criteria

1. WHEN a message is created, THE Chat_Message_Store SHALL assign it a unique identifier, timestamp, role type, and content
2. WHEN a message is stored, THE Chat_Message_Store SHALL persist it with metadata including sender role (system, kimi, expert, user), expert type (if applicable), and timestamp
3. WHEN retrieving messages, THE Chat_Message_Store SHALL return messages in chronological order
4. THE Chat_Message_Store SHALL support message roles: system, kimi, expert, and user
5. WHEN an expert sends a message, THE Chat_Message_Store SHALL include the expert type identifier

### Requirement 2: Message Visibility Control

**User Story:** As an expert agent, I want to see all relevant conversation messages except system prompts, so that I can provide contextual analysis without being influenced by system instructions.

#### Acceptance Criteria

1. WHEN constructing context for experts, THE Message_Visibility_Filter SHALL include all messages with roles: kimi, expert, and user
2. WHEN constructing context for experts, THE Message_Visibility_Filter SHALL exclude all messages with role: system
3. FOR ALL expert analysis requests, THE Message_Visibility_Filter SHALL apply visibility rules before passing context to experts
4. WHEN a user message is added, THE Message_Visibility_Filter SHALL make it visible to all experts
5. WHEN an expert message is added, THE Message_Visibility_Filter SHALL make it visible to all other experts and users

### Requirement 3: Message Counting and Threshold Detection

**User Story:** As a system, I want to track the number of messages in the conversation, so that I can trigger summarization when the threshold is reached.

#### Acceptance Criteria

1. WHEN a new message is added to the conversation, THE Message_Counter SHALL increment the count by one
2. WHEN counting messages, THE Message_Counter SHALL only count messages visible to experts (excluding system messages)
3. WHEN the message count reaches 10, THE Message_Counter SHALL trigger the Context_Summarizer
4. WHEN the message count exceeds 10, THE Message_Counter SHALL trigger the Context_Summarizer immediately
5. AFTER summarization completes, THE Message_Counter SHALL reset to zero

### Requirement 4: Conversation Context Summarization

**User Story:** As a system, I want to automatically summarize conversation history when it becomes too long, so that expert responses remain efficient and contextual without exceeding token limits.

#### Acceptance Criteria

1. WHEN the message count exceeds 10, THE Context_Summarizer SHALL invoke the 阶跃星辰8k model to generate a summary
2. WHEN summarizing, THE Context_Summarizer SHALL include all expert-visible messages (kimi, expert, user roles)
3. WHEN summarizing, THE Context_Summarizer SHALL preserve key information including: market insights, expert recommendations, user questions, and important context
4. WHEN summarization completes, THE Context_Summarizer SHALL return a condensed summary text
5. THE Context_Summarizer SHALL use the 阶跃星辰8k (StepFun) API for generating summaries

### Requirement 5: Context Replacement After Summarization

**User Story:** As a system, I want to replace the conversation context with the summary after summarization, so that subsequent expert responses use the condensed context instead of the full history.

#### Acceptance Criteria

1. WHEN a summary is generated, THE Expert_Forum_System SHALL replace the conversation context with the summary text
2. WHEN context is replaced, THE Expert_Forum_System SHALL preserve the summary as a special context message
3. WHEN experts request context after summarization, THE Expert_Forum_System SHALL provide the summary plus any new messages since summarization
4. WHEN new messages are added after summarization, THE Expert_Forum_System SHALL append them to the summary context
5. WHEN the combined summary and new messages exceed 10 messages again, THE Expert_Forum_System SHALL trigger re-summarization

### Requirement 6: User Intent Recognition

**User Story:** As a user, I want the system to recognize my intent from my input, so that experts can provide more targeted responses.

#### Acceptance Criteria

1. WHEN a user submits a message, THE User_Intent_Recognizer SHALL analyze the message content
2. WHEN analyzing user input, THE User_Intent_Recognizer SHALL identify common intents such as: stock recommendation request, portfolio analysis request, market outlook request, risk assessment request, and general question
3. WHEN an intent is recognized, THE User_Intent_Recognizer SHALL tag the message with the identified intent
4. WHEN no clear intent is identified, THE User_Intent_Recognizer SHALL tag the message as general conversation
5. WHEN experts receive context, THE Expert_Forum_System SHALL include user intent tags to help experts provide relevant responses

### Requirement 7: Integration with News Summary Service

**User Story:** As a system, I want to integrate news summaries into the conversation, so that experts have access to the latest market information.

#### Acceptance Criteria

1. WHEN news summaries are generated, THE Expert_Forum_System SHALL add them to the conversation as messages with role "kimi"
2. WHEN adding news summaries, THE Expert_Forum_System SHALL include timestamp and relevant stock symbols
3. WHEN experts request context, THE Expert_Forum_System SHALL include the most recent news summary
4. WHEN counting messages for summarization, THE Expert_Forum_System SHALL include news summary messages in the count
5. WHEN summarizing context, THE Context_Summarizer SHALL preserve key market insights from news summaries

### Requirement 8: Integration with Expert Analysis

**User Story:** As a system, I want to integrate expert analysis responses into the conversation, so that all participants can see expert insights.

#### Acceptance Criteria

1. WHEN an expert generates analysis, THE Expert_Forum_System SHALL add it to the conversation as a message with role "expert"
2. WHEN adding expert messages, THE Expert_Forum_System SHALL include the expert type identifier (e.g., "选股分析师", "产业链分析师")
3. WHEN multiple experts respond, THE Expert_Forum_System SHALL maintain the order of expert responses
4. WHEN experts request context, THE Expert_Forum_System SHALL include all previous expert messages
5. WHEN counting messages for summarization, THE Expert_Forum_System SHALL include expert messages in the count

### Requirement 9: User Message Input and Processing

**User Story:** As a user, I want to input my thoughts and questions into the conversation, so that experts can respond to my specific needs.

#### Acceptance Criteria

1. WHEN a user submits input, THE Expert_Forum_System SHALL create a message with role "user"
2. WHEN processing user input, THE Expert_Forum_System SHALL validate that the input is not empty
3. WHEN user input is added, THE Expert_Forum_System SHALL make it immediately visible to all experts
4. WHEN user input is added, THE Expert_Forum_System SHALL trigger intent recognition
5. WHEN user input is added, THE Expert_Forum_System SHALL increment the message counter

### Requirement 10: Context Retrieval for Expert Responses

**User Story:** As an expert agent, I want to retrieve the current conversation context, so that I can generate relevant and informed responses.

#### Acceptance Criteria

1. WHEN an expert requests context, THE Expert_Forum_System SHALL return all expert-visible messages in chronological order
2. WHEN context has been summarized, THE Expert_Forum_System SHALL return the summary followed by new messages
3. WHEN no summarization has occurred, THE Expert_Forum_System SHALL return all messages from the conversation start
4. WHEN constructing context, THE Expert_Forum_System SHALL format messages with clear role indicators
5. WHEN context is empty, THE Expert_Forum_System SHALL return an empty context indicator

### Requirement 11: Conversation State Persistence

**User Story:** As a system, I want to persist conversation state across sessions, so that users can resume conversations after closing and reopening the application.

#### Acceptance Criteria

1. WHEN messages are added, THE Expert_Forum_System SHALL persist them to storage immediately
2. WHEN the application restarts, THE Expert_Forum_System SHALL restore the conversation history from storage
3. WHEN restoring conversations, THE Expert_Forum_System SHALL restore the message counter state
4. WHEN restoring conversations, THE Expert_Forum_System SHALL restore any active summary context
5. THE Expert_Forum_System SHALL store conversation data in a structured format (JSON)

### Requirement 12: Error Handling and Resilience

**User Story:** As a system, I want to handle errors gracefully during summarization and message processing, so that conversation flow is not disrupted by failures.

#### Acceptance Criteria

1. IF the Context_Summarizer fails to generate a summary, THEN THE Expert_Forum_System SHALL log the error and continue using the full context
2. IF message storage fails, THEN THE Expert_Forum_System SHALL retry the operation up to 3 times
3. IF intent recognition fails, THEN THE Expert_Forum_System SHALL tag the message as "unknown intent" and continue processing
4. IF the 阶跃星辰8k API is unavailable, THEN THE Expert_Forum_System SHALL fall back to using the full context without summarization
5. WHEN any error occurs, THE Expert_Forum_System SHALL log detailed error information for debugging

### Requirement 13: Summarization Prompt Configuration

**User Story:** As a system administrator, I want to configure the summarization prompt, so that the summary quality and focus can be customized.

#### Acceptance Criteria

1. THE Expert_Forum_System SHALL provide a default summarization prompt that emphasizes preserving key market insights and user questions
2. WHEN a custom summarization prompt is provided, THE Context_Summarizer SHALL use it instead of the default
3. WHEN no custom prompt is configured, THE Context_Summarizer SHALL use the default prompt
4. THE Expert_Forum_System SHALL allow updating the summarization prompt through configuration
5. WHEN the summarization prompt is updated, THE Expert_Forum_System SHALL use the new prompt for subsequent summarizations

### Requirement 14: Message Formatting and Display

**User Story:** As a user, I want to see clearly formatted messages with role indicators, so that I can easily distinguish between different types of messages.

#### Acceptance Criteria

1. WHEN displaying messages, THE Expert_Forum_System SHALL include a role label (e.g., "KimiClaw资讯", "选股分析师", "用户")
2. WHEN displaying messages, THE Expert_Forum_System SHALL include a timestamp in local time format
3. WHEN displaying expert messages, THE Expert_Forum_System SHALL include the expert type name
4. WHEN displaying messages, THE Expert_Forum_System SHALL use distinct visual styling for different roles
5. WHEN displaying the conversation, THE Expert_Forum_System SHALL show messages in chronological order

### Requirement 15: Conversation Reset and Management

**User Story:** As a user, I want to reset or clear the conversation, so that I can start fresh discussions on new topics.

#### Acceptance Criteria

1. WHEN a user requests conversation reset, THE Expert_Forum_System SHALL clear all messages from the conversation
2. WHEN resetting, THE Expert_Forum_System SHALL reset the message counter to zero
3. WHEN resetting, THE Expert_Forum_System SHALL clear any active summary context
4. WHEN resetting, THE Expert_Forum_System SHALL preserve expert configurations
5. WHEN resetting, THE Expert_Forum_System SHALL confirm the action with the user before proceeding
