# Firebase/Firestore Setup Guide

This guide explains how to set up Firebase and Firestore for dynamic AI model configuration in the Stock Analysis Agent backend.

## Overview

The Stock Analysis Agent uses Google Firestore to store and retrieve AI model configurations for each of the 11 specialized agents. This allows administrators to change which LLM model each agent uses via Firebase Console without requiring code changes or redeployment.

## Prerequisites

- Google Cloud Platform (GCP) account
- Firebase project: `stock-analysis-agent-a7bff`
- Access to Firebase Console: https://console.firebase.google.com/

## Step 1: Create Firebase Service Account

### 1.1 Access Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `stock-analysis-agent-a7bff`
3. Click on **Project Settings** (⚙️ icon)

### 1.2 Generate Service Account Key

1. Navigate to **Service Accounts** tab
2. Click **Generate New Private Key**
3. Click **Generate Key** to download the JSON file
4. The file will be named something like: `stock-analysis-agent-a7bff-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`

### 1.3 Rename and Store Credentials File

**For Development:**
```bash
# Create credentials directory
mkdir -p credentials

# Move and rename the downloaded file
mv ~/Downloads/stock-analysis-agent-*.json credentials/service-account.json

# Verify file exists
ls -la credentials/
```

**For Production (Docker):**
```bash
# Store in a secure location on your VPS
ssh user@158.247.216.21
mkdir -p /opt/stock-analysis/credentials
# Upload the file via scp or secure method
```

**⚠️ SECURITY WARNINGS:**
- ❌ **NEVER** commit this file to git
- ❌ **NEVER** share this file publicly
- ✅ Already added to `.gitignore` as `*service-account*.json`
- ✅ Store in secure location with restricted permissions

### 1.4 Set File Permissions (Linux/Mac)

```bash
chmod 600 credentials/service-account.json
```

## Step 2: Configure Environment Variables

The Firebase configuration uses environment variables defined in `.env` (development) and `.env.production` (production).

### 2.1 Development Environment

File: `.env` (root directory)

```bash
# Firebase/Firestore Configuration
FIREBASE_PROJECT_ID=stock-analysis-agent-a7bff
FIREBASE_CREDENTIALS_PATH=./credentials/service-account.json
```

### 2.2 Production Environment (Docker)

File: `.env.production`

```bash
# Firebase/Firestore Configuration
FIREBASE_PROJECT_ID=stock-analysis-agent-a7bff
FIREBASE_CREDENTIALS_PATH=/app/credentials/service-account.json
```

**Note**: In Docker, the path is absolute inside the container. Mount the credentials directory as a volume.

### 2.3 Verify Environment Variables

```bash
# Development
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Project ID:', os.getenv('FIREBASE_PROJECT_ID'))
print('Credentials Path:', os.getenv('FIREBASE_CREDENTIALS_PATH'))
"
```

## Step 3: Initialize Firestore Database

### 3.1 Enable Firestore

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: `stock-analysis-agent-a7bff`
3. Navigate to **Firestore Database** in left sidebar
4. Click **Create Database**
5. Select **Production mode** (or Test mode for development)
6. Choose location: `nam5 (us-central)` (or closest to your VPS)
7. Click **Enable**

### 3.2 Create Collection Structure

Navigate to **Firestore Database** → **Data** tab

**Create Collection:**
1. Click **Start Collection**
2. Collection ID: `stock_agents`
3. Click **Next**

**Add Initial Documents:**

For each of the 11 agents, create a document:

| Document ID | Field: llm_model | Type | Value |
|-------------|------------------|------|-------|
| `balance_sheet_agent` | llm_model | string | `gemini-2.5-flash` |
| `income_statement_agent` | llm_model | string | `gemini-2.5-flash` |
| `cash_flow_statement_agent` | llm_model | string | `gemini-2.5-flash` |
| `basic_financial_analyst_agent` | llm_model | string | `gemini-2.5-flash` |
| `senior_financial_advisor_agent` | llm_model | string | `gemini-2.5-flash` |
| `stock_researcher_agent` | llm_model | string | `gemini-2.5-flash` |
| `technical_analyst_agent` | llm_model | string | `gemini-2.5-flash` |
| `intrinsic_value_analyst_agent` | llm_model | string | `gemini-2.5-flash` |
| `growth_analyst_agent` | llm_model | string | `gemini-2.5-flash` |
| `senior_quantitative_advisor_agent` | llm_model | string | `gemini-2.5-flash` |
| `macro_economy_analyst_agent` | llm_model | string | `gemini-2.5-flash` |
| `hedge_fund_manager_agent` | llm_model | string | `gemini-2.5-pro` |

### 3.3 Automated Population Script (Optional)

Create a script to populate Firestore programmatically:

