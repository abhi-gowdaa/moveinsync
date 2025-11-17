from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Service.DBService.database import get_db, create_db
from agent.graph import get_agent_response
from agent.state import AgentState
from agent.tools import set_db_session
from langchain_core.messages import HumanMessage

import json
import uuid
import os
import logging
import base64
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from api import routes
from Service.Integration.vision import extract_photo_summary
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create database tables
create_db()

app = FastAPI(title="Movi Backend API")



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)



app.include_router(routes.router,  tags=["routes"])


# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)




@app.post("/api/agent/chat")
async def chat_with_agent(request: dict, db: Session = Depends(get_db)):
    """
    Standard chat endpoint without image.
    """
    try:
        logger.info(f"Received chat request: {request}")
        
        # Set the database session globally for tools to use
        set_db_session(db)
        logger.info("Database session set")
        
        
        user_message = request.get("message", "")
        current_page = request.get("currentPage", "")
        session_id = request.get("sessionId", str(uuid.uuid4()))
        
        logger.info(f"Processing message: '{user_message}' on page: '{current_page}'")
        
        #  we initialize agent state
        state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "user_message": user_message,
            "current_page": current_page,
            "session_id": session_id,
            "response": "",
            "pending_action": None,
            "awaiting_confirmation": False,
            "consequences": [],
            "context": {},
            "image_path": None
        }
        
        logger.info("Agent state initialized, calling agent...")
        
         
        response = await get_agent_response(state)
        
        logger.info(f"Agent response received: {response}")
        
        return {
            "response": response,
            "sessionId": session_id,
            "requiresConfirmation": False,
            "pendingAction": None
        }
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/image")
async def process_image_with_message(
    file: UploadFile = File(...),
    message: str = Form(...),
    currentPage: str = Form(""),
    sessionId: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
 
    try:
        logger.info(f"=== IMAGE PROCESSING STARTED ===")
        logger.info(f"Image: {file.filename}, Message: {message}")
        
         
        if not sessionId:
            sessionId = str(uuid.uuid4())
        
        # Save uploaded file
        file_location = f"uploads/{sessionId}_{file.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await file.read())
        
        logger.info(f"Image saved to: {file_location}")
        
        # STEP 1: Extract photo content using Gemini Vision
        logger.info("Extracting photo content...")
        photo_summary = await extract_photo_summary(file_location)
        
        # STEP 2: Combine user message with photo summary
        if photo_summary:
            user_message = f"{message}\n\n[From uploaded image: {photo_summary}]"
            logger.info(f"Combined message: {user_message}")
        else:
            user_message = message
            logger.warning("Photo extraction failed, using original message only")
        
      
        set_db_session(db)
        logger.info("Database session set")
        
      
        current_page = currentPage
        
        logger.info(f"Processing message: '{user_message}' on page: '{current_page}'")
        
        
        state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "user_message": user_message,
            "current_page": current_page,
            "session_id": sessionId,
            "response": "",
            "pending_action": None,
            "awaiting_confirmation": False,
            "consequences": [],
            "context": {},
            "image_path": file_location  # Store for reference
        }
        
        logger.info("Agent state initialized, calling agent...")
        
       
        response = await get_agent_response(state)
        
        logger.info(f"Agent response received: {response}")
        logger.info(f"=== IMAGE PROCESSING COMPLETED ===")
        
      
        return {
            "response": response,
            "sessionId": sessionId,
            "requiresConfirmation": False,
            "pendingAction": None
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Welcome to Movi Backend API"}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")