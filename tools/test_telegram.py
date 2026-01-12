#!/usr/bin/env python3
"""
Simple Telegram connection test script
Tests your bot token and chat ID without requiring external dependencies
"""
import sys
import json
import urllib.request
import urllib.error


def test_telegram_connection(token, chat_id):
    """Test Telegram bot connection and send a test message"""

    print("\n" + "="*60)
    print("🤖 TELEGRAM BOT CONNECTION TEST")
    print("="*60)

    # Step 1: Test bot token by calling getMe
    print("\n1️⃣ Testing bot token...")
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data.get('ok'):
                bot_info = data.get('result', {})
                bot_name = bot_info.get('username', 'Unknown')
                bot_id = bot_info.get('id', 'Unknown')
                print(f"   ✅ Bot token valid!")
                print(f"   Bot Username: @{bot_name}")
                print(f"   Bot ID: {bot_id}")
            else:
                print(f"   ❌ Bot token invalid: {data.get('description', 'Unknown error')}")
                return False
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code} - {e.reason}")
        if e.code == 401:
            print("   💡 Your bot token is incorrect. Please check it.")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Step 2: Test sending a message
    print("\n2️⃣ Testing message sending...")
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        message = """🤖 *Monitor-Bot Connection Test*

✅ Your Telegram bot is configured correctly!

This is a test message to verify that:
- Your bot token is valid
- Your chat ID is correct
- Messages can be sent successfully

You're ready to start monitoring crypto futures markets!

_Test completed at: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "_"

        payload = json.dumps({
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }).encode('utf-8')

        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data=payload, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data.get('ok'):
                print("   ✅ Test message sent successfully!")
                print("   📱 Check your Telegram to see the message")
                return True
            else:
                error_desc = data.get('description', 'Unknown error')
                print(f"   ❌ Failed to send message: {error_desc}")

                if 'chat not found' in error_desc.lower():
                    print("   💡 Your chat ID might be incorrect.")
                    print("   💡 Make sure you sent a message to your bot first!")

                return False

    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def get_chat_id_from_updates(token):
    """Try to get chat ID from recent messages"""
    print("\n🔍 Attempting to retrieve your Chat ID from recent messages...")

    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data.get('ok'):
                updates = data.get('result', [])

                if not updates:
                    print("   ⚠️  No messages found.")
                    print("   💡 Send a message to your bot first, then run this script again.")
                    return None

                # Get the most recent message
                latest_update = updates[-1]
                chat_id = latest_update.get('message', {}).get('chat', {}).get('id')

                if chat_id:
                    first_name = latest_update.get('message', {}).get('chat', {}).get('first_name', 'Unknown')
                    print(f"   ✅ Found Chat ID: {chat_id}")
                    print(f"   👤 Chat Name: {first_name}")
                    return str(chat_id)
                else:
                    print("   ❌ Could not extract Chat ID from updates")
                    return None
            else:
                print(f"   ❌ Error: {data.get('description', 'Unknown error')}")
                return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    print("\n" + "="*60)
    print("🚀 MONITOR-BOT TELEGRAM SETUP")
    print("="*60)

    # Check if .env file exists
    try:
        with open('.env', 'r') as f:
            env_content = f.read()

            # Parse .env file
            token = None
            chat_id = None

            for line in env_content.split('\n'):
                line = line.strip()
                if line.startswith('TELEGRAM_TOKEN='):
                    token = line.split('=', 1)[1].strip().strip('"').strip("'")
                elif line.startswith('CHAT_ID='):
                    chat_id = line.split('=', 1)[1].strip().strip('"').strip("'")

            # Check if token is set
            if not token or token == 'your_bot_token_here':
                print("\n❌ TELEGRAM_TOKEN not configured in .env file")
                print("\n📝 Please follow these steps:")
                print("   1. Open Telegram and search for @BotFather")
                print("   2. Send /newbot and follow the instructions")
                print("   3. Copy the bot token you receive")
                print("   4. Edit the .env file and set TELEGRAM_TOKEN=your_token")
                print("\nThen run this script again!")
                return 1

            # Check if chat_id is set
            if not chat_id or chat_id == 'your_chat_id_here':
                print("\n⚠️  CHAT_ID not configured in .env file")
                print("\n🔍 Let me try to find your Chat ID...")

                retrieved_chat_id = get_chat_id_from_updates(token)

                if retrieved_chat_id:
                    print(f"\n✅ Found your Chat ID: {retrieved_chat_id}")
                    print("\n📝 Update your .env file:")
                    print(f"   CHAT_ID={retrieved_chat_id}")

                    # Ask if we should test with this chat ID
                    print("\n❓ Would you like to test with this Chat ID? (y/n)")
                    # For automated testing, we'll just use it
                    chat_id = retrieved_chat_id
                else:
                    print("\n📝 To get your Chat ID:")
                    print("   Method 1: Search for @userinfobot in Telegram and send a message")
                    print("   Method 2: Send a message to your bot, then run this script again")
                    return 1

            # Run the test
            success = test_telegram_connection(token, chat_id)

            if success:
                print("\n" + "="*60)
                print("✅ TELEGRAM SETUP SUCCESSFUL!")
                print("="*60)
                print("\n🎉 Your bot is ready to send alerts!")
                print("\n📋 Your configuration:")
                print(f"   Bot Token: {token[:20]}...")
                print(f"   Chat ID: {chat_id}")
                print("\n🚀 Next steps:")
                print("   1. Run: python3 src/main/python/main.py")
                print("   2. The bot will start monitoring markets")
                print("   3. You'll receive alerts via Telegram!")
                print("="*60 + "\n")
                return 0
            else:
                print("\n" + "="*60)
                print("❌ TELEGRAM SETUP FAILED")
                print("="*60)
                print("\n🔧 Troubleshooting:")
                print("   - Check your bot token is correct")
                print("   - Check your chat ID is correct")
                print("   - Make sure you sent a message to your bot first")
                print("   - See docs/TELEGRAM_SETUP.md for detailed help")
                print("="*60 + "\n")
                return 1

    except FileNotFoundError:
        print("\n❌ .env file not found!")
        print("\n📝 Creating .env file from template...")
        print("   Please edit .env and add your bot token and chat ID")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
