# Chatbot API
A professional AI-powered chatbot backend built with FastAPI, MongoDB, and Groq AI. Designed for IT recruiting and software solutions company customer support.

## Features:

* Fast & Free AI - Powered by Groq's lightning-fast LLaMA 3.1 model
* Conversational Memory - Maintains context across chat sessions
* MongoDB Storage - Persistent chat history and session management
* RESTful API - Clean, documented endpoints for easy integration
* CORS Enabled - Ready for frontend integration
* Professional Responses - Context-aware answers about IT recruiting and software services

## Tech Stack:

* FastAPI - Modern, fast Python web framework
* MongoDB - NoSQL database for chat storage
* Motor - Async MongoDB driver
* Groq AI - Free, ultra-fast LLM inference
* Pydantic - Data validation and serialization
* Python 3.8+

## Prerequisites:

* Python 3.8 or higher
* MongoDB 8.0+ (local or cloud)
* Groq API Key (free at console.groq.com)

## Quick Start:

1. Clone the Repository <br>
bashgit clone https://github.com/yourusername/pinnacle-chatbot.git <br>
cd pinnacle-chatbot <br>
2. Set Up Virtual Environment <br>
bash# Create virtual environment <br>
python -m venv venv <br>

### Activate it
#### On macOS/Linux:
source venv/bin/activate

#### On Windows:
venv\Scripts\activate

3. Install Dependencies <br>
bashpip install -r requirements.txt

4. Configure Environment Variables <br>
Create a .env file in the backend directory:<br>
MONGO_URL="mongodb://localhost:27017"<br>
DB_NAME="test_database"<br>
GROQ_API_KEY="gsk_your_api_key_here"<br>
GROQ_MODEL="llama-3.1-8b-instant"<br>
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

## Running the Project <br>
1) Start MongoDB <br>
brew services start mongodb-community@8.0 <br>

2) Run the Backend Server <br>
cd backend<br>
uvicorn server:app --reload --host 0.0.0.0 --port 8000<br>

3) Run the React Frontend
cd .. <br>
npm start <br>
