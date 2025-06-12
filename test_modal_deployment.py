#!/usr/bin/env python3
"""Test script to verify Modal deployment and configuration"""

import subprocess
import sys

def test_modal_cli():
    """Test if Modal CLI is installed and authenticated"""
    print("1. Testing Modal CLI...")
    try:
        result = subprocess.run(["modal", "--version"], capture_output=True, text=True, check=True)
        print(f"   ✅ Modal CLI version: {result.stdout.strip()}")
    except:
        print("   ❌ Modal CLI not found. Run: pip install modal")
        return False
    
    try:
        result = subprocess.run(["modal", "profile", "current"], capture_output=True, text=True, check=True)
        print(f"   ✅ Authenticated as: {result.stdout.strip()}")
    except:
        print("   ❌ Not authenticated. Run: modal setup")
        return False
    
    return True

def test_secrets():
    """Test if required secrets exist"""
    print("\n2. Testing Modal secrets...")
    secrets_to_check = ["openai-secret", "discord-secret-2"]
    
    result = subprocess.run(["modal", "secret", "list"], capture_output=True, text=True)
    existing_secrets = result.stdout
    
    all_good = True
    for secret in secrets_to_check:
        if secret in existing_secrets:
            print(f"   ✅ {secret} exists")
        else:
            print(f"   ❌ {secret} missing")
            all_good = False
    
    return all_good

def test_simple_function():
    """Test deploying a simple Modal function"""
    print("\n3. Testing simple Modal deployment...")
    
    test_code = '''
import modal
app = modal.App("test-deployment")

@app.function()
def hello():
    return "Modal is working!"

@app.local_entrypoint()
def main():
    result = hello.remote()
    print(f"Result: {result}")
'''
    
    with open("test_modal_simple.py", "w") as f:
        f.write(test_code)
    
    try:
        result = subprocess.run(["modal", "run", "test_modal_simple.py"], 
                              capture_output=True, text=True, check=True)
        if "Modal is working!" in result.stdout:
            print("   ✅ Simple Modal function works")
            # Clean up
            subprocess.run(["rm", "test_modal_simple.py"])
            return True
        else:
            print("   ❌ Simple Modal function failed")
            print(f"   Output: {result.stdout}")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🔍 Modal Deployment Diagnostics")
    print("===============================")
    
    tests = [
        test_modal_cli(),
        test_secrets(),
        test_simple_function()
    ]
    
    if all(tests):
        print("\n✅ All tests passed! Ready to deploy Discord bot.")
        print("\nNext steps:")
        print("1. Run: python deploy.py")
        print("2. Run: python start_bot.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 