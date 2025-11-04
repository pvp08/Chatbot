from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configure Groq (FREE & FAST!)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-8b-instant')  # Free, fast, excellent quality

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


# Chat Models
class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessageCreate(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    user_message: ChatMessage
    assistant_message: ChatMessage


class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_interaction: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# System prompt for the chatbot
SYSTEM_PROMPT = """You are a professional AI assistant for Pinnacle Sync, an IT company specializing in:
1. IT Recruiting Services - We help IT companies find top-tier technical talent including software engineers, DevOps specialists, data scientists, and technology leaders.
2. Software Solutions - We provide custom software development, web applications, mobile apps, cloud solutions, and enterprise software systems.

Your role is to:
- Answer questions about our services professionally and formally
- Help potential clients understand how we can assist them
- Provide information about IT recruiting and software development
- Guide users to the right department or service
- Be helpful, knowledgeable, and maintain a professional tone

Key Points:
- Our IT recruiting services cover full-time, contract, and contract-to-hire positions
- We specialize in technical roles across all levels (junior to executive)
- Our software solutions are tailored to business needs with modern technology stacks
- We offer consultation services to help clients define their technology needs

Always be professional, concise, and helpful. If you don't know something specific about the company, acknowledge it and offer to have someone contact them."""


async def query_groq(messages: list) -> str:
    """Query Groq API (OpenAI-compatible)"""
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY not configured. Get one free at https://console.groq.com"
        )
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 1,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        try:
            response = await http_client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content']
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logging.error(f"Groq API HTTP error: {e.response.status_code} - {error_detail}")
            raise HTTPException(
                status_code=500, 
                detail=f"AI service error: {e.response.status_code}"
            )
        except Exception as e:
            logging.error(f"Groq API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


# Routes
@api_router.get("/")
async def root():
    return {
        "message": "Pinnacle Sync Chatbot API",
        "status": "running",
        "ai_provider": "Groq (FREE & FAST)",
        "model": GROQ_MODEL
    }


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# Chat endpoints
@api_router.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(input: ChatMessageCreate):
    """Send a message and get AI response using FREE Groq"""
    try:
        # Create or use existing session
        session_id = input.session_id or str(uuid.uuid4())
        
        # Create user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=input.message
        )
        
        # Save user message to database
        user_doc = user_message.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        await db.chat_messages.insert_one(user_doc)
        
        # Get conversation history for context (last 10 messages)
        history_docs = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).limit(10).to_list(100)
        
        # Build messages array for Groq (OpenAI format)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation history
        for msg in history_docs:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Generate response using Groq
        logging.info(f"Sending message to Groq for session {session_id}")
        ai_response = await query_groq(messages)
        logging.info(f"Received response: {ai_response[:100]}...")
        
        # Create assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_response
        )
        
        # Save assistant message to database
        assistant_doc = assistant_message.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        await db.chat_messages.insert_one(assistant_doc)
        
        # Update or create session
        await db.chat_sessions.update_one(
            {"id": session_id},
            {
                "$set": {
                    "last_interaction": datetime.now(timezone.utc).isoformat()
                },
                "$setOnInsert": {
                    "id": session_id,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        return ChatResponse(
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message
        )
        
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@api_router.get("/chat/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        for msg in messages:
            if isinstance(msg['timestamp'], str):
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
        
        return messages
        
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@api_router.post("/chat/session", response_model=ChatSession)
async def create_chat_session():
    """Create a new chat session"""
    try:
        session = ChatSession()
        
        doc = session.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['last_interaction'] = doc['last_interaction'].isoformat()
        
        await db.chat_sessions.insert_one(doc)
        
        return session
        
    except Exception as e:
        logging.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup message
@app.on_event("startup")
async def startup_event():
    if GROQ_API_KEY:
        logging.info(f"✅ Groq API configured with model: {GROQ_MODEL}")
    else:
        logging.warning("⚠️ GROQ_API_KEY not set - get one free at https://console.groq.com")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()