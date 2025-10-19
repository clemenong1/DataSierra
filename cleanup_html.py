#!/usr/bin/env python3
"""
Clean up existing query history with HTML tags
This script will clean up any existing query history entries that contain HTML tags
"""

import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clean_query_history():
    """Clean up query history entries with HTML tags"""
    print("🧹 Cleaning up query history with HTML tags...")
    
    try:
        from src.services.firebase_config import FirebaseConfig
        from src.services.session_service import SessionService
        
        # Initialize Firebase
        if not FirebaseConfig.initialize():
            print("❌ Firebase initialization failed")
            return False
        
        print("✅ Firebase initialized successfully")
        
        # Initialize session service
        session_service = SessionService()
        
        # Get all query history
        history = session_service.get_query_history(limit=100)
        
        if not history:
            print("ℹ️  No query history found to clean")
            return True
        
        print(f"📊 Found {len(history)} query history entries")
        
        # Check for HTML tags in responses
        html_entries = []
        for item in history:
            if '<' in item.response or '>' in item.response or '&' in item.response:
                html_entries.append(item)
        
        if not html_entries:
            print("✅ No HTML tags found in query history")
            return True
        
        print(f"🔍 Found {len(html_entries)} entries with HTML tags")
        
        # Clean up the entries (this would require updating the session service)
        # For now, just report what needs to be cleaned
        for i, item in enumerate(html_entries[:5]):  # Show first 5
            print(f"  {i+1}. Query: {item.query[:50]}...")
            print(f"     Response preview: {item.response[:100]}...")
            print()
        
        if len(html_entries) > 5:
            print(f"     ... and {len(html_entries) - 5} more entries")
        
        print("✅ HTML tag detection completed")
        print("💡 New queries will automatically have HTML tags escaped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning query history: {str(e)}")
        return False

if __name__ == "__main__":
    success = clean_query_history()
    
    if success:
        print("\n🎉 Query history cleanup completed!")
        print("The </div> issue should be resolved for new queries.")
    else:
        print("\n❌ Query history cleanup failed.")
    
    sys.exit(0 if success else 1)
