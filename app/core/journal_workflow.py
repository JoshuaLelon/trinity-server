from typing import Annotated, TypedDict, List, Dict, Any, Optional, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langsmith import traceable

from app.core.config import settings
from app.utils.notion import notion_client

# Set up the langshmith API key environment variable
import os
os.environ["LANGCHAIN_API_KEY"] = settings.get_langchain_api_key()
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT or settings.LANGSMITH_PROJECT
os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2 or settings.LANGSMITH_TRACING).lower()

# Define the state schema for our workflow
class JournalState(TypedDict):
    # Messages have type "list". The add_messages function defines how this state key is updated
    messages: Annotated[List[Any], add_messages]
    current_prompt: str  # "gratitude", "desire", or "brag"
    completed_prompts: List[str]
    formatted_responses: Dict[str, str]  # Stores cleaned responses for Notion
    user_stuck: bool  # Flag to indicate if user needs prompt refinement
    classification: Optional[Dict[str, Any]]  # Classification results
    saved_to_notion: bool  # Flag to indicate if saved to Notion


# Set up the LLM with clear, purpose-specific configuration
# Ensure the API key is properly set
api_key = settings.OPENAI_API_KEY
if not api_key:
    raise ValueError("OpenAI API key is not set. Please check your environment variables.")

model = ChatOpenAI(
    model="gpt-4o",
    temperature=settings.LLM_TEMPERATURE,  # Low temperature for deterministic responses
    api_key=api_key
)


# Define tools with clear documentation and purpose
@tool
async def save_to_notion(prompt_type: str, content: str) -> str:
    """
    Save the journal entry to Notion in the correct category.
    
    Args:
        prompt_type: The type of prompt (gratitude, desire, or brag)
        content: The formatted journal entry text
        
    Returns:
        Success or failure message
    """
    success = await notion_client.save_journal_entry(prompt_type, content)
    if success:
        return "Successfully saved to Notion"
    return "Failed to save to Notion"


@tool
async def get_completed_prompts() -> List[str]:
    """
    Get the list of prompts already completed today.
    
    Returns:
        List of completed prompt types (gratitude, desire, brag)
    """
    return await notion_client.get_completed_prompts()


# Workflow nodes - each with a single, clear responsibility
@traceable(run_type="chain")
def classify_response(state: JournalState) -> Dict[str, Any]:
    """
    Classify the user's response to determine which prompt it fits best.
    
    This node handles:
    1. Extracting the latest user message
    2. Sending it to the LLM for classification
    3. Parsing the classification result
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated state with classification results
    """
    messages = state['messages']
    current_prompt = state['current_prompt']
    
    # Get the latest user message
    if not messages or len(messages) == 0:
        return {"classification": {"prompt": current_prompt, "confidence": 1.0}}
    
    latest_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            latest_user_message = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "user":
            latest_user_message = msg.get("content")
            break
    
    if not latest_user_message:
        return {"classification": {"prompt": current_prompt, "confidence": 1.0}}
    
    # Create the system message for classification with detailed instructions
    classification_system_msg = f"""
    You are analyzing a journal response to determine which prompt category it best fits into.
    
    The current prompt is: {current_prompt}
    
    Determine if the user's response matches this prompt, or if it better matches one of these categories:
    - gratitude: expressions of thankfulness, appreciation for something/someone
    - desire: wishes, wants, aspirations, goals the user has
    - brag: accomplishments, proud moments, positive self-reflection
    
    Analyze the response and return a JSON with these fields:
    - prompt: the category that best matches the response (gratitude, desire, or brag)
    - confidence: a value between 0 and 1 indicating your confidence in this classification
    - explanation: brief reason for your classification
    
    Base your classification purely on the content, not on how the prompt was phrased.
    """
    
    # Get classification from model
    classification_result = model.invoke([
        {"role": "system", "content": classification_system_msg},
        {"role": "user", "content": latest_user_message}
    ])
    
    # Parse the result to extract JSON with robust error handling
    try:
        import json
        import re
        
        # Try to extract JSON from the response
        result_text = classification_result.content
        json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'(\{.*\})', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result_text
        
        classification = json.loads(json_str)
        return {"classification": classification}
    except Exception as e:
        print(f"Error parsing classification: {e}")
        # Default to current prompt if parsing fails
        return {"classification": {"prompt": current_prompt, "confidence": 0.5, "explanation": "Failed to parse classification result"}}


