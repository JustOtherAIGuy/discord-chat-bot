#!/usr/bin/env python3
"""
Script to stop the Discord bot running on Modal

This script helps stop the Discord bot service running on Modal infrastructure.
"""

import subprocess
import sys

def stop_persistent_bot():
    """Stop the persistent bot function"""
    print("🛑 Stopping persistent Discord bot...")
    try:
        # First, try to stop the specific app
        result = subprocess.run([
            "modal", "app", "stop", "discord-chat-bot"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Discord bot stopped successfully!")
            return True
        else:
            print(f"⚠️  App stop command returned: {result.stderr or result.stdout}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error stopping app: {e}")
        return False

def list_running_functions():
    """List all running functions to help identify what needs to be stopped"""
    print("\n🔍 Checking for running Modal functions...")
    try:
        result = subprocess.run([
            "modal", "app", "list"
        ], capture_output=True, text=True, check=True)
        
        print("Current Modal apps:")
        print(result.stdout)
        
        if "discord-chat-bot" in result.stdout:
            print("📍 Found discord-chat-bot app running")
            return True
        else:
            print("ℹ️  No discord-chat-bot app found running")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error listing apps: {e}")
        return False

def force_stop_containers():
    """Force stop any containers that might be running"""
    print("\n🔧 Attempting to stop any running containers...")
    try:
        # List containers
        result = subprocess.run([
            "modal", "container", "list"
        ], capture_output=True, text=True)
        
        if "discord-chat-bot" in result.stdout:
            print("Found running containers for discord-chat-bot")
            # Extract container IDs and stop them
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "discord-chat-bot" in line and "start_persistent_bot" in line:
                    # Extract container ID (usually first column)
                    parts = line.split()
                    if parts:
                        container_id = parts[0]
                        print(f"Stopping container: {container_id}")
                        subprocess.run([
                            "modal", "container", "stop", container_id
                        ], capture_output=True)
            return True
        else:
            print("No running containers found for discord-chat-bot")
            return False
            
    except Exception as e:
        print(f"⚠️  Error managing containers: {e}")
        return False

def main():
    print("⏹️  Stopping Discord Bot on Modal")
    print("=================================")
    
    # First, list what's running
    is_running = list_running_functions()
    
    if is_running:
        # Try to stop the app
        if stop_persistent_bot():
            print("\n✅ Bot stopped successfully!")
        else:
            print("\n⚠️  App stop command didn't fully work, trying container-level stop...")
            force_stop_containers()
    else:
        print("\n✅ No discord-chat-bot app appears to be running")
    
    # Final check
    print("\n🔍 Final status check...")
    list_running_functions()
    
    print("\n📝 Note: It may take a few moments for all containers to fully stop.")
    print("If the bot continues running, check the Modal dashboard.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 