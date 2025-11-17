from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from .state import AgentState
from .tools import TOOLS
import json
import re
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Bind tools to LLM
llm_with_tools = llm.bind_tools(TOOLS)
logger.info(f"LLM initialized with {len(TOOLS)} tools bound")

# Create tool node
tool_node = ToolNode(TOOLS)

SYSTEM_PROMPT = """You are Movi, an intelligent AI assistant for MoveInSync transport management.

**YOUR MISSION:** Execute tasks efficiently by intelligently chaining tools together WITHOUT asking for permission.

**INTELLIGENCE RULES:**
1. **Plan ahead:** If user asks to create something, FIRST check if it exists, THEN create if needed
2. **Execute immediately:** Don't ask "Should I check?" - Just DO IT
3. **Chain actions:** Call tool → Get result → Call next tool if needed → Provide final answer
4. **Never repeat:** If a tool returns a result, READ IT and move to next step. Don't call same tool again

**AVAILABLE TOOLS:**

 **Information Tools** (Check before creating):
• get_all_stops() - List ALL stops (use BEFORE create_stop and go to next step call (create_stop tool ) if stop not exists (create_stop))
• get_all_trips() - List all trips
• get_trip_status(trip_display_name) - Get specific trip details
• get_vehicle_details(license_plate) - Get vehicle info
• get_driver_details(driver_name) - Get driver info
• get_unassigned_vehicles() - Find available vehicles
• get_path_stops(path_name) - Get stops in a path
• get_routes_for_path(path_name) - Get routes for a path

 **Action Tools** (Create/Modify):
• create_stop(stop_name, latitude, longitude) - Create new stop, use after checking existence
• create_path(path_name, stop_names) - Create path with stops
• create_route(...) - Create new route
• assign_vehicle_to_trip(...) - Assign vehicle to trip
• remove_vehicle_from_trip(trip_display_name) - Remove vehicle

**INTELLIGENT WORKFLOWS:**

Example 1: User says "Create stop X"
CORRECT:
1. Call get_all_stops() 
2. Read results
3. If stop exists → Tell user it exists
4. If stop doesn't exist → Call create_stop()
5. Confirm creation

 WRONG:
1. Say "I'll check first" (Don't announce, just do it!)
2. Wait for user to say "ok"
3. Then call get_all_stops()

Example 2: User says "Assign vehicle ABC to trip XYZ"
 CORRECT:
1. Call get_vehicle_details("ABC")
2. If available → Call assign_vehicle_to_trip()
3. Confirm assignment

**CRITICAL RULES:**
• NEVER ask "Should I check?" - Just check!
• NEVER say "I'll get the list first" - Just get it!
• NEVER wait for user confirmation for read operations
• DO wait only for destructive operations (delete, remove) as the user confirmation yes or no 
• After tool returns result, READ IT and proceed to next step
• If tool says "already exists", STOP and tell user
• If tool says "success", STOP and confirm to user

Current Page: {current_page}

**UI PAGES AVAILABLE:**

 **Bus Dashboard Page:**
- Shows: Vehicles Not Assigned, Trips Not Generated, Employees Scheduled, Ongoing Trips
- Actions: Track Route, Generate Tripsheet, Merge Route
- Lists: All routes with booking status (Bulk-0001, Path Path-0002, etc.)
- If we click on the bus it will reveal all the information about that bus like: bus number, driver name, vehicle type, capacity, current location, assigned route, status
- Inside the click there are - Buttons: Manage Vehicles, Manage Bookings, Add/Edit Vehicle
- Top Bar: Date selector, Route filter dropdown, Search by Name/ID, Filters, Pause Operations, Download

 **Manage Routes Page:**
- Header Buttons: History, Download, **+ Routes** (Primary action to create new route)
- Search: "Search route name or ID"
- Filters button
- Tabs: Active Routes | Deactivated Routes
- Table Columns: Route ID, Route Name, Direction, Shift Time, Route Start Point, Route End Point, Capacity, Allowed Waitlist, Action
- Action Menu (⋮): Edit, Deactivate, View Details options

First be aware of what page user is in and answer related to that. If the user's request relates to these pages, use the above details to instruct them, like if user wants to create a route, tell them to go to Manage Routes page and click on + Routes button or offer to do it for them.

Remember: You're autonomous and intelligent. Think → Plan → Execute → Respond. Don't narrate your process!"""