@traceable(run_type="chain")
def handle_prompt_switch(state: JournalState) -> Dict[str, Any]:
    """
    Handle switching the prompt if the classification suggests it.
    
    This node:
    1. Checks if the detected prompt differs from the current prompt
    2. Switches the prompt if confidence is high enough
    3. Generates a friendly message explaining the switch
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated state with new prompt and explanation message
    """
    classification = state.get("classification", {})
    current_prompt = state["current_prompt"]
    detected_prompt = classification.get("prompt", current_prompt)
    confidence = classification.get("confidence", 0)
    
    if detected_prompt != current_prompt and confidence > 0.7:
        # Switch the prompt with a clear explanation
        response = f"I notice you're talking about {detected_prompt} instead of {current_prompt}. Let's switch to that prompt."
        return {
            "messages": [AIMessage(content=response)],
            "current_prompt": detected_prompt
        }
    
    return {}  # No changes if no switch needed


@traceable(run_type="chain")
def continue_with_current(state: JournalState) -> Dict[str, Any]:
    """
    Continue with the current prompt without switching.
    
    This is a no-op node that serves as a clear branch in the workflow.
    
    Args:
        state: The current workflow state
        
    Returns:
        Unchanged state
    """
    return {}  # No state changes


@traceable(run_type="chain")
def refine_prompt(state: JournalState) -> Dict[str, Any]:
    """
    Refine the prompt if the user seems stuck.
    
    This node:
    1. Analyzes the user message for signs of being stuck
    2. Provides targeted suggestions based on the prompt type
    3. Sets a flag to indicate refinement was needed
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated state with refinement message and stuck flag
    """
    messages = state['messages']
    current_prompt = state['current_prompt']
    
    # Get the latest user message
    latest_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            latest_user_message = msg.content.lower() if msg.content else ""
            break
        elif isinstance(msg, dict) and msg.get("role") == "user":
            latest_user_message = msg.get("content", "").lower()
            break
    
    if not latest_user_message:
        return {"user_stuck": False}
    
    # Check for signs of being stuck with comprehensive criteria
    stuck_phrases = ["i don't know", "not sure", "can't think", "um", "uh", "hmm", "difficult", "struggling"]
    
    is_stuck = any(phrase in latest_user_message for phrase in stuck_phrases) or len(latest_user_message.split()) < 3
    
    if is_stuck:
        # Generate refinement based on prompt type with specific, helpful suggestions
        refinements = {
            "gratitude": "Let's break this down. Consider gratitude in these areas: health, relationships, career, or small daily joys. What's something positive you've experienced recently?",
            "desire": "What about desires related to personal growth, experiences you want to have, or changes you'd like to make? It could be something big or small you're looking forward to.",
            "brag": "Think about recent accomplishments, challenges you've overcome, or personal strengths you've displayed. Even small victories count - what's something you did well?"
        }
        
        return {
            "messages": [AIMessage(content=refinements[current_prompt])],
            "user_stuck": True
        }
    
    return {"user_stuck": False}