```python
# scripts/populate_firestore.py
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Agent configurations
agents = {
    'balance_sheet_agent': 'gemini-2.5-flash',
    'income_statement_agent': 'gemini-2.5-flash',
    'cash_flow_statement_agent': 'gemini-2.5-flash',
    'basic_financial_analyst_agent': 'gemini-2.5-flash',
    'senior_financial_advisor_agent': 'gemini-2.5-flash',
    'stock_researcher_agent': 'gemini-2.5-flash',
    'technical_analyst_agent': 'gemini-2.5-flash',
    'intrinsic_value_analyst_agent': 'gemini-2.5-flash',
    'growth_analyst_agent': 'gemini-2.5-flash',
    'senior_quantitative_advisor_agent': 'gemini-2.5-flash',
    'macro_economy_analyst_agent': 'gemini-2.5-flash',
    'hedge_fund_manager_agent': 'gemini-2.5-pro',
}

# Populate Firestore
for agent_name, model_name in agents.items():
    db.collection('stock_agents').document(agent_name).set({
        'llm_model': model_name
    })
    print(f'✅ Created {agent_name} → {model_name}')

print('\n✨ Firestore population complete!')
```

Run the script:
```bash
uv run python scripts/populate_firestore.py
```

## Step 4: Set Firestore Security Rules

Navigate to **Firestore Database** → **Rules** tab

**Recommended Rules for Production:**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read-only access to stock_agents collection
    match /stock_agents/{agent} {
      // Backend service account can read
      allow read: if request.auth != null;
      
      // Only admins can write (via Firebase Console)
      allow write: if false;
    }
  }
}
```

**For Development/Testing:**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /stock_agents/{agent} {
      allow read, write: if true; // WARNING: Development only!
    }
  }
}
```

## Step 5: Verify Setup

### 5.1 Test Firestore Connection

Create a test script:

```python
# scripts/test_firestore.py
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

try:
    # Initialize Firebase
    cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    # Test read
    docs = db.collection('stock_agents').limit(1).stream()
    for doc in docs:
        print(f'✅ Successfully connected to Firestore')
        print(f'   Sample: {doc.id} → {doc.to_dict()}')
        break
    else:
        print('⚠️  No documents found in stock_agents collection')
        
except Exception as e:
    print(f'❌ Error connecting to Firestore: {e}')
```

Run the test:
```bash
uv run python scripts/test_firestore.py
```

Expected output:
```
✅ Successfully connected to Firestore
   Sample: balance_sheet_agent → {'llm_model': 'gemini-2.5-flash'}
```

### 5.2 Test Backend Integration

After implementing the Firestore configuration service (Task 2), verify it loads configurations:

```bash
# Start backend
make dev-backend

# Check logs for:
# ✅ "Loaded 12 agent configurations from Firestore"
```

## Step 6: Docker Deployment Configuration

### 6.1 Update docker-compose.yml

Add volume mount for credentials:

```yaml
services:
  stock-analysis-backend:
    # ... existing config
    volumes:
      - ./credentials:/app/credentials:ro  # Read-only mount
    environment:
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - FIREBASE_CREDENTIALS_PATH=/app/credentials/service-account.json
```

### 6.2 Deploy to Production

```bash
# Copy credentials to VPS
scp credentials/service-account.json user@158.247.216.21:/opt/stock-analysis/credentials/

# SSH to VPS and restart services
ssh user@158.247.216.21
cd /opt/stock-analysis
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f stock-analysis-backend | grep Firestore
```

## Troubleshooting

### Issue: "GOOGLE_APPLICATION_CREDENTIALS not found"

**Solution**: Ensure `FIREBASE_CREDENTIALS_PATH` is set correctly in `.env`

```bash
# Check if file exists
ls -la $(python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('FIREBASE_CREDENTIALS_PATH'))")
```

### Issue: "Permission denied" when accessing credentials

**Solution**: Set proper file permissions

```bash
chmod 600 credentials/service-account.json
# For Docker on Linux
sudo chown 1000:1000 credentials/service-account.json
```

### Issue: "Firestore connection timeout"

**Possible causes:**
1. Network/firewall blocking Firestore access
2. Invalid project ID
3. Service account permissions insufficient

**Solution**: 
```bash
# Test network connectivity
curl https://firestore.googleapis.com/

# Verify project ID
grep FIREBASE_PROJECT_ID .env

# Check service account has Firestore permissions in GCP Console
```

### Issue: "Document not found" errors

**Solution**: Ensure all 12 agent documents exist in Firestore

```python
# Run verification script
uv run python scripts/verify_agents.py
```

## Security Best Practices

1. ✅ **Store credentials outside git repository**
   - Use `.gitignore` to exclude `*service-account*.json`
   - Use environment variables for paths

2. ✅ **Restrict service account permissions**
   - Only grant **Firestore Read** permission to backend
   - Use principle of least privilege

3. ✅ **Use different credentials for environments**
   - Separate service accounts for dev/staging/prod
   - Different Firebase projects if possible

4. ✅ **Monitor access logs**
   - Enable Firestore audit logs in GCP
   - Set up alerts for unusual access patterns

5. ✅ **Rotate credentials regularly**
   - Generate new service account keys periodically
   - Revoke old keys after deployment

## Next Steps

After completing this setup:
1. ✅ Verify all 12 agent documents exist in Firestore
2. ✅ Test connection with test script
3. ➡️ Proceed to **Task 2**: Implement Firestore Client Initialization
4. ➡️ See [`guide/MODEL_CONFIGURATION.md`](./MODEL_CONFIGURATION.md) for changing models

## References

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Plan Document](../plan.md) - Full implementation plan