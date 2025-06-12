#!/usr/bin/env python3
"""
Verification script to check Discord bot setup before deployment
"""

import subprocess
import sys
import os

def check_modal_app():
    """Check if the Modal app can be loaded"""
    print("1. Checking Modal app structure...")
    try:
        # Try to import the modal app
        sys.path.insert(0, 'src')
        from modal_discord_bot import app, discord_bot_runner
        print("   ✅ Modal app loaded successfully")
        print(f"   ✅ Found discord_bot_runner function")
        return True
    except Exception as e:
        print(f"   ❌ Error loading Modal app: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("\n2. Checking environment...")
    
    # Check for data file
    if os.path.exists("data/WS1-C2.vtt"):
        print("   ✅ Data file found")
    else:
        print("   ❌ Data file missing: data/WS1-C2.vtt")
        return False
    
    # Check for source files
    required_files = ["src/database.py", "src/vector_emb.py"]
    all_found = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} found")
        else:
            print(f"   ❌ {file} missing")
            all_found = False
    
    return all_found

def check_modal_deployment():
    """Do a dry run of Modal deployment"""
    print("\n3. Testing Modal deployment (dry run)...")
    try:
        # List functions in the app
        result = subprocess.run(
            ["modal", "app", "list", "discord-chat-bot"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Modal app 'discord-chat-bot' exists")
            if result.stdout:
                print("   Current deployments:")
                print(result.stdout)
        else:
            print("   ℹ️  Modal app 'discord-chat-bot' not yet deployed")
            print("   This is normal for first-time deployment")
        
        return True
    except Exception as e:
        print(f"   ❌ Error checking Modal deployment: {e}")
        return False

def main():
    print("🔍 Discord Bot Setup Verification")
    print("=================================")
    
    checks = [
        check_modal_app(),
        check_environment(),
        check_modal_deployment()
    ]
    
    if all(checks):
        print("\n✅ All checks passed!")
        print("\nNext steps:")
        print("1. Run: python start_bot.py")
        print("2. Monitor logs: modal app logs -f discord_bot_runner")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("- Ensure all required files are present")
        print("- Check that Modal secrets are configured")
        print("- Verify Modal CLI is authenticated")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 