# Trinity Journaling App Product Requirements Document

## 1. Executive Summary
This journaling app is designed to help users develop a consistent journaling habit through scheduled notifications, voice-based input, and intelligent prompt management. The app guides the user through three key prompts—Desire, Gratitude, and Brag—by automatically initiating voice recording and dynamically adapting to the user's input. Journal entries are ultimately sent to Notion, ensuring users have an external, structured record of their daily reflections.

## 2. Problem Statement & Objectives
**Problem Statement:**  
Many people struggle with maintaining a daily journaling habit due to time constraints, lack of motivation, or difficulty in organizing their thoughts. Users need an app that not only reminds them to journal but also simplifies the journaling process through voice input and intelligent guidance.

**Objectives:**
- Ensure users receive timely reminders to journal each day.
- Provide an intuitive interface that minimizes friction by auto-starting voice recording.
- Utilize AI to adaptively switch prompts or refine questions when users are stuck.
- Seamlessly store entries in Notion, enabling users to track their progress over time.
- Lay a robust foundation for future feature enhancements.

## 3. User Personas & Use Cases
**User Personas:**
- **Busy Professional:**  
  Needs quick, voice-based journaling during a hectic day. Values simplicity and automated prompts.
- **Self-Improver:**  
  Enjoys daily reflection and seeks insights into personal growth. Prefers a guided, adaptive journaling experience.
- **Tech-Savvy Organizer:**  
  Uses multiple apps to manage life and productivity. Prefers integration with tools like Notion for centralized note-keeping.

**Use Cases:**
- **Morning Routine:**  
  The user receives a notification at 8 AM, opens the app, and begins a voice journaling session.
- **Flexible Session Management:**  
  The app auto-starts recording, transcribes speech, and, if needed, refines the prompt based on voice input.
- **Notion Integration:**  
  Completed entries for Desire, Gratitude, and Brag are automatically formatted and sent to the user's Notion daily note.
- **Adaptive Interaction:**  
  If the user mixes response types or indicates confusion, the app intelligently adapts, ensuring clarity and ease-of-use.

## 4. Feature Requirements
- **Journaling Prompts:**  
  - Three key prompts: Desire, Gratitude, Brag.
  
- **Voice Recording & Transcription:**  
  - Automatic start of recording upon app launch.
  - Real-time transcription using Apple's built-in speech-to-text API.
  - Retry mechanism for failed transcriptions.

- **Notification Scheduling & Reminder Logic:**  
  - Initial notification at 8 AM.
  - Reminders every 30 minutes until 10 PM, if journaling remains incomplete.
  - Intelligent cessation of reminders upon journaling completion.

- **Notion API Integration:**  
  - Map each journaling prompt to corresponding fields in the Notion daily note.
  - Confirmation messages upon successful upload; error handling for connectivity issues.

- **AI-Powered Prompt Classification & Switching:**  
  - Use an AI engine to classify voice responses.
  - Dynamically switch or refine prompts based on detected content.
  - Format transcriptions to remove filler words and improve readability.

