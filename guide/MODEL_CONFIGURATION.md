# AI Model Configuration Guide

This guide explains how to manage AI model configurations for Stock Analysis Agent's 11 specialized agents using Firebase Console.

## Overview

Stock Analysis Agent uses Google Firestore to store model configurations for each agent. This allows administrators to change which LLM model each agent uses without modifying code or redeploying the service.

## Agent List

The system has 12 agents (11 specialized + 1 root):

| Agent Name | Purpose | Default Model |
|-----------|---------|---------------|
| `balance_sheet_agent` | Balance sheet analysis | gemini-2.5-flash |
| `income_statement_agent` | Income statement analysis | gemini-2.5-flash |
| `cash_flow_statement_agent` | Cash flow analysis | gemini-2.5-flash |
| `basic_financial_analyst_agent` | Key metrics & ratios | gemini-2.5-flash |
| `senior_financial_advisor_agent` | Financial team synthesis | gemini-2.5-flash |
| `stock_researcher_agent` | News & market sentiment | gemini-2.5-flash |
| `technical_analyst_agent` | Technical indicators | gemini-2.5-flash |
| `intrinsic_value_analyst_agent` | DCF valuation | gemini-2.5-flash |
| `growth_analyst_agent` | Growth metrics | gemini-2.5-flash |
| `senior_quantitative_advisor_agent` | Quant team synthesis | gemini-2.5-flash |
| `macro_economy_analyst_agent` | Economic indicators | gemini-2.5-flash |
| `hedge_fund_manager_agent` | Final investment report | gemini-2.5-pro |

## Accessing Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: `stock-analysis-agent-a7bff`
3. Navigate to **Firestore Database** in the left sidebar
4. Click on **Data** tab

You should see the `stock_agents` collection with 12 documents.

## Changing Agent Models

### Method 1: Edit via Firebase Console UI

1. **Navigate to Collection**:
   - Open Firestore Database → Data
   - Click on `stock_agents` collection

2. **Select Agent to Modify**:
   - Click on the agent document (e.g., `hedge_fund_manager_agent`)

3. **Edit Model Field**:
   - Click on the `llm_model` field value
   - Change to desired model name (see Supported Models below)
   - Click **Update**

4. **Restart Backend**:
   - **IMPORTANT**: Changes take effect only after backend restart
   - See "Applying Changes" section below

### Method 2: Edit via Firebase CLI (Advanced)

```bash
# Install Firebase CLI if not already installed
npm install -g firebase-tools

# Login to Firebase
firebase login

# Use project
firebase use stock-analysis-agent-a7bff

# Update model via Firestore CLI
firebase firestore:set stock_agents/hedge_fund_manager_agent '{
  "llm_model": "gemini-2.5-pro"
}' --merge
```

### Method 3: Programmatic Update (Python Script)

Create a script to bulk update models:

```python
# scripts/update_models.py
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Update specific agent
db.collection('stock_agents').document('hedge_fund_manager_agent').update({
    'llm_model': 'gemini-2.5-pro'
})

print("✅ Model updated successfully!")
```

Run:
```bash
uv run python scripts/update_models.py
```

## Supported Models

### Google Gemini Models (Recommended)

| Model Name | Context Window | Strengths | Cost |
|-----------|----------------|-----------|------|
| `gemini-2.5-flash` | 1M tokens | Fast, cost-effective | Low |
| `gemini-2.5-pro` | 2M tokens | Advanced reasoning | Medium |
| `gemini-1.5-flash` | 1M tokens | Legacy fast model | Low |
| `gemini-1.5-pro` | 2M tokens | Legacy pro model | Medium |

### Other Models (via LiteLLM)

The system uses LiteLLM, so you can configure models from other providers:

```
# OpenAI
gpt-4o
gpt-4-turbo
gpt-3.5-turbo

# Anthropic Claude
claude-3-opus
claude-3-sonnet
claude-3-haiku

# Example: Using OpenAI GPT-4
llm_model: "gpt-4o"
```

**Note**: Requires appropriate API keys set in environment variables.

## Configuration Strategies

### Strategy 1: Cost Optimization

