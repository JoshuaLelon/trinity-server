# Phase 4: AI-Powered Prompt Switching & Formatting with LangGraph

**[Home](../README.md) | [Previous: Phase 3](./phase_3.md)**

---

## Problem Statement
The app should intelligently handle user responses, allowing prompt switching when a user mixes multiple types of responses. It should also refine prompts dynamically if the user gets stuck. This ensures a more natural and flexible journaling experience.

## Solution Overview
In this phase, we create the backend that will:
- AI-based classification of responses to determine whether they match the current prompt. This should use a Routing Workflow as defined in this blog:
- Dynamic prompt switching when the answer the user gives matches a different prompt.
- Adaptive prompt refinement if the user is stuck.
- Formatting of responses before sending to Notion.

Note: in this phase, we will be moving the logic that connects to the Notion API into the backend.

---
Note: consider design patterns and UI design

## Feature List
### **Existing (From Previous Phase)**
- **Notifications**: Sent at 8 AM, then every 30 minutes if the user hasn't journaled.
- **UI**: Displays current prompt and transcribed response.
- **Speech-to-Text**: Automatic transcription when the app is opened.
- **Notion API Integration**: Stores journal responses in Notion under corresponding fields.
- **Journaling Flow**:
  - User opens the app, and recording begins automatically.
  - Speech is transcribed and displayed.
  - User can edit or save the response.
  - App moves to the next prompt.

### **New (Implemented in This Phase)**
- **AI-Based Prompt Classification**:
  - Detect which of the three prompts (gratitude, desire, brag) the response best aligns with and switch to that prompt.
- **Dynamic Prompt Switching**:
  - Switch to a different prompt and let the user know that the prompt has changed.
- **Adaptive Prompt Refinement**:
  - If the user says "I don't know" or is stuck, refine the prompt with subcategories.
  - Example: If stuck on gratitude, suggest health, career, or relationships.
- **Formatting of Responses**:
  - Ensure responses are cleaned up before sending to Notion. Cleaned up means retain as much of the user's original response as possible, but remove filler words and improve readability.
- **Tracking Journaling Completion**:
  - Track which prompts have been answered for the day.
  - Consider journaling complete only when all three prompts (Desire, Gratitude, Brag) have been answered.

## UI & Styling Guidelines
- **User Feedback:**  
  - Use subtle animations (e.g., slide transitions) to indicate when the prompt changes.
  - Display an overlay message when the app auto-switches a prompt (e.g., "Switching to Gratitude").
- **Consistent Elements:**  
  - Maintain the card-based layout and font styles from earlier phases.
  - Use progress indicators to show journaling advancement (e.g., checkmarks on completed prompts).
- **Notification of Success/Error:**  
  - Use modal popups with clear messages.
  - Success modals: green accents; error modals: red accents.
- **Color Palette:**  
  - Background: #FFFFFF (white)  
  - Primary Accent: #007AFF (iOS blue)  
  - Text: #333333 (dark gray)  
- **Typography:**  
  - Font: San Francisco (iOS default)  
  - Headings: Bold, 20pt; Body: Regular, 16pt.
- **Layout:**  
  - Clean, minimal design with plenty of white space.
  - Use rounded corners for buttons and cards.
- **Visuals:**  
  - Use simple icons (e.g., microphone icon for recording) from SF Symbols.
  - Animations for transitions (fade in/out) for a smooth user experience.
- **Layout Enhancements:**  
  - Introduce a progress indicator or subtle animation while recording.
  - Use card-style views to display prompts and transcriptions.
- **Colors & Fonts:**  
  - Maintain Phase 1 color palette.
  - Use a slightly larger font for real-time transcription display (18pt, regular).
- **Interactive Elements:**  
  - Clearly styled "Retry" and "Save" buttons with a shadow effect for depth.
  - Visual feedback (e.g., change button color) when recording starts/stops.

## Design Patterns & Architecture
- **Strategy Pattern:**  
  Implement different strategies for prompt classification (e.g., one for detecting mixed responses and another for refining prompts).
- **Chain of Responsibility:**  
  Route the response through a series of handlers (e.g., check for "I don't know," mixed content, or clear prompt alignment) before final formatting.
- **Mediator Pattern:**  
  Coordinate between the AI engine, the UI, and the Notion integration without tightly coupling them.
 
 ## Dependencies & Configuration
