# Product Requirements Document: Firestore Integration for Dynamic Model Configuration

## Project Overview
Integrate Google Firestore into the Stock Analysis Agent backend to enable dynamic configuration of AI models for all agents. This will allow administrators to change which LLM model each agent uses in real-time through Firebase Console, without requiring code changes or service restarts.

## Problem Statement
Currently, all 11 specialized agents use a hardcoded model name (`gemini-2.5-flash`) defined in `app/sub_agents/utils/llm_model.py`. This creates several problems:
1. Cannot dynamically change models for specific agents
2. Cannot A/B test different models for performance comparison
3. Requires code changes and redeployment to change models
4. No flexibility to optimize cost vs performance per agent

## Goals
1. Load agent-to-model mappings from Firestore at backend startup
2. Enable real-time model configuration changes via Firebase Console
3. Support agent-specific model selection (e.g., hedge_fund_manager uses gemini-2.5-pro while others use gemini-2.5-flash)
4. Maintain backward compatibility if Firestore is unavailable
5. Minimize latency impact on agent execution

## Target Users
- System administrators who manage the Stock Analysis Agent deployment
- DevOps engineers who need to optimize model usage and costs
- Development team testing different model configurations

## Current System Architecture

### Agent Hierarchy (11 total agents):
```
root_agent
  └─ stock_analysis_department (ParallelAgent)
      ├─ stock_researcher_agent
      ├─ financial_team (SequentialAgent)
      │   ├─ parallel_financial_agent (ParallelAgent)
      │   │   ├─ balance_sheet_agent
      │   │   ├─ income_statement_agent
      │   │   ├─ cash_flow_statement_agent
      │   │   └─ basic_financial_analyst_agent
      │   └─ senior_financial_advisor_agent
      ├─ technical_analyst_agent
      ├─ quantitative_analysis_team (SequentialAgent)
      │   ├─ quantitative_analysis_agents (ParallelAgent)
      │   │   ├─ intrinsic_value_analyst_agent
      │   │   └─ growth_analyst_agent
      │   └─ senior_quantitative_advisor_agent
      └─ macro_economy_analyst_agent
  └─ hedge_fund_manager_agent
```

### Current Model Configuration
- File: `app/sub_agents/utils/llm_model.py`
- Function: `lite_llm_model()` returns `"gemini-2.5-flash"` (hardcoded)
- Usage: All agent creation functions call `lite_llm_model()` when setting the `model` parameter

## Firestore Schema (from FIRESTORE_GUIDE.md)

### Collection Structure:
```
stock_agents (collection)
  ├─ balance_sheet_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ income_statement_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ cash_flow_statement_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ basic_financial_analyst_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ senior_financial_advisor_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ stock_researcher_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ technical_analyst_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ intrinsic_value_analyst_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ growth_analyst_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ senior_quantitative_advisor_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  ├─ macro_economy_analyst_agent (document)
  │   └─ llm_model: "gemini-2.5-flash"
  └─ hedge_fund_manager_agent (document)
      └─ llm_model: "gemini-2.5-pro"
```

