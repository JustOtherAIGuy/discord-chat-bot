#!/usr/bin/env python3
"""
Script to start the Discord bot on Modal infrastructure

This script deploys and starts the Discord bot to run persistently on Modal.
"""

import subprocess
import sys
import time
import json

def deploy_bot():
    """Deploy the bot to Modal"""
    print("📦 Deploying Discord bot to Modal...")
    try:
        result = subprocess.run([
            "modal", "deploy", "src/minimal_discord_bot.py"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Bot deployed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def start_bot_persistent():
    """Start the Discord bot function"""
    print("\n🤖 Starting Discord bot...")
    print("The bot will run indefinitely with auto-restart on errors.")
    print("You can safely close this terminal - the bot will continue running on Modal.")
    
    try:
        # Start the Discord bot function
        print("Launching start_persistent_bot function...")
        subprocess.run([
            "modal", "run", "src/minimal_discord_bot.py::start_persistent_bot"
        ])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start bot: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Script interrupted.")
        print("Note: The bot may still be running on Modal.")
        return False
    
    return True

def check_bot_status():
    """Check if the bot is running by calling the health endpoint"""
    print("\n🔍 Checking bot status...")
    try:
        # Get the app info to find the health endpoint
        result = subprocess.run([
            "modal", "app", "list", "--json"
        ], capture_output=True, text=True, check=True)
        
        # Parse the output to find our app
        if "discord-chat-bot" in result.stdout:
            print("✅ Discord bot app is deployed on Modal")
            print("📊 Monitor your bot:")
            print("   1. Modal dashboard: https://modal.com/apps")
            print("   2. View logs: modal app logs discord-chat-bot")
            print("   3. Function logs: modal app logs -f start_discord_bot")
        else:
            print("⚠️  Bot app not found in Modal")
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def main():
    print("🚀 Starting Discord Bot on Modal")
    print("================================")
    
    # Deploy first
    if not deploy_bot():
        print("\n❌ Deployment failed. Please fix the errors above.")
        return 1
    
    # Check status
    check_bot_status()
    
    # Ask user if they want to start the Discord bot
    print("\n🤖 Ready to start the Discord bot.")
    print("This will run indefinitely on Modal (even after you close this terminal).")
    
    response = input("Start the bot now? (y/n): ").lower().strip()
    if response == 'y' or response == 'yes':
        if start_bot_persistent():
            print("\n✅ Bot started successfully!")
        else:
            print("\n❌ Failed to start bot.")
            return 1
    else:
        print("\nBot deployment completed but not started.")
        print("To start later, run:")
        print("  modal run src/minimal_discord_bot.py::start_persistent_bot")
    
    print("\n🔧 Useful commands:")
    print("  Stop bot: modal app stop discord-chat-bot")
    print("  View logs: modal app logs discord-chat-bot")
    print("  View function logs: modal app logs -f start_persistent_bot")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())