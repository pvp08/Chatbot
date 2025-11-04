#!/usr/bin/env python3
"""View chatbot conversations from MongoDB"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def view_conversations():
    """Display all chat conversations"""
    try:
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Get all sessions
        sessions = await db.chat_sessions.find({}).sort("last_interaction", -1).to_list(100)
        
        if not sessions:
            print("📭 No conversations found yet.")
            return
        
        print(f"💬 Found {len(sessions)} conversation(s)\n")
        print("=" * 80)
        
        for idx, session in enumerate(sessions, 1):
            session_id = session['id']
            created = datetime.fromisoformat(session['created_at'])
            last_interaction = datetime.fromisoformat(session['last_interaction'])
            
            print(f"\n🗨️  Conversation #{idx}")
            print(f"   Session ID: {session_id}")
            print(f"   Started: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Last Active: {last_interaction.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get messages for this session
            messages = await db.chat_messages.find(
                {"session_id": session_id}
            ).sort("timestamp", 1).to_list(1000)
            
            print(f"   Messages: {len(messages)}")
            print("\n   Conversation:")
            print("   " + "-" * 76)
            
            for msg in messages:
                timestamp = datetime.fromisoformat(msg['timestamp'])
                role = msg['role'].upper()
                content = msg['content']
                
                # Format message display
                if role == "USER":
                    print(f"\n   👤 USER [{timestamp.strftime('%H:%M:%S')}]:")
                    print(f"      {content}")
                else:
                    print(f"\n   🤖 ASSISTANT [{timestamp.strftime('%H:%M:%S')}]:")
                    # Wrap long messages
                    words = content.split()
                    line = "      "
                    for word in words:
                        if len(line) + len(word) > 76:
                            print(line)
                            line = "      " + word
                        else:
                            line += " " + word if line != "      " else word
                    if line.strip():
                        print(line)
            
            print("\n" + "=" * 80)
        
        # Statistics
        total_messages = await db.chat_messages.count_documents({})
        total_user_messages = await db.chat_messages.count_documents({"role": "user"})
        total_assistant_messages = await db.chat_messages.count_documents({"role": "assistant"})
        
        print(f"\n📊 Statistics:")
        print(f"   Total Conversations: {len(sessions)}")
        print(f"   Total Messages: {total_messages}")
        print(f"   User Messages: {total_user_messages}")
        print(f"   Assistant Messages: {total_assistant_messages}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(view_conversations())