### Firebase Configuration (from FIRESTORE_GUIDE.md):
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDZpb_uTG95YAWbcQXZcDyMO2ySjua6rMA",
  authDomain: "stock-analysis-agent-a7bff.firebaseapp.com",
  projectId: "stock-analysis-agent-a7bff",
  storageBucket: "stock-analysis-agent-a7bff.firebasestorage.app",
  messagingSenderId: "38726995691",
  appId: "1:38726995691:web:f7f415d48dd657be2938ae"
}
```

## Technical Requirements

### Backend Requirements

1. **Firestore Python SDK Integration**
   - Add `firebase-admin` to `pyproject.toml` dependencies
   - Initialize Firestore client at application startup
   - Load all agent model configurations before agent creation

2. **Centralized Model Configuration Service**
   - Create `app/sub_agents/utils/firestore_config.py`
   - Implement singleton pattern to load configurations once at startup
   - Cache model mappings in memory for fast access
   - Provide `lite_llm_model(agent_name: str) -> str` function

3. **Modified `llm_model.py`**
   - Change from returning hardcoded string to accepting `agent_name` parameter
   - Call Firestore configuration service to get model name
   - Implement fallback to default model if Firestore lookup fails

4. **Startup Sequence**
   - Initialize Firestore client using Firebase Admin SDK
   - Load all agent configurations from `stock_agents` collection
   - Store in-memory cache (dictionary: agent_name -> model_name)
   - Create root agent hierarchy using cached configurations
   - Log any missing or invalid configurations

5. **Error Handling & Fallback**
   - If Firestore is unavailable: use default model (`gemini-2.5-flash`)
   - If specific agent config is missing: use default model
   - Log warnings for missing configurations
   - Never fail startup due to Firestore issues

### Configuration Requirements

1. **Environment Variables**
   - Add to `.env` and `.env.production`:
     ```
     FIREBASE_PROJECT_ID=stock-analysis-agent-a7bff
     FIREBASE_CREDENTIALS_PATH=/path/to/service-account-key.json
     # Or use GOOGLE_APPLICATION_CREDENTIALS
     ```

2. **Service Account Setup**
   - Create Firebase service account with Firestore read permissions
   - Store credentials file securely (not in git)
   - Document setup steps in guide

### Performance Requirements

1. **Startup Performance**
   - Firestore load must complete within 5 seconds
   - Parallel loading of configurations if possible
   - Timeout handling for slow Firestore responses

2. **Runtime Performance**
   - Zero latency impact during agent execution (use cached values)
   - No Firestore queries during user request processing
   - Model configuration lookup should be O(1) dictionary access

### Testing Requirements

1. **Unit Tests**
   - Test Firestore configuration loader with mock Firestore
   - Test fallback behavior when Firestore unavailable
   - Test `lite_llm_model()` with various agent names

2. **Integration Tests**
   - Test actual Firestore connection
   - Verify all 11 agents load correct models
   - Test model configuration changes via Firebase Console

## Implementation Scope

### In Scope
1. Backend Firestore integration
2. Dynamic model loading at startup
3. Agent-specific model configuration
4. Fallback to default models
5. Logging and error handling
6. Documentation and setup guide

### Out of Scope
1. Real-time model switching during agent execution (requires restart)
2. Frontend UI for model configuration (use Firebase Console)
3. Model performance monitoring/tracking
4. Cost tracking per model
5. Automatic model optimization/selection

## Success Criteria

1. **Functionality**
   - All 11 agents successfully load model configurations from Firestore
   - `lite_llm_model("balance_sheet_agent")` returns correct model name
   - Changing model in Firebase Console takes effect after backend restart
   - System functions normally when Firestore is unavailable (fallback mode)

2. **Performance**
   - Backend startup time increases by no more than 5 seconds
   - No measurable latency impact during user requests
   - Configuration cache hit rate: 100%

3. **Reliability**
   - System never fails to start due to Firestore issues
   - All error conditions are properly logged
   - Missing agent configurations use sensible defaults

## Implementation Phases

### Phase 1: Firestore Infrastructure
- Add firebase-admin dependency
- Create Firestore configuration service
- Implement connection and authentication
- Add environment variable configuration

### Phase 2: Model Loading System
- Implement configuration cache
- Create configuration loader at startup
- Add error handling and fallback logic
- Update logging

### Phase 3: Agent Integration
- Modify `llm_model.py` to accept agent_name parameter
- Update all agent creation functions to pass agent_name
- Test with all 11 agents
- Verify model configurations are applied

### Phase 4: Testing & Documentation
- Write unit tests for configuration service
- Write integration tests for Firestore connection
- Create setup guide for Firebase credentials
- Document Firebase Console usage for model changes

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Firestore unavailable at startup | High | Implement robust fallback to default models |
| Slow Firestore responses | Medium | Add timeout and use cached values |
| Missing agent configurations | Medium | Use default model and log warning |
| Invalid model names in Firestore | Medium | Validate model names, use default if invalid |
| Service account credential issues | High | Document setup clearly, validate at startup |

## Dependencies

### New Python Dependencies
- `firebase-admin>=6.0.0` - Firebase Admin SDK for Python

### External Services
- Firebase/Firestore (already configured in FIRESTORE_GUIDE.md)

## Documentation Needs

1. **Setup Guide**: `guide/FIRESTORE_SETUP.md`
   - How to create Firebase service account
   - Where to store credentials
   - Environment variable configuration
   - Initial Firestore data population

2. **Configuration Guide**: `guide/MODEL_CONFIGURATION.md`
   - How to change model per agent via Firebase Console
   - List of supported model names
   - When changes take effect (restart required)
   - Troubleshooting common issues

## Future Enhancements (Not in Current Scope)

1. **Real-time Configuration Reloading**
   - Listen to Firestore changes
   - Hot-swap models without restart
   - Requires coordination with agent lifecycle

2. **Frontend Configuration UI**
   - Admin dashboard for model configuration
   - Visual model performance comparison
   - Cost estimation per configuration

3. **A/B Testing Framework**
   - Split traffic between model configurations
   - Collect performance metrics
   - Automatic model selection based on metrics

4. **Model Rotation Strategy**
   - Periodic model updates based on performance
   - Fallback to previous model on errors
   - Blue-green deployment for models