@traceable(run_type="chain")
def format_response(state: JournalState) -> Dict[str, Any]:
    """
    Format the user's response for readability and clarity.
    
    This node:
    1. Collects all user messages for the current prompt
    2. Sends them to the LLM for formatting
    3. Stores the formatted response for later use
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated state with formatted responses
    """
    messages = state['messages']
    current_prompt = state['current_prompt']
    
    # Get user messages for the current prompt
    user_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_messages.append(msg.content)
        elif isinstance(msg, dict) and msg.get("role") == "user":
            user_messages.append(msg.get("content", ""))
    
    if not user_messages:
        return {}
    
    # Format the combined response with clear instructions
    formatting_system_msg = """
    Clean up this journal response while preserving the original sentiment and content.
    
    Guidelines:
    - Remove filler words, repetition, and hesitations
    - Fix grammar and punctuation
    - Improve readability and flow
    - Keep the personal tone and all important details
    - Aim for 2-3 sentences maximum, focusing on the core message
    
    Return only the cleaned text with no additional commentary.
    """
    
    formatted_response = model.invoke([
        {"role": "system", "content": formatting_system_msg},
        {"role": "user", "content": " ".join(user_messages)}
    ])
    
    # Update the formatted responses dictionary
    formatted_responses = state.get("formatted_responses", {})
    formatted_responses[current_prompt] = formatted_response.content
    
    return {"formatted_responses": formatted_responses}


@traceable(run_type="chain")
async def save_entry_to_notion(state: JournalState) -> Dict[str, Any]:
    """
    Save the formatted entry to Notion.
    
    This node:
    1. Gets the formatted entry for the current prompt
    2. Saves it to Notion using the client
    3. Updates the list of completed prompts
    4. Provides feedback on the successful save
    5. Sets up the next prompt if available
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated state with save status, completed prompts, and next prompt
    """
    current_prompt = state["current_prompt"]
    formatted_responses = state.get("formatted_responses", {})
    
    if current_prompt not in formatted_responses:
        return {"saved_to_notion": False}
    
    content = formatted_responses[current_prompt]
    
    # Try to save to Notion, but don't let failures block the workflow
    try:
        print(f"Attempting to save {current_prompt} entry to Notion: {content}")
        success = await notion_client.save_journal_entry(current_prompt, content)
        print(f"Save to Notion result: {success}")
    except Exception as e:
        # Log the error but continue with the workflow
        print(f"Error saving to Notion: {str(e)}")
        success = False
    
    # Always update completed prompts regardless of Notion save status
    completed_prompts = state.get("completed_prompts", [])
    if current_prompt not in completed_prompts:
        completed_prompts.append(current_prompt)
        
    # Generate a response based on which prompts are left
    all_prompts = ["gratitude", "desire", "brag"]
    remaining_prompts = [p for p in all_prompts if p not in completed_prompts]
    
    # Create appropriate response messages
    if not remaining_prompts:
        if success:
            response = "Great job! You've completed all your journal prompts for today and they've been saved to Notion."
        else:
            response = "Great job! You've completed all your journal prompts for today. I've saved your entries locally, but couldn't save them to Notion."
    else:
        next_prompt = remaining_prompts[0]
        if success:
            response = f"Saved your {current_prompt} entry to Notion! Let's move on to {next_prompt}."
        else:
            response = f"I've recorded your {current_prompt} entry locally (though it couldn't be saved to Notion). Let's move on to {next_prompt}."
    
    # Return updated state
    return {
        "messages": [AIMessage(content=response)],
        "saved_to_notion": success,
        "completed_prompts": completed_prompts,
        "current_prompt": remaining_prompts[0] if remaining_prompts else current_prompt
    }


# Define state graph conditions with clear logic and purpose
def should_switch_prompt(state: JournalState) -> str:
    """
    Determine if we should switch the prompt based on classification.
    
    This condition checks:
    1. If the classified prompt is different from the current one
    2. If the confidence level is high enough to warrant a switch
    
    Args:
        state: The current workflow state
        
    Returns:
        The next node to execute based on the condition
    """
    classification = state.get("classification", {})
    if classification.get("prompt") != state["current_prompt"] and classification.get("confidence", 0) > 0.7:
        return "handle_prompt_switch"
    return "continue_current_prompt"


