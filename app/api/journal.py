from fastapi import APIRouter, HTTPException, Depends
from typing import List
import traceback
import logging
from langchain_core.messages import HumanMessage, AIMessage

from app.models.schemas import JournalRequest, JournalResponse
from app.core.journal_workflow import journal_workflow
from app.utils.notion import notion_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/process", response_model=JournalResponse)
async def process_journal(request: JournalRequest):
    """
    Process a journal entry using the LangGraph workflow.
    
    This endpoint:
    1. Classifies the response to determine which prompt it fits
    2. Switches prompts if necessary
    3. Refines the prompt if the user seems stuck
    4. Formats the response for readability
    5. Saves the entry to Notion
    """
    try:
        # Initialize the journal state with a LangChain HumanMessage
        initial_state = {
            "messages": [HumanMessage(content=request.transcription)],
            "current_prompt": request.current_prompt,
            "completed_prompts": request.completed_prompts,
            "formatted_responses": {},
            "user_stuck": False,
            "saved_to_notion": False
        }
        
        logger.info(f"Processing journal entry: {request.transcription[:50]}...")
        
        # Run the LangGraph workflow
        try:
            result = await journal_workflow.ainvoke(initial_state)
            logger.info("Workflow completed successfully")
        except Exception as workflow_error:
            logger.error(f"Workflow error: {str(workflow_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, 
                detail=f"Error in journal workflow: {str(workflow_error)}"
            )
        
        # Extract relevant information
        current_prompt = result["current_prompt"]
        detected_prompt = result.get("classification", {}).get("prompt", current_prompt)
        formatted_responses = result.get("formatted_responses", {})
        
        # Get the last assistant message for refinement suggestion
        refinement_suggestion = None
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, AIMessage):
                refinement_suggestion = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                refinement_suggestion = msg.get("content")
                break
        
        response = JournalResponse(
            detected_prompt=detected_prompt,
            prompt_changed=detected_prompt != request.current_prompt,
            formatted_response=formatted_responses.get(current_prompt, ""),
            needs_refinement=result.get("user_stuck", False),
            refinement_suggestion=refinement_suggestion,
            saved_to_notion=result.get("saved_to_notion", False)
        )
        
        logger.info(f"Journal response processed: {response.detected_prompt}")
        return response
    
    except Exception as e:
        logger.error(f"Error processing journal entry: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/completed-prompts", response_model=List[str])
async def get_completed_prompts():
    """Get a list of prompts that have been completed today."""
    try:
        return await notion_client.get_completed_prompts()
    except Exception as e:
        logger.error(f"Error getting completed prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 