## 5. User Experience (UX) & Interface (UI) Design
**Visual Style & Branding:**
- **Color Palette:**  
  - Background: White (#FFFFFF)  
  - Primary Accent: iOS Blue (#007AFF)  
  - Text: Dark Gray (#333333)

- **Typography:**  
  - Use San Francisco font (default for iOS).  
  - Headings at 20pt, bold; body text at 16pt regular; real-time transcription at 18pt for clarity.

- **Layout & Components:**  
  - Clean, minimal design with generous white space.
  - Card-style views with rounded corners for displaying prompts and transcriptions.
  - Use SF Symbols for icons (e.g., microphone for recording, checkmarks for completion).
  - Interactive buttons (e.g., "Retry", "Save") with subtle shadow effects and animations (e.g., fade, slide transitions).

**Interaction Flow:**
- User opens the app and sees a clear, card-based prompt.
- Auto-initiated voice recording with a progress indicator.
- Real-time transcription appears on-screen with options to edit, retry, or save.
- Success and error modals are used to confirm actions (styled with green accents for success and red for errors).

## 6. Technical Architecture & Design Patterns
**Tech Stack:**
- **Frontend:**  
  - iOS app built in Swift using either UIKit or SwiftUI.
  - Apple's Speech Framework for transcription.
  - Local Notifications for reminders.

- **Backend:**  
  - FastAPI (Python) hosted on AWS EC2 for handling AI logic and acting as a proxy for Notion API calls.
  - LangGraph for building the workflow that handles prompt classification, switching, and refinement

- **Third-Party Integrations:**  
  - Notion API for storing journal entries.
  - OpenAI API (or similar) for AI-powered prompt classification and text formatting.

**Design Patterns:**
- **MVC (Model-View-Controller):**  
  - Clean separation of concerns between UI, business logic, and data storage.
- **Singleton:**  
  - For managing notifications and Notion API configurations.
- **Observer:**  
  - To update the UI in response to changes in the journaling state (e.g., new transcription).
- **State Pattern:**  
  - Manage journaling session states (Idle, Recording, Transcribing, Completed) for smooth UI transitions.
- **Strategy & Chain of Responsibility:**  
  - For AI classification, enabling different strategies to handle mixed inputs or unclear responses.

## 7. Data Model & API Contracts
**Data Model:**
```swift
struct JournalEntry: Codable {
    let date: String
    let gratitude: [String]
    let desire: [String]
    let brag: [String]
}
```

**API Contracts:**
- **Notion Integration Request:**
  ```json
  POST /send_to_notion
  {
    "date": "2025-03-01",
    "gratitude": ["I am grateful for my health."],
    "desire": ["I want a new job."],
    "brag": ["I completed a major project."]
  }
  ```
- **AI Classification Request:**
  ```json
  POST /classify_response
  {
    "text": "I am grateful for my health, but I also want a new job."
  }
  ```
- **AI Classification Response:**
  ```json
  {
    "prompt": "gratitude",
    "formattedResponse": "I am grateful for my health. I also want a new job."
  }
  ```

## 8. Milestones & Roadmap
**Phase 1: Basic Local-Only Journaling App**
- Set up Xcode project, configure permissions, and implement basic UI.
- Integrate local notifications and Apple's Speech Framework.
- Implement in-memory storage for journal entries.
- [View detailed Phase 1 documentation](./docs/phase_1.md)

**Phase 2: Auto-Start Recording & Improved UI**
- Auto-start voice recording on app launch.
- Enhance UI with real-time transcription, animated indicators, and edit options.
- Implement retry logic for transcription errors.
- [View detailed Phase 2 documentation](./docs/phase_2.md)

**Phase 3: Notion Integration (Basic)**
- Develop a Notion API client using a Facade pattern.
- Map journal entries to Notion's daily note format.
- Provide user feedback on successful uploads and error handling.
- [View detailed Phase 3 documentation](./docs/phase_3.md)

**Phase 4: AI-Powered Prompt Switching & Formatting**
- Integrate AI for prompt classification via a backend endpoint.
- Implement dynamic prompt switching and adaptive refinement.
- Format responses using Strategy and Chain of Responsibility patterns.
- [View detailed Phase 4 documentation](./docs/phase_4.md)

## 9. Future Enhancements
- **Enhanced Data Visualization:**  
  Provide analytics and insights based on the user's journaling history (e.g., mood trends, recurring themes).
- **Customizable Prompts:**  
  Allow users to create or modify prompts based on their personal growth areas.
- **Auto-Tagging & Sentiment Analysis:**  
  Integrate additional AI features to auto-tag entries and perform sentiment analysis.
- **Offline Capabilities:**  
  Enable local storage and later syncing when internet connectivity is restored.
- **Cross-Platform Support:**  
  Develop web or Android versions of the app for a seamless cross-device journaling experience.

## 10. Documentation Structure
All diagrams for the project are stored in the `docs/diagrams/` directory for better organization and maintainability. Each phase documentation references these diagrams instead of embedding them directly.