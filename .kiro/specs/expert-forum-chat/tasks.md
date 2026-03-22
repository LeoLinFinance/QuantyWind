# Implementation Plan: Expert Forum Chat

## Overview

This implementation plan breaks down the Expert Forum Chat feature into discrete, incremental tasks. The approach follows a bottom-up strategy: first implementing core data models and storage, then building the message management layer, adding context summarization, integrating with existing services, and finally updating the frontend UI. Each task builds on previous work, with property-based tests integrated throughout to validate correctness properties.

## Tasks

- [ ] 1. Create core data models and enums
  - Create `backend/models/message.py` with Message class, MessageRole enum, and Intent enum
  - Create `backend/models/summary.py` with Summary class
  - Create `backend/models/conversation_state.py` with ConversationState class
  - Implement serialization methods (to_dict, from_dict) for all models
  - _Requirements: 1.1, 1.2_

- [ ]* 1.1 Write property tests for data model serialization
  - **Property 2: Message Persistence Round-Trip**
  - **Validates: Requirements 1.2, 11.2**
  - Test that Message.to_dict() → Message.from_dict() preserves all fields
  - Test that Summary.to_dict() → Summary.from_dict() preserves all fields

- [ ] 2. Implement conversation storage layer
  - [ ] 2.1 Create `backend/services/conversation_store.py` with ConversationContextStore class
    - Implement save_message() method with JSON file persistence
    - Implement load_messages() method to restore from JSON
    - Implement save_summary() and get_active_summary() methods
    - Implement message counter management (get_message_counter, reset_counter)
    - Implement clear_all() method for conversation reset
    - _Requirements: 11.1, 11.2, 11.5, 15.1, 15.2, 15.3_

  - [ ]* 2.2 Write property test for storage round-trip
    - **Property 28: Conversation State Round-Trip**
    - **Validates: Requirements 11.2**
    - Test that saving and loading conversation state preserves all data

  - [ ]* 2.3 Write property test for JSON format validation
    - **Property 29: JSON Storage Format**
    - **Validates: Requirements 11.5**
    - Test that saved data is valid JSON

  - [ ]* 2.4 Write unit tests for storage error handling
    - Test retry logic for storage failures (3 retries)
    - Test handling of corrupted JSON files
    - _Requirements: 12.2_

- [ ] 3. Implement message manager
  - [ ] 3.1 Create `backend/services/message_manager.py` with MessageManager class
    - Implement add_message() with validation and ID generation
    - Implement get_messages() with filtering options
    - Implement get_message_count() for visible messages only
    - Implement clear_messages() method
    - Implement get_context_for_expert() with visibility filtering and formatting
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.1, 2.3, 3.1, 3.2, 10.1, 10.4_

  - [ ]* 3.2 Write property test for message creation
    - **Property 1: Message Creation Completeness**
    - **Validates: Requirements 1.1**
    - Test that all created messages have required fields

  - [ ]* 3.3 Write property test for chronological ordering
    - **Property 3: Chronological Message Ordering**
    - **Validates: Requirements 1.3**
    - Test that messages are always returned in timestamp order

  - [ ]* 3.4 Write property test for visibility filtering
    - **Property 5: Message Visibility Filtering**
    - **Validates: Requirements 2.1, 2.3**
    - Test that only kimi/expert/user messages are visible to experts

  - [ ]* 3.5 Write property test for message counter
    - **Property 6: Message Counter Increment**
    - **Property 7: Visible Message Counting**
    - **Validates: Requirements 3.1, 3.2**
    - Test that counter increments correctly for visible messages

  - [ ]* 3.6 Write property test for context formatting
    - **Property 26: Context Formatting with Role Indicators**
    - **Validates: Requirements 10.4**
    - Test that context strings include role labels

  - [ ]* 3.7 Write unit tests for message manager
    - Test each message role type (system, kimi, expert, user)
    - Test empty context handling
    - Test expert message metadata requirement
    - _Requirements: 1.4, 1.5, 10.5_

- [ ] 4. Checkpoint - Ensure core message management tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement intent recognizer
  - [ ] 5.1 Create `backend/services/intent_recognizer.py` with IntentRecognizer class
    - Implement recognize_intent() with keyword-based matching
    - Define intent keywords for each intent type (stock_recommendation, portfolio_analysis, market_outlook, risk_assessment, general_question)
    - Implement fallback to "unknown" intent
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 5.2 Write property test for intent tagging
    - **Property 15: User Message Intent Tagging**
    - **Validates: Requirements 6.3**
    - Test that all user messages receive an intent tag

  - [ ]* 5.3 Write unit tests for intent recognition
    - Test recognition of each intent type with clear examples
    - Test fallback to general_question for ambiguous input
    - Test error handling when recognition fails
    - _Requirements: 6.2, 6.4, 12.3_