def call_model(state: AgentState):
    """Call the LLM to decide actions."""
    logger.info("=== CALL_MODEL NODE ===")
    messages = state["messages"]
    logger.info(f"Total messages: {len(messages)}")
    
    # Filter messages
    filtered = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            filtered.append(msg)
        elif hasattr(msg, 'content') and msg.content and msg.content.strip():
            filtered.append(msg)
        elif not hasattr(msg, 'content'):
            filtered.append(msg)
    
    messages = filtered
    logger.info(f"After filtering: {len(messages)}")
    
    # Keep last 8 messages max
    if len(messages) > 8:
        messages = messages[-8:]
        logger.info("Trimmed to last 8")
    
    if not messages:
        return {"messages": [AIMessage(content="Error: No messages")]}
    
    # Add system prompt with current page context
    current_page = state.get("current_page", "unknown")
    system_msg = SystemMessage(content=SYSTEM_PROMPT.format(current_page=current_page))
    
    if not isinstance(messages[0], SystemMessage):
        messages = [system_msg] + messages
    
    # Check last message
    last_msg = messages[-1]
    
    # If last message is ToolMessage with a clear result, force direct answer
    if isinstance(last_msg, ToolMessage):
        tool_result = last_msg.content
        logger.info(f"Last is ToolMessage: {tool_result[:100]}")
        
        # Check for final result indicators using prefixes and keywords
        final_prefixes = ["success:", "error:", "info:"]
        final_keywords = [
            "successfully",
            "already exists",
            "not found",
            "no vehicle is currently assigned",
            "no vehicle or driver assigned",
            "no stops found",
            "no routes found",
            "no trips found"
        ]
        
        tool_result_lower = tool_result.lower()
        
        # Check if starts with final prefix or contains final keyword
        is_final = (
            any(tool_result_lower.startswith(prefix) for prefix in final_prefixes) or
            any(keyword in tool_result_lower for keyword in final_keywords)
        )
        
        if is_final:
            logger.info("Tool result is final - providing direct response")
            return {"messages": [AIMessage(content=tool_result)]}
        
        # Otherwise add instruction to continue or finish
        instruction = SystemMessage(content=f"""[SYSTEM]
           
        Tool returned: {tool_result}

        Based on this result:
        - If you need to call another tool to complete the task, do it NOW
        - If the task is complete, provide final answer to user
        - DO NOT call the same tool again""")
        messages = messages + [instruction]
    
    logger.info(f"Calling LLM with {len(messages)} messages...")
    
    try:
        response = llm_with_tools.invoke(messages)
        
        has_tools = hasattr(response, 'tool_calls') and response.tool_calls
        logger.info(f"LLM response has tool_calls: {has_tools}")
        
        if has_tools:
            logger.info(f"Tool calls: {[(tc['name'], tc.get('args', {})) for tc in response.tool_calls]}")
        
        return {"messages": [response]}
        
    except Exception as e:
        logger.error(f"LLM error: {str(e)[:200]}")
        if "429" in str(e) or "quota" in str(e).lower():
            return {"messages": [AIMessage(content=" API rate limit reached. Please wait.")]}
        return {"messages": [AIMessage(content="I encountered an error. Please try again.")]}