- **Technologies**: 
  - Frontend: Swift (iOS app) 
  - Backend: FastAPI with LangGraph & LangSmith
  - LLM: Claude 3.5 Sonnet (via LangChain OpenAI integration)
  - APIs: Notion API
- **Environment Variables**:
  ```
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=<your-langsmith-api-key>
  OPENAI_API_KEY=<your-openai-api-key>
  NOTION_API_KEY=<your-notion-api-key>
  ```

## Architecture with LangGraph and LangSmith

### LangGraph Workflow Design
We'll implement the following LangGraph workflows:

1. **Routing Workflow**:
   - Analyze user input to classify which prompt category it belongs to
   - Route to appropriate handler based on classification
   - Switch prompts when necessary

2. **Prompt Chaining Workflow**:
   - Break down response processing into sequential steps
   - Handle transcription, classification, formatting, and storage as separate nodes

3. **Evaluator-Optimizer Workflow**:
   - When user seems stuck, evaluate their response
   - Generate refined prompts with better suggestions
   - Track effectiveness of refinements

### LangSmith Integration
We'll use LangSmith for:
- Tracing all interactions in development and production
- Creating datasets of sample responses for testing
- Evaluating the agent's classification and prompt refinement accuracy
- Continuous monitoring of production performance

## Implementation Checklist

### LangGraph Setup
- [ ] **Install Dependencies**:
  ```bash
  pip install langgraph langchain langchain-openai langsmith
  ```

- [ ] **Set Up Environment**:
  ```bash
  export LANGCHAIN_TRACING_V2=true
  export LANGCHAIN_API_KEY=<your-langsmith-api-key>
  export OPENAI_API_KEY=<your-openai-api-key>
  ```

- [ ] **Create State Definition**:
  ```python
  from typing import Annotated, TypedDict, List
  from langgraph.graph.message import add_messages
  
  class JournalState(TypedDict):
      # Messages have type "list". The add_messages function defines how this state key is updated
      messages: Annotated[list, add_messages]
      current_prompt: str  # "gratitude", "desire", or "brag"
      completed_prompts: List[str]
      formatted_responses: dict  # Stores cleaned responses for Notion
      user_stuck: bool  # Flag to indicate if user needs prompt refinement
  ```

- [ ] **Define Tools**:
  ```python
  from langchain_core.tools import tool
  
  @tool
  def save_to_notion(prompt_type: str, content: str) -> str:
      """Save the journal entry to Notion in the correct category."""
      # Implementation to save to Notion
      return "Successfully saved to Notion"
  
  @tool
  def get_completed_prompts() -> List[str]:
      """Get the list of prompts already completed today."""
      # Implementation to query Notion for completed prompts
      return ["desire"]  # Example return
  ```

- [ ] **Implement Classification Node**:
  ```python
  from langchain_openai import ChatOpenAI
  
  model = ChatOpenAI(model="claude-3-5-sonnet-20240620", temperature=0).bind_tools(tools)
  
  def classify_response(state: JournalState):
      messages = state['messages']
      current_prompt = state['current_prompt']
      
      # Add system message for classification
      classification_system_msg = f"""
      You are an AI assistant helping to classify journal responses.
      The current prompt is: {current_prompt}
      Determine if the user's response matches this prompt, or if it better matches one of:
      - gratitude (things the user is grateful for)
      - desire (things the user wants)
      - brag (things the user is proud of)
      
      Return the classification and confidence level.
      """
      
      # Get classification from model
      classification_result = model.invoke([
          {"role": "system", "content": classification_system_msg},
          messages[-1]  # The user's latest message
      ])
      
      # Parse the result to determine the true prompt type
      # Logic to extract the classification
      
      return {
          "classification": detected_prompt,
          "confidence": confidence_score
      }
  ```

- [ ] **Implement Prompt Switching Node**:
  ```python
  def handle_prompt_switch(state: JournalState):
      classification = state.get("classification", {})
      current_prompt = state["current_prompt"]
      detected_prompt = classification.get("prompt", current_prompt)
      confidence = classification.get("confidence", 0)
      
      if detected_prompt != current_prompt and confidence > 0.7:
          # Switch the prompt
          response = f"I notice you're talking about {detected_prompt} instead. Let's switch to that prompt."
          return {
              "messages": [{"role": "assistant", "content": response}],
              "current_prompt": detected_prompt
          }
      
      return {}  # No changes if no switch needed
  ```

