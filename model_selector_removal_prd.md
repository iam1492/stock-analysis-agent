# Product Requirements Document: ModelSelector Removal Refactoring

## Overview
Remove the ModelSelector component and all related functionality from the stock analysis application. The ModelSelector is currently non-functional as the model is hardcoded to "gemini-2.5-flash", and users cannot actually select different models through the UI.

## Goals
- Completely remove ModelSelector component from the frontend
- Remove all model selection logic from frontend-backend communication
- Ensure no impact on other stock analysis service features
- Clean up all related code in both nextjs and app directories

## Scope
- **Frontend (nextjs/)**: Remove ModelSelector component and related UI elements
- **Backend (app/)**: Remove model selection handling logic
- **Communication**: Remove model parameter passing between frontend and backend

## Requirements
1. **Frontend Changes**:
   - Remove ModelSelector component from chat interface
   - Remove model selection state management
   - Remove model-related props and handlers
   - Clean up imports and dependencies

2. **Backend Changes**:
   - Remove model parameter handling in API endpoints
   - Remove model validation and processing logic
   - Ensure default model ("gemini-2.5-flash") remains hardcoded

3. **Communication**:
   - Remove model parameter from SSE/WebSocket messages
   - Remove model-related request/response fields

## Constraints
- Must not affect any other stock analysis functionality
- Application must continue to work with hardcoded "gemini-2.5-flash" model
- No breaking changes to existing API contracts (except model selection)
- All changes must be backward compatible where possible

## Success Criteria
- ModelSelector component completely removed from UI
- No model selection options visible to users
- Application functions normally with existing features
- No console errors or warnings related to removed code
- Clean, maintainable codebase without dead code