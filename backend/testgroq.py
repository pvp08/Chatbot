#!/usr/bin/env python3
"""
Test script to debug Groq API connection
"""
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY not found in .env file")
    exit(1)

print(f"✅ Found API key: {GROQ_API_KEY[:10]}...")
print()

# Test the API
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one sentence."}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

print("🧪 Testing Groq API...")
print(f"URL: {url}")
print(f"Model: llama3-8b-8192")
print()

try:
    response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS!")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")