- [ ] **Implement Prompt Refinement Node**:
  ```python
  def refine_prompt(state: JournalState):
      messages = state['messages']
      current_prompt = state['current_prompt']
      
      last_message = messages[-1]["content"].lower()
      stuck_phrases = ["i don't know", "not sure", "can't think", "um", "uh"]
      
      is_stuck = any(phrase in last_message for phrase in stuck_phrases)
      
      if is_stuck:
          # Generate refinement based on prompt type
          refinements = {
              "gratitude": "Let's break this down. Consider gratitude in these areas: health, relationships, career, or small daily joys.",
              "desire": "What about desires related to: personal growth, experiences you want to have, or changes you'd like to make?",
              "brag": "Think about recent accomplishments, challenges you've overcome, or personal strengths you've displayed."
          }
          
          return {
              "messages": [{"role": "assistant", "content": refinements[current_prompt]}],
              "user_stuck": True
          }
      
      return {"user_stuck": False}
  ```

- [ ] **Implement Response Formatting Node**:
  ```python
  def format_response(state: JournalState):
      messages = state['messages']
      current_prompt = state['current_prompt']
      
      # Get all user messages for the current prompt
      user_messages = [m["content"] for m in messages if m["role"] == "user"]
      
      # Format the combined response
      formatting_system_msg = """
      Clean up this journal response while preserving the original sentiment and content.
      Remove filler words, fix grammar, and improve readability.
      Keep the personal tone and all important details.
      """
      
      formatted_response = model.invoke([
          {"role": "system", "content": formatting_system_msg},
          {"role": "user", "content": " ".join(user_messages)}
      ])
      
      # Update the formatted responses dictionary
      formatted_responses = state.get("formatted_responses", {})
      formatted_responses[current_prompt] = formatted_response.content
      
      return {"formatted_responses": formatted_responses}
  ```

- [ ] **Define State Graph Conditions**:
  ```python
  def should_switch_prompt(state: JournalState) -> str:
      classification = state.get("classification", {})
      if classification.get("prompt") != state["current_prompt"] and classification.get("confidence", 0) > 0.7:
          return "handle_prompt_switch"
      return "continue_current_prompt"
  
  def should_refine_prompt(state: JournalState) -> str:
      messages = state['messages']
      last_message = messages[-1]["content"].lower()
      stuck_phrases = ["i don't know", "not sure", "can't think", "um", "uh"]
      
      if any(phrase in last_message for phrase in stuck_phrases):
          return "refine_prompt"
      return "format_response"
  
  def is_ready_to_save(state: JournalState) -> str:
      if state.get("user_confirmed_save", False):
          return "save_to_notion"
      return "ask_for_confirmation"
  ```

- [ ] **Create and Compile the Graph**:
  ```python
  from langgraph.graph import StateGraph, END
  
  # Create the graph
  workflow = StateGraph(JournalState)
  
  # Add nodes
  workflow.add_node("classify_response", classify_response)
  workflow.add_node("handle_prompt_switch", handle_prompt_switch)
  workflow.add_node("continue_current_prompt", continue_with_current)
  workflow.add_node("refine_prompt", refine_prompt)
  workflow.add_node("format_response", format_response)
  workflow.add_node("ask_for_confirmation", ask_user_confirmation)
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
  
  # Format then confirm
  workflow.add_edge("format_response", "ask_for_confirmation")
  
  # Conditional edges for saving
  workflow.add_conditional_edges(
      "ask_for_confirmation",
      is_ready_to_save,
      {
          "save_to_notion": "save_to_notion",
          "ask_for_confirmation": "classify_response"  # Loop back if not confirmed
      }
  )
  
  # Save and end
  workflow.add_edge("save_to_notion", END)
  
  # Compile the graph
  app = workflow.compile()
  ```