def should_continue(state: AgentState) -> str:
    """Decide if we continue to tools or end."""
    logger.info("=== SHOULD_CONTINUE NODE ===")
    messages = state["messages"]
    last_message = messages[-1]
    
    # Count tool executions ONLY since last HumanMessage (current request)
    tool_execution_count = 0
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            break
        elif isinstance(msg, ToolMessage):
            tool_execution_count += 1
    
    logger.info(f"Tool executions in current request: {tool_execution_count}")
    
    # HARD LIMIT: Max 3 tool executions per user request
    if tool_execution_count >= 3:
        logger.warning(f"HIT LIMIT: {tool_execution_count} tool executions! FORCING END")
        return "end"
    
    # Check if LLM wants to call tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        if tool_execution_count >= 3:
            logger.error(" LLM wants to call tools but limit reached!")
            last_tool_msg = None
            for msg in reversed(messages):
                if isinstance(msg, ToolMessage):
                    last_tool_msg = msg
                    break
            
            if last_tool_msg:
                forced_response = AIMessage(content=last_tool_msg.content)
            else:
                forced_response = AIMessage(content="I've processed your request.")
            
            state["messages"] = state["messages"] + [forced_response]
            return "end"
        
        logger.info(f"Continuing to tools ({len(last_message.tool_calls)} calls)")
        return "tools"
    
    logger.info("No tool calls - ending")
    return "end"

def check_consequences(state: AgentState) -> AgentState:
    """
    CRITICAL: Check consequences for destructive actions BEFORE execution.
    This implements the "Tribal Knowledge" flow.
    """
    logger.info("=== CHECK_CONSEQUENCES NODE ===")
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if there are tool calls to examine
    if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
        logger.info("No tool calls to check")
        return {}
    
    # Examine each tool call for potential consequences
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get("name")
        logger.info(f"Checking tool: {tool_name}")
        
        # CRITICAL: Check for remove_vehicle_from_trip
        if tool_name == "remove_vehicle_from_trip":
            trip_name = tool_call.get("args", {}).get("trip_display_name")
            logger.info(f" CONSEQUENCE CHECK: Removing vehicle from '{trip_name}'")
            
            try:
                # Import the tool function to check trip status
                from .tools import get_trip_status
                
                # Get current trip status
                trip_result = get_trip_status.invoke({"trip_display_name": trip_name})
                logger.info(f"Trip status result: {trip_result}")
                
                # Check if trip has no vehicle (safe to "remove")
                if "no vehicle" in trip_result.lower():
                    logger.info(" No vehicle assigned - safe to proceed")
                    continue
                
                # CRITICAL: Parse booking percentage
                booking_percent = 0
                
                # Look for patterns like "50% booked", "Booking: 50%", etc.
                booking_patterns = [
                    r"booking[:\s]+(\d+)%",  # "Booking: 50%"
                    r"(\d+)%\s*booked",       # "50% booked"
                    r"booked[:\s]+(\d+)%"     # "Booked: 50%"
                ]
                
                for pattern in booking_patterns:
                    match = re.search(pattern, trip_result, re.IGNORECASE)
                    if match:
                        booking_percent = int(match.group(1))
                        logger.info(f"Found booking: {booking_percent}%")
                        break
                
                # If there are bookings, require confirmation
                if booking_percent > 0:
                    logger.warning(f"CONSEQUENCE DETECTED: {booking_percent}% booked!")
                    
                    # Extract vehicle details if available
                    vehicle_match = re.search(r"vehicle[:\s]+([^\s,]+)", trip_result, re.IGNORECASE)
                    vehicle_info = vehicle_match.group(1) if vehicle_match else "the assigned vehicle"
                    
                    # Create consequence warning message
                    consequence_msg = (
                        f" **Warning: Consequence Detected**\n\n"
                        f"Trip **'{trip_name}'** is currently **{booking_percent}% booked** by employees.\n\n"
                        f"**Consequences of removing {vehicle_info}:**\n"
                        f"• All {booking_percent}% of bookings will be **cancelled**\n"
                        f"• Trip-sheet generation will **fail**\n"
                        f"• Employees will lose their ride\n\n"
                        f"**Do you want to proceed?** (yes/no)"
                    )
                    
                    logger.info(f" BLOCKING action - awaiting user confirmation")
                    
                    # Return state update to pause execution
                    return {
                        "awaiting_confirmation": True,
                        "pending_action": tool_call,
                        "consequence_info": {
                            "trip_name": trip_name,
                            "booking_percent": booking_percent,
                            "vehicle": vehicle_info
                        },
                        "response": consequence_msg,
                        "messages": messages + [AIMessage(content=consequence_msg)]
                    }
                
                else:
                    logger.info(" No bookings found - safe to proceed")
                    
            except Exception as e:
                logger.error(f" Error checking consequences: {str(e)}", exc_info=True)
                # On error, allow action but log warning
                logger.warning(" Could not verify consequences - allowing action")
    
    # No consequences detected - allow tools to execute
    logger.info(" No consequences detected - proceeding to tool execution")
    return {}

