"""
Populate Firestore with initial agent model configurations.

This script creates all 12 agent documents in the stock_agents collection
with their default model configurations.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()


def populate_firestore() -> None:
    """Populate Firestore with agent configurations."""
    
    # Initialize Firebase
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not cred_path:
        print("❌ Error: FIREBASE_CREDENTIALS_PATH not set in environment")
        sys.exit(1)
    
    if not os.path.exists(cred_path):
        print(f"❌ Error: Credentials file not found: {cred_path}")
        sys.exit(1)
    
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        print("✅ Connected to Firestore\n")
    except Exception as e:
        print(f"❌ Failed to initialize Firestore: {e}")
        sys.exit(1)
    
    # Agent configurations (11 agents + 1 root = 12 total)
    # Note: root_agent doesn't need config as it's not an LlmAgent
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
        'hedge_fund_manager_agent': 'gemini-2.5-pro',  # Premium for final report
    }
    
    # Populate Firestore
    print("📥 Populating Firestore with agent configurations...\n")
    
    success_count = 0
    for agent_name, model_name in agents.items():
        try:
            db.collection('stock_agents').document(agent_name).set({
                'llm_model': model_name
            })
            print(f'  ✓ {agent_name} → {model_name}')
            success_count += 1
        except Exception as e:
            print(f'  ✗ {agent_name}: {e}')
    
    print(f"\n✨ Firestore population complete!")
    print(f"   {success_count}/{len(agents)} agents configured successfully")


if __name__ == "__main__":
    populate_firestore()