### LangSmith Setup and Integration
- [ ] **Create Evaluation Dataset**:
  ```python
  from langsmith import Client
  
  client = Client()
  
  # Create a dataset of example journal responses
  example_inputs = [
      {"text": "I'm grateful for my family's support during tough times", "expected_prompt": "gratitude"},
      {"text": "I want to travel more this year", "expected_prompt": "desire"},
      {"text": "I'm proud that I finished that big project at work", "expected_prompt": "brag"},
      {"text": "I don't know what I'm grateful for today", "expected_prompt": "gratitude", "needs_refinement": True},
      # Add more diverse examples including mixed content
  ]
  
  dataset = client.create_dataset(
      "journal_classification",
      description="Test dataset for journal prompt classification",
  )
  
  for example in example_inputs:
      client.create_example(
          inputs={"text": example["text"]},
          outputs={"prompt": example["expected_prompt"]},
          dataset_id=dataset.id
      )
  ```

- [ ] **Set Up Evaluation**:
  ```python
  from langsmith import evaluation
  
  # Define a custom evaluator for classification accuracy
  def classification_accuracy(run, example):
      expected = example.outputs.get("prompt")
      actual = run.outputs.get("classification", {}).get("prompt")
      return {
          "score": 1.0 if expected == actual else 0.0,
          "reasoning": f"Expected {expected}, got {actual}"
      }
  
  # Run the evaluation
  eval_results = evaluation.evaluate(
      classify_response,  # The node to evaluate
      dataset_name="journal_classification",
      evaluators=[classification_accuracy]
  )
  ```

- [ ] **Add Tracing to Production**:
  ```python
  # In your FastAPI backend
  from langsmith import traceable
  
  @app.post("/process_journal")
  @traceable(run_type="chain")
  async def process_journal(request: JournalRequest):
      # Process with the LangGraph workflow
      result = app.invoke({
          "messages": [{"role": "user", "content": request.transcription}],
          "current_prompt": request.current_prompt,
          "completed_prompts": request.completed_prompts,
          "formatted_responses": {},
          "user_stuck": False
      })
      
      return {"result": result}
  ```

### FastAPI Backend Implementation
- [ ] **Create API Endpoints**:
  ```python
  from fastapi import FastAPI, HTTPException
  from pydantic import BaseModel
  from typing import List, Optional
  
  app = FastAPI()
  
  class JournalRequest(BaseModel):
      transcription: str
      current_prompt: str
      completed_prompts: List[str]
  
  class JournalResponse(BaseModel):
      detected_prompt: str
      prompt_changed: bool
      formatted_response: str
      needs_refinement: bool
      refinement_suggestion: Optional[str] = None
      saved_to_notion: bool
  
  @app.post("/process_journal", response_model=JournalResponse)
  async def process_journal(request: JournalRequest):
      try:
          # Initialize the journal state
          initial_state = {
              "messages": [{"role": "user", "content": request.transcription}],
              "current_prompt": request.current_prompt,
              "completed_prompts": request.completed_prompts,
              "formatted_responses": {},
              "user_stuck": False
          }
          
          # Run the LangGraph workflow
          result = app.invoke(initial_state)
          
          # Extract relevant information
          return JournalResponse(
              detected_prompt=result["current_prompt"],
              prompt_changed=result["current_prompt"] != request.current_prompt,
              formatted_response=result["formatted_responses"].get(result["current_prompt"], ""),
              needs_refinement=result["user_stuck"],
              refinement_suggestion=result["messages"][-1]["content"] if result["user_stuck"] else None,
              saved_to_notion=result.get("saved_to_notion", False)
          )
      
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  ```

## Flow Diagrams

### **Sequence Diagram**
See [Phase 4 Sequence Diagram](./diagrams/phase_4_sequence_diagram.md)

### **Flow Diagram**
See [Phase 4 Flow Diagram](./diagrams/phase_4_flow_diagram.md)

### **Backend and LangGraph Flow Diagram**
See [Phase 4 LangGraph Flow Diagram](./diagrams/phase_4_langgraph_flow_diagram.md)

## Dependencies & Configuration
- **Technologies**: Swift (iOS app), FastAPI (backend), LangChain, OpenAI API (for classification & formatting), Notion API.
- **Permissions Needed**:
  - `NSMicrophoneUsageDescription` (for voice input)
  - `NSSpeechRecognitionUsageDescription` (for speech-to-text)
  - `NSUserNotificationUsageDescription` (for reminders)
  - Notion API authentication key.

---

This phase makes the journaling experience much more adaptive and intelligent.

**[Home](../README.md) | [Previous: Phase 3](./phase_3.md)**