def handle_confirmation(state: AgentState) -> AgentState:
    """
    Handle user confirmation for actions with consequences.
    This is part of the "Tribal Knowledge" flow.
    """
    logger.info("=== HANDLE_CONFIRMATION NODE ===")
    
    user_message = state.get("user_message", "").lower().strip()
    logger.info(f"User response: '{user_message}'")
    
    # Check for positive confirmation
    positive_responses = ["yes", "yeah", "yep", "ok", "okay", "sure", "proceed", "continue", "confirm"]
    if any(word in user_message for word in positive_responses):
        logger.info(" User confirmed - executing action")
        
        pending_action = state.get("pending_action")
        if not pending_action:
            error_msg = " Error: No pending action found"
            logger.error(error_msg)
            return {
                "response": error_msg,
                "awaiting_confirmation": False,
                "pending_action": None,
                "messages": state["messages"] + [AIMessage(content=error_msg)]
            }
        
        try:
            # Execute the pending action
            tool_name = pending_action.get("name")
            tool_args = pending_action.get("args", {})
            
            logger.info(f"Executing {tool_name} with args: {tool_args}")
            
            # Import and execute the tool
            from .tools import remove_vehicle_from_trip
            
            if tool_name == "remove_vehicle_from_trip":
                tool_result = remove_vehicle_from_trip.invoke(tool_args)
                logger.info(f"Tool result: {tool_result}")
                
                success_msg = f" {tool_result}"
                
                return {
                    "response": success_msg,
                    "awaiting_confirmation": False,
                    "pending_action": None,
                    "consequence_info": None,
                    "messages": state["messages"] + [AIMessage(content=success_msg)]
                }
            else:
                error_msg = f" Unknown tool: {tool_name}"
                logger.error(error_msg)
                return {
                    "response": error_msg,
                    "awaiting_confirmation": False,
                    "pending_action": None,
                    "messages": state["messages"] + [AIMessage(content=error_msg)]
                }
                
        except Exception as e:
            error_msg = f" Error executing action: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "response": error_msg,
                "awaiting_confirmation": False,
                "pending_action": None,
                "consequence_info": None,
                "messages": state["messages"] + [AIMessage(content=error_msg)]
            }
    
    # Check for negative confirmation
    negative_responses = ["no", "nope", "cancel", "stop", "abort", "don't", "dont"]
    if any(word in user_message for word in negative_responses):
        logger.info(" User cancelled action")
        
        cancel_msg = " Action cancelled. The vehicle will remain assigned to the trip ,Please say yes or no to continue."
        return {
            "response": cancel_msg,
            "awaiting_confirmation": False,
            "pending_action": None,
            "consequence_info": None,
            "messages": state["messages"] + [AIMessage(content=cancel_msg)]
        }
    
    # Unclear response - ask for clarification
    logger.warning(f" Unclear response: '{user_message}'")
    clarify_msg = "lease respond with **'yes'** to proceed or **'no'** to cancel."
    
    return {
        "response": clarify_msg,
        "awaiting_confirmation": True,  # Keep waiting
        "messages": state["messages"] + [AIMessage(content=clarify_msg)]
    }