- [ ] 6. Implement context summarizer
  - [ ] 6.1 Create `backend/services/context_summarizer.py` with ContextSummarizer class
    - Initialize with StepFun API client (阶跃星辰8k model: step-1-8k)
    - Implement should_summarize() to check threshold (> 10 messages)
    - Implement summarize_conversation() to call StepFun API
    - Implement get_default_prompt() with market-focused summarization prompt
    - Implement update_prompt() for custom prompt configuration
    - _Requirements: 3.3, 3.4, 4.1, 4.2, 4.4, 13.1, 13.2, 13.4_

  - [ ]* 6.2 Write property test for summarization trigger
    - **Property 8: Summarization Trigger**
    - **Validates: Requirements 3.4**
    - Test that summarization triggers when count exceeds 10

  - [ ]* 6.3 Write property test for summary input
    - **Property 10: Summary Input Completeness**
    - **Validates: Requirements 4.2**
    - Test that only expert-visible messages are included in summary input

  - [ ]* 6.4 Write property test for summary output
    - **Property 11: Summary Output Non-Empty**
    - **Validates: Requirements 4.4**
    - Test that successful summarization returns non-empty text

  - [ ]* 6.5 Write unit tests for context summarizer
    - Test StepFun API integration (with mocking)
    - Test default prompt usage
    - Test custom prompt override
    - Test error handling for API failures
    - _Requirements: 4.1, 12.1, 13.2_

- [ ] 7. Implement main chat service
  - [ ] 7.1 Create `backend/services/expert_forum_chat_service.py` with ExpertForumChatService class
    - Initialize with MessageManager, ContextSummarizer, IntentRecognizer, and ConversationContextStore
    - Implement add_user_message() with intent recognition and counter check
    - Implement add_news_summary() for kimi role messages
    - Implement add_expert_response() for expert role messages
    - Implement get_context_for_expert() with summarization logic
    - Implement reset_conversation() method
    - Implement get_conversation_history() for UI display
    - _Requirements: 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 8.1, 8.2, 9.1, 9.2, 15.1, 15.2, 15.3, 15.4_

  - [ ]* 7.2 Write property test for counter reset after summarization
    - **Property 9: Counter Reset After Summarization**
    - **Validates: Requirements 3.5**
    - Test that counter resets to zero after summarization

  - [ ]* 7.3 Write property test for context replacement
    - **Property 12: Context Replacement After Summarization**
    - **Validates: Requirements 5.1, 5.2**
    - Test that summary is stored and accessible after summarization

  - [ ]* 7.4 Write property test for post-summarization context
    - **Property 13: Post-Summarization Context Composition**
    - **Validates: Requirements 5.3, 10.1**
    - Test that context includes summary + new messages after summarization

  - [ ]* 7.5 Write property test for re-summarization
    - **Property 14: Re-Summarization Trigger**
    - **Validates: Requirements 5.5**
    - Test that summarization triggers again after 10 new messages

  - [ ]* 7.6 Write property tests for message role validation
    - **Property 17: News Summary Message Role**
    - **Property 20: Expert Response Message Role**
    - **Property 24: User Input Message Role**
    - **Validates: Requirements 7.1, 8.1, 9.1**
    - Test that each message type has correct role

  - [ ]* 7.7 Write property test for empty input rejection
    - **Property 25: Empty Input Rejection**
    - **Validates: Requirements 9.2**
    - Test that empty/whitespace-only input is rejected

  - [ ]* 7.8 Write property test for conversation reset
    - **Property 32: Conversation Reset Completeness**
    - **Validates: Requirements 15.1, 15.2, 15.3, 15.4**
    - Test that reset clears messages/counter/summary but preserves configs

  - [ ]* 7.9 Write unit tests for chat service
    - Test full conversation flow (user → expert → news → summarization)
    - Test message counting for different message types
    - Test intent inclusion in context
    - _Requirements: 6.5, 7.4, 8.5, 16_

