#!/usr/bin/env python3
"""Test MongoDB connection script"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_connection():
    """Test MongoDB connection and collections"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        
        print(f"🔌 Connecting to MongoDB...")
        print(f"   URL: {mongo_url[:30]}...")
        print(f"   Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection with ping
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # List existing collections
        collections = await db.list_collection_names()
        print(f"\n📦 Existing collections: {collections if collections else 'None (database is new)'}")
        
        # Check each collection's document count
        if collections:
            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"   - {collection_name}: {count} documents")
        
        # Create indexes for better performance
        print(f"\n🔧 Setting up indexes...")
        
        # Index for chat_messages
        await db.chat_messages.create_index([("session_id", 1), ("timestamp", 1)])
        print("   ✓ chat_messages: session_id + timestamp")
        
        # Index for chat_sessions
        await db.chat_sessions.create_index([("id", 1)], unique=True)
        await db.chat_sessions.create_index([("last_interaction", -1)])
        print("   ✓ chat_sessions: id (unique) + last_interaction")
        
        # Index for status_checks
        await db.status_checks.create_index([("timestamp", -1)])
        print("   ✓ status_checks: timestamp")
        
        print(f"\n✨ Database '{db_name}' is ready to use!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("\nTroubleshooting:")
        print("1. Check your MONGO_URL in .env file")
        print("2. Verify your MongoDB password doesn't contain special characters")
        print("3. Make sure your IP is whitelisted in MongoDB Atlas")
        print("4. If using Atlas, check your cluster is running")

if __name__ == "__main__":
    asyncio.run(test_connection())