from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class JournalRequest(BaseModel):
    """Request model for journal processing."""
    transcription: str = Field(..., description="The transcribed text from user's voice input")
    current_prompt: str = Field(..., description="The current prompt type (gratitude, desire, or brag)")
    completed_prompts: List[str] = Field(default_factory=list, description="List of prompts already completed today")


class JournalResponse(BaseModel):
    """Response model for journal processing."""
    detected_prompt: str = Field(..., description="The prompt type detected from the response")
    prompt_changed: bool = Field(..., description="Whether the prompt was changed based on the response")
    formatted_response: str = Field(..., description="The cleaned and formatted response")
    needs_refinement: bool = Field(..., description="Whether the prompt needs refinement")
    refinement_suggestion: Optional[str] = Field(None, description="Suggested refinement if user is stuck")
    saved_to_notion: bool = Field(..., description="Whether the response was saved to Notion")


class NotionEntry(BaseModel):
    """Model for Notion journal entry."""
    date: str = Field(..., description="The date of the journal entry")
    gratitude: List[str] = Field(default_factory=list, description="List of gratitude entries")
    desire: List[str] = Field(default_factory=list, description="List of desire entries")
    brag: List[str] = Field(default_factory=list, description="List of brag entries")


class StateUpdate(BaseModel):
    """Model for partial state updates in the LangGraph workflow."""
    messages: Optional[List[Dict[str, str]]] = None
    current_prompt: Optional[str] = None
    completed_prompts: Optional[List[str]] = None
    formatted_responses: Optional[Dict[str, str]] = None
    user_stuck: Optional[bool] = None
    classification: Optional[Dict[str, str]] = None
    saved_to_notion: Optional[bool] = None 