Use cheaper models for simpler tasks:

```
balance_sheet_agent: gemini-2.5-flash
income_statement_agent: gemini-2.5-flash
cash_flow_statement_agent: gemini-2.5-flash
...
hedge_fund_manager_agent: gemini-2.5-pro  # Only final synthesis uses pro
```

**Impact**: Reduces cost by ~60% while maintaining quality

### Strategy 2: Quality Maximization

Use premium models for all agents:

```
All agents: gemini-2.5-pro
```

**Impact**: Higher cost, potentially better analysis

### Strategy 3: Hybrid Approach

Use pro models for critical agents:

```
# Standard models
balance_sheet_agent: gemini-2.5-flash
income_statement_agent: gemini-2.5-flash
...

# Premium for synthesis and advisor agents
senior_financial_advisor_agent: gemini-2.5-pro
senior_quantitative_advisor_agent: gemini-2.5-pro
hedge_fund_manager_agent: gemini-2.5-pro
```

**Impact**: Balanced cost/quality tradeoff

## Applying Changes

### Restart Requirement

**CRITICAL**: Model changes take effect **only after backend restart**.

**Why?**: The backend loads configurations once at startup and caches them in memory for performance.

### Development Environment

```bash
# Stop backend (Ctrl+C if running)
# Then restart:
make dev-backend

# Or if using uv directly:
uv run adk api_server app.agent
```

**Verify**:
Check logs for:
```
✅ Successfully loaded 12 agent configuration(s) from Firestore
```

### Production Environment (Docker)

**SSH into VPS**:
```bash
ssh user@158.247.216.21
cd /opt/stock-analysis
```

**Restart Backend Service**:
```bash
# Restart only backend
docker-compose restart stock-analysis-backend

# Or restart all services
docker-compose down
docker-compose up -d
```

**Verify**:
```bash
# Check logs
docker-compose logs -f stock-analysis-backend | grep Firestore

# Expected output:
# ✅ Successfully loaded 12 agent configuration(s) from Firestore
```

**Zero-Downtime Restart (Advanced)**:
```bash
# Start new backend instance
docker-compose up -d --no-deps --scale stock-analysis-backend=2 stock-analysis-backend

# Wait for new instance to be ready (check logs)
sleep 10

# Scale down to 1 instance (removes old one)
docker-compose up -d --no-deps --scale stock-analysis-backend=1 stock-analysis-backend
```

## Verification

### 1. Check Firestore Update

**Via Firebase Console**:
- Open Firestore Database → Data → `stock_agents`
- Verify model field shows new value

### 2. Check Backend Logs

**Development**:
```bash
# Logs show loaded configurations
make dev-backend
```

**Production**:
```bash
docker-compose logs stock-analysis-backend | grep -A 12 "Loading agent"
```

Expected output:
```
📥 Loading agent configurations from Firestore collection 'stock_agents'...
  ✓ balance_sheet_agent → gemini-2.5-flash
  ✓ income_statement_agent → gemini-2.5-flash
  ...
  ✓ hedge_fund_manager_agent → gemini-2.5-pro
✅ Successfully loaded 12 agent configuration(s) from Firestore
```

### 3. Test Stock Analysis

Run a stock analysis request and verify the agent uses correct model:

```
User: Analyze AAPL stock
```

Check logs for model usage:
```
🎯 Agent 'hedge_fund_manager_agent' using model 'gemini-2.5-pro'
```

## Bulk Configuration Management

### Export Current Configuration

```python
# scripts/export_config.py
from app.sub_agents.utils.firestore_config import FirestoreConfig
import json

FirestoreConfig.load_configs()
configs = FirestoreConfig.get_all_configs()

with open('model_config_backup.json', 'w') as f:
    json.dump(configs, f, indent=2)

print(f"✅ Exported {len(configs)} configurations")
```

### Import Configuration

```python
# scripts/import_config.py
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize
cred = credentials.Certificate('./credentials/service-account.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load config
with open('model_config_backup.json') as f:
    configs = json.load(f)

# Update Firestore
for agent_name, model_name in configs.items():
    db.collection('stock_agents').document(agent_name).set({
        'llm_model': model_name
    })
    print(f'✅ {agent_name} → {model_name}')
```

