from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from .tools import TOOLS, set_db_session

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

 
SYSTEM_PROMPT = """You are Movi, an intelligent assistant for a transportation management system. 

Your role is to help users manage:
- Routes, paths, and stops
- Vehicles and drivers
- Trip assignments and status
- Daily operations

When users ask questions or request actions:
1. Use the available tools to get information or perform actions
2. Provide clear, helpful responses
3. If an action could have consequences (like removing a vehicle from a booked trip), explain the impact
4. Be professional and proactive

Always provide concise, actionable responses."""

# Create memory for conversation history
memory = MemorySaver()

# Create the agent using create_react_agent
# This handles all the ReAct logic automatically!
agent_graph = create_react_agent(
    llm,
    TOOLS,
    checkpointer=memory,
    state_modifier=SYSTEM_PROMPT
)


async def get_agent_response(user_message: str, db_session, session_id: str = "default", current_page: str = "") -> dict:
    """
    Process the user message through the agent and return the response.
    
    Args:
        user_message: The user's input message
        db_session: SQLAlchemy database session
        session_id: Session ID for conversation memory
        current_page: Current page context (optional)
    
    Returns:
        dict with 'response' and 'messages' keys
    """
    
    # Set the database session for tools to use
    set_db_session(db_session)
    
    # Create config with thread_id for conversation memory
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }
    
    # Add context about current page if provided
    full_message = user_message
    if current_page:
        full_message = f"[Context: User is on {current_page} page]\n\n{user_message}"
    
    # Prepare input for the agent
    input_data = {
        "messages": [HumanMessage(content=full_message)]
    }
    
    try:
        
        result = await agent_graph.ainvoke(input_data, config)
        
        # Extract the final response
        messages = result.get("messages", [])
        if messages:
            # Get the last AI message
            for msg in reversed(messages):
                if hasattr(msg, 'content') and hasattr(msg, 'type'):
                    if msg.type == 'ai' and msg.content:
                        return {
                            "response": msg.content,
                            "messages": messages
                        }
        
        return {
            "response": "I'm sorry, I couldn't process your request.",
            "messages": messages
        }
        
    except Exception as e:
        print(f"Agent error: {e}")
        return {
            "response": f"I encountered an error: {str(e)}",
            "messages": []
        }