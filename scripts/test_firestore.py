"""
Test Firestore connection and configuration loading.

This script verifies that Firestore is properly configured and
agent configurations can be loaded successfully.
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


def test_firestore_connection() -> bool:
    """Test basic Firestore connectivity."""
    
    print("🔍 Testing Firestore Connection\n")
    print("=" * 60)
    
    # Check environment variables
    print("\n1️⃣ Checking Environment Variables...")
    
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    
    if not project_id:
        print("   ❌ FIREBASE_PROJECT_ID not set")
        return False
    else:
        print(f"   ✓ FIREBASE_PROJECT_ID: {project_id}")
    
    if not cred_path:
        print("   ❌ FIREBASE_CREDENTIALS_PATH not set")
        return False
    else:
        print(f"   ✓ FIREBASE_CREDENTIALS_PATH: {cred_path}")
    
    # Check credentials file exists
    print("\n2️⃣ Checking Credentials File...")
    
    if not os.path.exists(cred_path):
        print(f"   ❌ File not found: {cred_path}")
        return False
    else:
        print(f"   ✓ File exists: {cred_path}")
        # Check file size
        size = os.path.getsize(cred_path)
        print(f"   ✓ File size: {size} bytes")
    
    # Initialize Firebase
    print("\n3️⃣ Initializing Firebase Admin SDK...")
    
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("   ✓ Firebase initialized successfully")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    # Test Firestore read
    print("\n4️⃣ Testing Firestore Read Access...")
    
    try:
        # Try to read one document
        docs = list(db.collection('stock_agents').limit(1).stream())
        
        if docs:
            doc = docs[0]
            print(f"   ✓ Successfully read document: {doc.id}")
            print(f"   ✓ Data: {doc.to_dict()}")
        else:
            print("   ⚠️  Collection exists but no documents found")
            print("   💡 Run: uv run python scripts/populate_firestore.py")
            return False
            
    except Exception as e:
        print(f"   ❌ Read failed: {e}")
        return False
    
    # Load all agents
    print("\n5️⃣ Loading All Agent Configurations...")
    
    try:
        docs = db.collection('stock_agents').stream()
        configs = {}
        
        for doc in docs:
            agent_name = doc.id
            data = doc.to_dict()
            llm_model = data.get('llm_model', 'N/A')
            configs[agent_name] = llm_model
            print(f"   ✓ {agent_name}: {llm_model}")
        
        print(f"\n   📊 Total configurations loaded: {len(configs)}")
        
        # Expected agents
        expected = {
            'balance_sheet_agent',
            'income_statement_agent',
            'cash_flow_statement_agent',
            'basic_financial_analyst_agent',
            'senior_financial_advisor_agent',
            'stock_researcher_agent',
            'technical_analyst_agent',
            'intrinsic_value_analyst_agent',
            'growth_analyst_agent',
            'senior_quantitative_advisor_agent',
            'macro_economy_analyst_agent',
            'hedge_fund_manager_agent',
        }
        
        missing = expected - set(configs.keys())
        if missing:
            print(f"\n   ⚠️  Missing agents: {', '.join(missing)}")
            print("   💡 Run: uv run python scripts/populate_firestore.py")
            return False
        else:
            print("   ✓ All 12 expected agents configured")
            
    except Exception as e:
        print(f"   ❌ Failed to load configs: {e}")
        return False
    
    return True


def test_backend_integration() -> bool:
    """Test backend FirestoreConfig integration."""
    
    print("\n" + "=" * 60)
    print("\n6️⃣ Testing Backend Integration...")
    
    try:
        from app.sub_agents.utils.firestore_config import FirestoreConfig
        
        # Load configs
        FirestoreConfig.load_configs()
        
        # Get all configs
        configs = FirestoreConfig.get_all_configs()
        print(f"   ✓ Backend loaded {len(configs)} configurations")
        
        # Test specific lookups
        test_agents = [
            'balance_sheet_agent',
            'hedge_fund_manager_agent',
            'unknown_agent_test'
        ]
        
        print("\n   Testing model lookups:")
        for agent in test_agents:
            model = FirestoreConfig.get_model(agent)
            status = "✓" if agent != 'unknown_agent_test' else "⚠️"
            print(f"   {status} {agent}: {model}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Backend integration test failed: {e}")
        return False


def main() -> None:
    """Run all tests."""
    
    print("\n" + "🔥" * 30)
    print("FIRESTORE CONFIGURATION TEST")
    print("🔥" * 30)
    
    # Test Firestore connection
    firestore_ok = test_firestore_connection()
    
    # Test backend integration
    backend_ok = test_backend_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("\n📊 TEST SUMMARY\n")
    
    print(f"   Firestore Connection: {'✅ PASS' if firestore_ok else '❌ FAIL'}")
    print(f"   Backend Integration:  {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if firestore_ok and backend_ok:
        print("\n🎉 All tests passed! Firestore is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Start backend: make dev-backend")
        print("   2. Check logs for: '✅ Successfully loaded 12 agent configurations'")
        print("   3. Try stock analysis: 'Analyze AAPL stock'")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check errors above.")
        print("\n💡 Troubleshooting:")
        print("   1. Verify credentials file exists and is valid")
        print("   2. Check environment variables in .env")
        print("   3. See guide/FIRESTORE_SETUP.md for detailed setup")
        sys.exit(1)


if __name__ == "__main__":
    main()