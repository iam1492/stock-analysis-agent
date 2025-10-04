# Next.js Frontend Deployment Guide - Vercel

## Overview
This guide explains how to deploy your Next.js frontend to Vercel and configure it to connect to your deployed ADK agent backend. The frontend automatically detects the deployment environment and configures endpoints accordingly.

## Prerequisites

### 1. Vercel Account Setup
1. Go to [vercel.com](https://vercel.com) and sign up/sign in
2. Connect your GitHub/GitLab/Bitbucket account


### 2. Backend Deployment
Your Next.js frontend needs a backend to connect to:
- **Agent Engine** - Follow the [ADK Deployment Guide](./ADK_DEPLOYMENT_GUIDE.md)


## Environment Variables by Deployment Type

The frontend automatically detects which backend type to use based on available environment variables. Here's what you need for each deployment scenario:

### 🚀 Agent Engine Backend (Recommended)

**Required Variables:**
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=stock-adk-vertex-ai
REASONING_ENGINE_ID=7116061245198827520
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64=ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic3RvY2stYWRrLXZlcnRleC1haSIsCiAgInByaXZhdGVfa2V5X2lkIjogImE4OGI5MjBjYWU0NDliMDAzYmFhODQyZDI1YTgzODAwYTAwM2MyZjciLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQ3ptVmxZK2FuUEtuTTFcbkhTSUpwbXFJaVlJUkZtSkc4UVAydjA4ME1mVThhR3cydnk1emlySHl3Um5tVTIzQVJMWk5mVDBJb0NzaTdxaWVcbjVFK2gyWjBrbVpicTZCZjc5Z1RXckduclRUcTFkazM1djNvS0VmRnBCTEpXTWtrUkEzUWQ2SkRrQjIvdE03VjNcbm1MZmF2LzFxSnZsM3IycVZhSjMyczhsMXZpUVNJZVJkcEhmREtrNGxnc1dBMmFrVVZrd3JtMVVuc0hicDFERURcbkZaRFh6RjhXclRaV25QTVRpcXBmNWtrSklUY2EyZ2R2VEl3UVlWN05XNGFBcXI3OUR1dnZtOS8wSmZ1MVQyQ0lcbitFY2lRVS9kR2ovR00xZzZCUTVVK2pMOVdRWC9LYkN4Y3ZJRTFiQ1B6Q3VDRndSYnhPc0hWTkx5dlA3Tmo3VHBcbnlMbHQvNXpQQWdNQkFBRUNnZ0VBSlR1VTJNdkZadVBiaDNiWE1CMzJkd0RlM0pFQjVjZ2dkTDU3ZW93aTFaZW1cblc0RXQ3Wmtpdy90QlZjMFU4eWVyall2NW83aWt5TFNtYzI1TWpmYXh5NzBsbXVScjJIbkx6ZjluWS9jYVJUVlZcbi9BRTBtVExZRTlmNzZyKzVBeFJ1dGFhWnB4UmRvVlMzZWFoSThVb2RESzB3eVoydG9IVFVUcWsrQ2pGVmhBWjFcbjlhOUxaeEViZllhZkF2S2ZuejlKMTQraGEwTG9iSW1KY1RLN1RmaFBDd0RFcmZOU1FPR0dPQVVkdGU4ZzVXUUtcbjlBTVpCVHlZZHcrRHBGRjViQzdsQmV3aFJJekJOZ2NMYTN4OEZFNy9NYkEzZEtPSlhrbUdqZTFrMXhDWkNjck5cbk9yUXZpWGhWR1A0bUlwS1hOOWd4aXlkU2R5aDNLT3IxUTNLUFNJWjE1UUtCZ1FEMThWMUxZUmRLQTBycGMvdnNcblFuK2Jmd0l5NTVuSkY5WjVSZW4va3lnc0ZYaGZoYllDUkl1MlV3eEtDRld4YVJlNVNzOWtKRHRrY2xqK29aelpcbmplcEN0SC9SNlI5L0IycEYzaXg4Sktock5UdWJVNWVPTUFTYUZ3TEhsOVc5czIxaWR4QWpiblhLNGF0YzdFdmhcbnNWOFBpRWtzQUNvY0llSUJoWnU3QnRkRjh3S0JnUUM2OFhnTzBuOE1DUlNmdDFSTkR6V2dBdGJ2eXZwYkNiZThcbjhjUFhSY3hOLy9BbjN3WTcyQTNGVnVlV0lGU2NzMHU1ZnNCc0R5QjBFR0JPQW8wRkxpdFJZZWNpQXkvQml0V0tcbm5pTEpTZzY5N0FybWFzVTBUWndWb0cxem56ZmtoejRMR2o0aXJXYjdDQitaUWVkVHpFY2pJeWVMdXZaVUtOckxcbjFOc0xad280dFFLQmdHMUtjNzNpaUZuZ2VyS2hVdXJiWmg5d1lrYkN1b2t0S2FhOGxjNTMwMXM3czBFbmh3a2NcbjhzVHp4THRGVnVjK24wYzg0a3BLKzRXWWRzbTRnWjMvdllFaytzUUtCM0FJbUlZeHc2enJFVmlLMEZFbTVXdFBcbkZVeHdPMUQ4dlFQT3J5WVphTGVHQjV3L2lrb0J5M3FndW5DSmpKS2NCQnA2U0JlTEN2Z2lneGxYQW9HQkFKZ2lcblpvZjVlZmI3ZE5NOXlOY2xaNGllaHZpQ2dSZVJZdnZhN0h2R2k2dDJlNlNXOVdYQ1FBSzI1S1RpRHJtdm1CS1Bcbk9sMDJPano2RHNXdGdjSVRmcUV1UVlFR2d0akkrVnRqc2YrSnkxRjRSSzZiZVgxRkk1N2QvZlM0UUM0MGVhTmpcbmFlbWlvRW51cEhoK2o1azhoeS9yTGdXaTAxQk9KekQyT29TZkNFeDVBb0dCQU9JTlhaWXVlNlV1K1Jlc3JNZTZcbnRKallMT2d2a3ljV2ZnU1R2eGhPd3VCaUc3Q3ozQS9sZ0tjaHZEeWVwTzI0STFBTzlxb0VvTHdrVTFDSjllblJcbjF3Tlk5bDNHamZJRk1NOUdMcDNoS3dpVk1jVk9idUJzdzVjdkZLakpkcjZMZzAyTmhqYWpubG9KUjBGTzU3WlBcbmdPUkRtY0E2Mk8zK1MyVEZtdTVZcFN1QlxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImFkay1mZS1zZXJ2aWNlQHN0b2NrLWFkay12ZXJ0ZXgtYWkuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA5MzQ1MTI2Njk3OTc1Mjk3Mjk0IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9hZGstZmUtc2VydmljZSU0MHN0b2NrLWFkay12ZXJ0ZXgtYWkuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K
ADK_APP_NAME=stock-analysis-agent
AGENT_ENGINE_ENDPOINT=https://us-central1-aiplatform.googleapis.com/v1/projects/stock-adk-vertex-ai/locations/us-central1/reasoningEngines/7116061245198827520
GOOGLE_CLOUD_LOCATION=us-central1
```

**How to get these values:**
1. **GOOGLE_CLOUD_PROJECT**: Your Google Cloud project ID
2. **REASONING_ENGINE_ID**: From your ADK deployment output (e.g., `projects/123/locations/us-central1/reasoningEngines/abc123` → use `abc123`)
3. **GOOGLE_CLOUD_LOCATION**: Region where you deployed your agent (default: `us-central1`)
4. **GOOGLE_SERVICE_ACCOUNT_KEY_BASE64**: Base64-encoded service account key (see setup instructions below)

## Service Account Setup for Agent Engine

If you're using Agent Engine backend, you need to create a Google Cloud service account and configure authentication. This is required for the frontend to authenticate with Google Cloud's Vertex AI API.

### Step 1: Create Service Account

1. **Go to Google Cloud Console:**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com)
   - Select your project (the same one where you deployed your ADK agent)

2. **Navigate to Service Accounts:**
   - Go to **IAM & Admin** → **Service Accounts**
   - Click **"Create Service Account"**

3. **Configure Service Account:**
   - **Service account name**: `agent-engine-frontend` (or any descriptive name)
   - **Service account ID**: Will be auto-generated
   - **Description**: `Service account for frontend to access Agent Engine`
   - Click **"Create and Continue"**

4. **Add Required Roles:**
   Add these roles to your service account:
   - **Vertex AI User** (`roles/aiplatform.user`) - Required for Agent Engine API access
   - **Service Account Token Creator** (`roles/iam.serviceAccountTokenCreator`) - Required for token generation
   
   Click **"Continue"** then **"Done"**

### Step 2: Generate Service Account Key

1. **Access Service Account:**
   - In the Service Accounts list, click on the service account you just created
   - Go to the **"Keys"** tab

2. **Create New Key:**
   - Click **"Add Key"** → **"Create new key"**
   - Select **"JSON"** as the key type
   - Click **"Create"**

3. **Download Key:**
   - The JSON key file will be automatically downloaded to your computer
   - **Important**: Store this file securely and never commit it to version control

### Step 3: Convert JSON Key to Base64

You need to convert the JSON key to base64 for safe storage in environment variables.

**Option A: Using Terminal/Command Line (Recommended)**

```bash
# On macOS/Linux
cat path/to/your-service-account-key.json | base64

# On Windows (PowerShell)
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content path/to/your-service-account-key.json -Raw)))
```

**Option B: Using Node.js**

```javascript
const fs = require('fs');
const keyFile = fs.readFileSync('path/to/your-service-account-key.json', 'utf8');
const base64Key = Buffer.from(keyFile).toString('base64');
console.log(base64Key);
```

**Option C: Using Online Tool**

1. Go to [base64encode.org](https://www.base64encode.org/)
2. Copy the entire contents of your JSON key file
3. Paste it into the encoder
4. Copy the base64 output


**For Vercel Production:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add a new environment variable:
   - **Name**: `GOOGLE_SERVICE_ACCOUNT_KEY_BASE64`
   - **Value**: The base64 string you generated
   - **Environments**: Select Production, Preview, and Development


## Deploy via Vercel Dashboard (Recommended)

1. **Import Your Repository:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository
   - Select the `nextjs` folder as the root directory

2. **Configure Build Settings:**
   - **Framework Preset**: Next.js
   - **Root Directory**: `nextjs`
   - **Build Command**: `npm run build`
   - **Output Directory**: Leave empty (uses default)

3. **Set Environment Variables:**
   - In project settings, go to "Environment Variables"
   - Add your variables based on your backend type (see sections above)
   - Set for "Production", "Preview", and "Development" as needed

4. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy your app


 `bash
  git rm -r --cached .
  git add .
  git commit -m "fix: Git 캐시 정리 및 파일 재추적"
  git push
  `