def should_refine_prompt(state: JournalState) -> str:
    """
    Determine if we should refine the prompt based on user response.
    
    This condition checks:
    1. If the user message contains indicators of being stuck
    2. If the message is too short to be a complete response
    
    Args:
        state: The current workflow state
        
    Returns:
        The next node to execute based on the condition
    """
    messages = state['messages']
    
    # Get the latest user message
    latest_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            latest_user_message = msg.content.lower() if msg.content else ""
            break
        elif isinstance(msg, dict) and msg.get("role") == "user":
            latest_user_message = msg.get("content", "").lower()
            break
    
    if not latest_user_message:
        return "format_response"
    
    # Check for signs of being stuck
    stuck_phrases = ["i don't know", "not sure", "can't think", "um", "uh", "hmm", "difficult", "struggling"]
    
    if any(phrase in latest_user_message for phrase in stuck_phrases) or len(latest_user_message.split()) < 3:
        return "refine_prompt"
    return "format_response"


# Create the journal workflow graph with a clear, linear flow
def create_journal_workflow() -> StateGraph:
    """
    Create and compile the journal workflow graph.
    
    This function:
    1. Creates a StateGraph with the JournalState schema
    2. Adds nodes for each step in the workflow
    3. Connects nodes with edges and conditional logic
    4. Compiles and returns the workflow
    
    Returns:
        Compiled StateGraph for journal processing
    """
    # Create the graph
    workflow = StateGraph(JournalState)
    
    # Add nodes
    workflow.add_node("classify_response", classify_response)
    workflow.add_node("handle_prompt_switch", handle_prompt_switch)
    workflow.add_node("continue_current_prompt", continue_with_current)
    workflow.add_node("refine_prompt", refine_prompt)
    workflow.add_node("format_response", format_response)
    workflow.add_node("save_to_notion", save_entry_to_notion)
    
    # Set entry point
    workflow.add_edge("__start__", "classify_response")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "classify_response",
        should_switch_prompt,
        {
            "handle_prompt_switch": "refine_prompt",
            "continue_current_prompt": "refine_prompt"
        }
    )
    
    # Add conditional edges for refinement
    workflow.add_conditional_edges(
        "refine_prompt",
        should_refine_prompt,
        {
            "refine_prompt": "format_response",
            "format_response": "format_response"
        }
    )
    
    # Format then save to Notion
    workflow.add_edge("format_response", "save_to_notion")
    
    # Save and end
    workflow.add_edge("save_to_notion", END)
    
    # Compile the graph with config options
    compiled = workflow.compile()
    
    # Store the original ainvoke method
    original_ainvoke = compiled.ainvoke
    
    # Create a wrapper to handle the config parameter and other kwargs
    async def invoke_wrapper(state, **kwargs):
        # We need to ignore any additional kwargs that the original method doesn't expect
        # The original method only accepts the state parameter
        print(f"Invoking journal workflow with state type: {type(state).__name__}")
        
        # Check if state is a dict and convert it to JournalState if needed
        if isinstance(state, dict):
            # Ensure all required fields are present
            if 'messages' not in state:
                state['messages'] = []
            if 'current_prompt' not in state:
                state['current_prompt'] = 'gratitude'  # Default prompt
            if 'completed_prompts' not in state:
                state['completed_prompts'] = []
            if 'formatted_responses' not in state:
                state['formatted_responses'] = {}
            if 'user_stuck' not in state:
                state['user_stuck'] = False
            if 'classification' not in state:
                state['classification'] = None
            if 'saved_to_notion' not in state:
                state['saved_to_notion'] = False
        
        try:
            # Ignore any kwargs that aren't expected by the original method
            return await original_ainvoke(state)
        except TypeError as e:
            print(f"Error in journal workflow: {str(e)}")
            # If there's a TypeError, it might be due to unexpected kwargs
            # Just return the current state as a fallback
            return state
    
    # Replace the ainvoke method with our wrapper
    compiled.ainvoke = invoke_wrapper
    
    return compiled


# Create the workflow instance
journal_workflow = create_journal_workflow() 