- [ ] 8. Checkpoint - Ensure all core service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Create API endpoints
  - [ ] 9.1 Create `backend/routers/expert_forum_chat.py` with FastAPI router
    - Create POST /api/expert-forum-chat/messages endpoint for adding user messages
    - Create GET /api/expert-forum-chat/messages endpoint for retrieving conversation history
    - Create GET /api/expert-forum-chat/context endpoint for getting expert context
    - Create POST /api/expert-forum-chat/reset endpoint for resetting conversation
    - Create GET /api/expert-forum-chat/summary-config endpoint for getting summarization prompt
    - Create POST /api/expert-forum-chat/summary-config endpoint for updating summarization prompt
    - Add request/response models using Pydantic
    - _Requirements: 9.1, 9.2, 13.4, 15.1_

  - [ ]* 9.2 Write integration tests for API endpoints
    - Test full API flow: add messages → get context → reset
    - Test error responses for invalid input
    - Test prompt configuration endpoints

- [ ] 10. Integrate with existing expert forum service
  - [ ] 10.1 Update `backend/services/expert_forum_service.py`
    - Add ExpertForumChatService as a dependency
    - Modify fetch_news_summary() to call chat_service.add_news_summary()
    - Modify get_expert_analysis() to use chat_service.get_context_for_expert()
    - Modify get_expert_analysis() to call chat_service.add_expert_response() with result
    - _Requirements: 7.1, 7.2, 7.3, 8.1, 8.2, 10.1_

  - [ ]* 10.2 Write integration tests for expert forum service
    - Test that news summaries are added to conversation
    - Test that expert responses are added to conversation
    - Test that experts receive proper context with chat history

- [ ] 11. Update frontend components
  - [ ] 11.1 Create `src/services/expertForumChatService.ts`
    - Implement API client methods for all chat endpoints
    - Add TypeScript types for Message, ConversationState, etc.
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 11.2 Create `src/components/ChatMessageList.tsx`
    - Display messages with role-based styling
    - Show role labels, timestamps, and expert types
    - Implement auto-scroll to latest message
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 11.3 Create `src/components/ChatInput.tsx`
    - User input field with validation
    - Submit button and Enter key handling
    - Empty input prevention
    - _Requirements: 9.2_

  - [ ] 11.4 Create `src/components/ConversationControls.tsx`
    - Reset conversation button with confirmation dialog
    - Summarization prompt configuration modal
    - Display message count and summarization status
    - _Requirements: 13.4, 15.5_

  - [ ] 11.5 Update `src/pages/ExpertForumPage.tsx`
    - Integrate new chat components
    - Replace direct message display with ChatMessageList
    - Add ChatInput component for user interaction
    - Add ConversationControls component
    - Update message handling to use chat service
    - _Requirements: 9.1, 14.1, 14.2, 14.3, 15.5_

- [ ] 12. Add property-based test infrastructure
  - [ ] 12.1 Create custom generators in `backend/tests/property_tests/generators.py`
    - Implement message_strategy() generator for random messages
    - Implement conversation_state_strategy() generator for random conversation states
    - Implement summary_strategy() generator for random summaries
    - Configure hypothesis settings (min 100 iterations)

  - [ ] 12.2 Create test utilities in `backend/tests/property_tests/utils.py`
    - Helper functions for test setup and teardown
    - Mock StepFun API responses
    - Test data fixtures

- [ ] 13. Final integration and testing
  - [ ]* 13.1 Write end-to-end integration tests
    - Test complete user flow: open page → receive news → experts respond → user asks question → summarization → more discussion
    - Test application restart and state restoration
    - Test concurrent expert responses
    - _Requirements: 11.2_

  - [ ]* 13.2 Write property test for immediate persistence
    - **Property 27: Immediate Message Persistence**
    - **Validates: Requirements 11.1**
    - Test that messages are saved before add operation completes

  - [ ]* 13.3 Write property test for prompt persistence
    - **Property 30: Prompt Update Persistence**
    - **Validates: Requirements 13.5**
    - Test that updated prompts are used in subsequent summarizations

  - [ ] 13.4 Perform manual testing
    - Test full conversation flow in browser
    - Test error scenarios (API failures, network issues)
    - Test UI responsiveness and styling
    - Verify message display formatting

- [ ] 14. Final checkpoint - Ensure all tests pass
  - Run full test suite with coverage report
  - Verify all property tests pass with 100+ iterations
  - Ensure all integration tests pass
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and error conditions
- The implementation follows a bottom-up approach: models → storage → services → API → UI
- StepFun API model for summarization: `step-1-8k` (阶跃星辰8k)
- All conversation data is stored in `data/conversations/conversation_state.json`
- Custom summarization prompt stored in `data/config/summarization_prompt.txt`
