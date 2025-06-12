#!/usr/bin/env python3
"""
Deployment script for Discord Chat Bot on Modal

This script helps deploy the Discord chat bot to Modal with all necessary steps.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if Modal CLI is installed
    try:
        subprocess.run(["modal", "--version"], capture_output=True, check=True)
        print("✅ Modal CLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Modal CLI not found. Please install it first:")
        print("   pip install modal")
        return False
    
    # Check if data file exists
    data_file = Path("data/WS1-C2.vtt")
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print("   Please ensure your transcript file is in the data directory")
        return False
    else:
        print(f"✅ Data file found: {data_file}")
    
    # Check if user is logged in to Modal
    try:
        result = subprocess.run(["modal", "profile", "current"], capture_output=True, text=True, check=True)
        print(f"✅ Logged in to Modal as: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("❌ Not logged in to Modal. Please run:")
        print("   modal setup")
        return False
    
    return True

def setup_secrets():
    """Help user set up Modal secrets"""
    print("\n🔑 Setting up Modal secrets...")
    print("Please ensure you have created the following Modal secrets:")
    print("\n1. OpenAI secret:")
    print("   modal secret create openai-secret OPENAI_API_KEY=<your-openai-key>")
    print("\n2. Discord secret:")
    print("   modal secret create discord-secret-2 \\")
    print("     DISCORD_BOT_TOKEN=<your-bot-token> \\")
    print("     DISCORD_CLIENT_ID=<your-client-id>")
    print("\n   Note: DISCORD_PUBLIC_KEY is not needed for message-based bots")
    
    response = input("\nHave you created these secrets? (y/n): ")
    return response.lower() == 'y'

def deploy_bot():
    """Deploy the bot to Modal"""
    print("\n🚀 Deploying Discord bot...")
    
    # Deploy the main application
    if not run_command(
        "modal deploy src/modal_discord_bot.py",
        "Deploying bot to Modal"
    ):
        return False
    
    print("\n✅ Setup completed!")
    print("\n🚀 To start the bot on Modal infrastructure:")
    print("   python start_bot.py")
    print("\n📝 After starting:")
    print("1. The bot will run continuously on Modal (not locally)")
    print("2. Mention the bot in any channel: @botname your question")
    print("3. The bot will create a thread for each question")
    print("4. Provide feedback in the thread when prompted")
    print("5. Check Modal dashboard for monitoring and logs")
    print("\n⚠️  Important: Use 'python start_bot.py' to deploy to Modal infrastructure")
    
    return True

def main():
    """Main deployment function"""
    print("🤖 Discord Chat Bot Deployment Script")
    print("=====================================")
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Setup secrets
    if not setup_secrets():
        print("\nPlease set up the required secrets first.")
        sys.exit(1)
    
    # Deploy
    if not deploy_bot():
        print("\nDeployment failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n🎉 Deployment successful!")

if __name__ == "__main__":
    main() 