from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import call_model, tool_node, should_continue, check_consequences, handle_confirmation
import logging

logger = logging.getLogger(__name__)

def create_agent_graph():
    """Create langgraph for the Movi agent."""
    logger.info("Creating agent graph...")
    
     
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("check_consequences", check_consequences)
    workflow.add_node("handle_confirmation", handle_confirmation)
    
    # Set the entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "check_consequences",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "check_consequences",
        lambda state: "handle_confirmation" if state.get("awaiting_confirmation") else "tools",
        {
            "handle_confirmation": "handle_confirmation",
            "tools": "tools"
        }
    )
    
    workflow.add_conditional_edges(
        "handle_confirmation",
        lambda state: "agent" if state.get("awaiting_confirmation") else "complete",
        {
            "agent": "agent",
            "complete": END
        }
    )
    
    # Add regular edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Add memory for conversation history
    memory = MemorySaver()
    
    # Compile the graph
    logger.info("Agent graph compiled successfully")
    return workflow.compile(checkpointer=memory)

 
agent_graph = create_agent_graph()

async def get_agent_response(state: AgentState) -> str:
    """Process the user message through the agent graph and return the response."""
    try:
        logger.info(f"Processing agent request for session: {state.get('session_id', 'default')}")
        logger.info(f"User message: {state.get('user_message', '')}")
        
        #   conversation memory
        config = {"configurable": {"thread_id": state.get("session_id", "default")}}
        
      
        if state.get("awaiting_confirmation"):
            logger.info("Handling confirmation...")
            result = handle_confirmation(state)
            response = result.get("response", "I'm sorry, I couldn't process your request.")
            logger.info(f"Confirmation result response: {response}")
            return response
        
        # Process through the graph
        logger.info("Invoking agent graph...")
        result = await agent_graph.ainvoke(state, config)
        
        logger.info(f"Agent graph completed. Result keys: {result.keys()}")
        logger.info(f"Result response field: '{result.get('response', 'NOT FOUND')}'")
        logger.info(f"Result awaiting_confirmation: {result.get('awaiting_confirmation', False)}")
        
        # CRITICAL FIX: Check for response field first (from confirmation/consequence nodes)
        if "response" in result and result["response"] and result["response"].strip():
            logger.info(f"Found non-empty response field, returning: {result['response']}")
            return result["response"]
        
        # Otherwise, extract from messages (look backwards through messages for non-empty content)
        if "messages" in result and result["messages"]:
            logger.info(f"Checking {len(result['messages'])} messages for content")
            # Search backwards through messages to find the last one with content
            for message in reversed(result["messages"]):
                if hasattr(message, 'content') and message.content and message.content.strip():
                    logger.info(f"Found message with content: {message.content[:100]}...")
                    return message.content
            logger.warning("All messages have empty content!")
        
        logger.warning("No response found in result, returning default message")
        return "I'm sorry, I couldn't process your request."
    
    except Exception as e:
        logger.error(f"Error in get_agent_response: {str(e)}", exc_info=True)
        raise