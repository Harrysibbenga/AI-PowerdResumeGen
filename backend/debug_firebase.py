#!/usr/bin/env python3
"""
Firebase Configuration Debug Script
Run this script to diagnose Firebase setup issues
"""

import os
import sys
import json
from pathlib import Path

def main():
    print("🔍 Firebase Configuration Diagnostic")
    print("=" * 60)
    
    # 1. Check current working directory
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📄 Script location: {__file__}")
    print(f"📂 Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print()
    
    # 2. Check environment variables
    print("🌍 Environment Variables:")
    env_vars = [
        'FIREBASE_SERVICE_ACCOUNT_PATH',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'PYTHONPATH'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        print(f"   {var}: {value if value else 'Not set'}")
    print()
    
    # 3. Check .env file
    print("📋 Checking .env file:")
    env_files = ['.env', '../.env', '../../.env']
    
    for env_file in env_files:
        abs_path = os.path.abspath(env_file)
        if os.path.exists(abs_path):
            print(f"   ✓ Found .env at: {abs_path}")
            try:
                with open(abs_path, 'r') as f:
                    content = f.read()
                    if 'FIREBASE_SERVICE_ACCOUNT_PATH' in content:
                        lines = [line for line in content.split('\n') if 'FIREBASE_SERVICE_ACCOUNT_PATH' in line and not line.strip().startswith('#')]
                        for line in lines:
                            print(f"     {line.strip()}")
                    else:
                        print("     ⚠️  FIREBASE_SERVICE_ACCOUNT_PATH not found in .env")
            except Exception as e:
                print(f"     ❌ Error reading .env: {e}")
        else:
            print(f"   ✗ No .env at: {abs_path}")
    print()
    
    # 4. Check common Firebase service account locations
    print("🔥 Checking Firebase service account locations:")
    possible_paths = [
        "./firebase/serviceAccount.json",
        "../firebase/serviceAccount.json",
        "../../firebase/serviceAccount.json",
        "./serviceAccount.json",
        "../serviceAccount.json",
        "./firebase-adminsdk.json",
        "./config/serviceAccount.json",
        # Add paths based on your project structure
        "./backend/firebase/serviceAccount.json",
        "../backend/firebase/serviceAccount.json",
    ]
    
    found_files = []
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            print(f"   ✓ {abs_path}")
            found_files.append(abs_path)
            
            # Validate the JSON file
            try:
                with open(abs_path, 'r') as f:
                    data = json.load(f)
                    
                    # Check required fields
                    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                    missing = [field for field in required_fields if field not in data]
                    
                    if missing:
                        print(f"     ⚠️  Missing fields: {missing}")
                    else:
                        print(f"     ✓ Valid service account file")
                        print(f"     📊 Project ID: {data.get('project_id', 'Unknown')}")
                        print(f"     📧 Client Email: {data.get('client_email', 'Unknown')}")
                        
                        if data.get('type') != 'service_account':
                            print(f"     ⚠️  Type is '{data.get('type')}', should be 'service_account'")
                            
            except json.JSONDecodeError as e:
                print(f"     ❌ Invalid JSON: {e}")
            except Exception as e:
                print(f"     ❌ Error reading file: {e}")
        else:
            print(f"   ✗ {abs_path}")
    print()
    
    # 5. Check Firebase directory structure
    print("📁 Checking Firebase directories:")
    firebase_dirs = ["./firebase", "../firebase", "../../firebase", "./backend/firebase"]
    
    for dir_path in firebase_dirs:
        abs_dir = os.path.abspath(dir_path)
        if os.path.exists(abs_dir):
            print(f"   ✓ {abs_dir}")
            try:
                files = [f for f in os.listdir(abs_dir) if f.endswith('.json')]
                if files:
                    print(f"     📄 JSON files: {files}")
                else:
                    print(f"     ⚠️  No JSON files found")
            except Exception as e:
                print(f"     ❌ Error reading directory: {e}")
        else:
            print(f"   ✗ {abs_dir}")
    print()
    
    # 6. Recommendations
    print("💡 Recommendations:")
    
    if not found_files:
        print("   ❌ No Firebase service account file found!")
        print("   📋 To fix this:")
        print("   1. Download serviceAccount.json from Firebase Console:")
        print("      - Go to https://console.firebase.google.com")
        print("      - Select your project")
        print("      - Go to Project Settings > Service Accounts")
        print("      - Click 'Generate new private key'")
        print("   2. Place the file in one of these locations:")
        print("      - ./firebase/serviceAccount.json")
        print("      - ./serviceAccount.json")
        print("   3. Update your .env file:")
        print("      FIREBASE_SERVICE_ACCOUNT_PATH=./firebase/serviceAccount.json")
    else:
        print(f"   ✓ Found {len(found_files)} service account file(s)")
        print("   📋 To use the correct file:")
        print(f"   1. Set in .env: FIREBASE_SERVICE_ACCOUNT_PATH={found_files[0]}")
        print("   2. Or set environment variable:")
        print(f"      export FIREBASE_SERVICE_ACCOUNT_PATH='{found_files[0]}'")
    
    print()
    print("🚀 Test Firebase initialization:")
    print("   Run this to test: python -c \"from firebase_init import initialize_firebase_from_env; initialize_firebase_from_env()\"")
    print()
    
    # 7. Try to load settings
    try:
        print("⚙️ Checking app settings:")
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from app.core.config import settings
        print(f"   📋 Settings loaded successfully")
        print(f"   🔥 Firebase path from settings: {settings.FIREBASE_SERVICE_ACCOUNT_PATH}")
        
        if settings.FIREBASE_SERVICE_ACCOUNT_PATH:
            abs_settings_path = os.path.abspath(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
            if os.path.exists(abs_settings_path):
                print(f"   ✓ Settings path exists: {abs_settings_path}")
            else:
                print(f"   ❌ Settings path does not exist: {abs_settings_path}")
        else:
            print(f"   ⚠️  Firebase path not set in settings")
            
    except Exception as e:
        print(f"   ❌ Error loading settings: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Diagnostic complete!")

if __name__ == "__main__":
    main()