## Troubleshooting

### Issue: Changes Not Applied

**Symptoms**: Model still using old configuration after update

**Causes**:
1. Backend not restarted
2. Firestore update didn't save
3. Cache not cleared

**Solution**:
```bash
# 1. Verify Firestore update
# Check Firebase Console

# 2. Restart backend
docker-compose restart stock-analysis-backend

# 3. Force reload configuration
# In Python shell:
from app.sub_agents.utils.firestore_config import FirestoreConfig
FirestoreConfig.reload_configs()
```

### Issue: Invalid Model Name

**Symptoms**: Backend logs show warnings about unknown model

**Example**:
```
⚠️  Agent 'balance_sheet_agent' model 'invalid-model' not recognized
⚠️  Falling back to default model 'gemini-2.5-flash'
```

**Solution**: Check model name spelling in Firestore. Must match exactly:
- ✅ `gemini-2.5-pro`
- ❌ `gemini-2.5pro` (missing hyphen)
- ❌ `Gemini-2.5-Pro` (wrong case)

### Issue: Firestore Connection Failed

**Symptoms**: 
```
❌ Failed to load Firestore configurations: connection timeout
⚠️  Using default model 'gemini-2.5-flash' for all agents
```

**Causes**:
1. Credentials file missing/invalid
2. Network/firewall blocking Firestore
3. Project ID mismatch

**Solution**:
```bash
# 1. Verify credentials exist
ls -la credentials/service-account.json

# 2. Check environment variables
env | grep FIREBASE

# 3. Test connection
uv run python scripts/test_firestore.py
```

### Issue: Permission Denied

**Symptoms**:
```
❌ Permission denied: Missing or insufficient permissions
```

**Solution**: Check Firestore Security Rules allow read access for service account.

## Best Practices

### 1. Test Before Production

Always test model changes in development environment first:

```bash
# Development
1. Update Firestore (dev database if separate)
2. Restart local backend: make dev-backend
3. Test with sample queries
4. Verify output quality

# Production (if tests pass)
5. Update production Firestore
6. Restart production backend
7. Monitor logs and user feedback
```

### 2. Document Changes

Keep a changelog of model configuration changes:

```markdown
# Model Configuration Changelog

## 2025-01-04
- Changed hedge_fund_manager_agent: gemini-2.5-flash → gemini-2.5-pro
- Reason: Improve investment recommendation quality
- Result: 15% better user satisfaction scores

## 2025-01-01
- Changed all agents: gemini-1.5-pro → gemini-2.5-flash
- Reason: Cost optimization, new model has better price/performance
- Result: 40% cost reduction, similar quality
```

### 3. Monitor Performance

Track metrics after model changes:

- Response quality (user feedback)
- Response time (latency)
- Cost per analysis
- Error rates

### 4. Gradual Rollout

For major changes, use gradual rollout:

1. Change 1 agent (e.g., balance_sheet_agent) → test → verify
2. Change similar agents (financial team) → test → verify
3. Change all agents → monitor

### 5. Have Rollback Plan

Keep backup of working configurations:

```bash
# Before major change
uv run python scripts/export_config.py

# If issues occur
uv run python scripts/import_config.py
docker-compose restart stock-analysis-backend
```

## Advanced: Per-User Model Selection

**Future Enhancement**: Configure models per user or subscription tier

```
Premium users: gemini-2.5-pro for all agents
Standard users: gemini-2.5-flash for all agents
```

Implementation would require:
1. User tier stored in database
2. Multiple Firestore collections (e.g., `stock_agents_premium`, `stock_agents_standard`)
3. Load appropriate collection based on user tier

## References

- [Firebase Console](https://console.firebase.google.com/)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Google Gemini Models](https://ai.google.dev/models/gemini)
- [LiteLLM Provider List](https://docs.litellm.ai/docs/providers)
- [Plan Document](../plan.md) - Full implementation architecture
- [Setup Guide](./FIRESTORE_SETUP.md) - Initial configuration steps