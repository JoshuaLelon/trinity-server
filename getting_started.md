# Getting Started with Trinity Journaling App

This quick start guide will help you set up and run the Trinity Journaling App backend on your local machine using Anaconda.

## Prerequisites

Before you begin, make sure you have:

- Anaconda or Miniconda installed ([download here](https://docs.conda.io/en/latest/miniconda.html))
- Git installed
- API keys for:
  - Anthropic (Claude API)
  - Notion
  - LangSmith (optional, for tracing)

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/trinity-server.git
cd trinity-server
```

## Step 2: Set Up Anaconda Environment

```bash
# Create a new conda environment for the project
conda create -n trinity python=3.11

# Activate the environment
conda activate trinity

# Install required packages
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

```bash
# Create .env file from example
cp .env.example .env

# Edit the .env file with your actual API keys
nano .env  # or use any text editor
```

Your `.env` file should contain:

```
# LangChain and LangSmith (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=trinity-journal

# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key

# Notion
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id

# LLM Settings
LLM_MODEL=claude-3-5-sonnet-20240620
LLM_TEMPERATURE=0.0
```

## Step 4: Run the Server

```bash
# Make sure your conda environment is activated
conda activate trinity

# Start the server
python run.py
```

The server will start at http://localhost:8000

## Step 5: Test the API

You can test the API using the included test script:

```bash
python test_api.py
```

Or use a tool like curl or Postman to make requests to the API endpoints:

```bash
# Example: Check server health
curl http://localhost:8000/api/v1/health

# Example: Process a journal entry
curl -X POST http://localhost:8000/api/v1/journal/process \
  -H "Content-Type: application/json" \
  -d '{"transcription": "I am grateful for my health", "current_prompt": "gratitude", "completed_prompts": []}'
```

## API Endpoints

- `GET /api/v1/health`: Check server health
- `GET /api/v1/journal/completed-prompts`: Get list of completed prompts 
- `POST /api/v1/journal/process`: Process a journal entry

## Notion Setup

To use the Notion integration:

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Create a database in Notion with these columns:
   - `Type` (Select: options for gratitude, desire, brag)
   - `Content` (Text)
   - `Date` (Date)
3. Share your database with the integration
4. Copy your database ID from the URL (the part after the workspace name and before the question mark)

## Troubleshooting

- **API key issues**: Ensure your keys are correct in the `.env` file
- **Conda environment problems**: Try `conda deactivate` and then `conda activate trinity`
- **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **Server connection issues**: Ensure no other process is using port 8000

## Next Steps

- Explore the Langsmith dashboard to see traces of your journal processing
- Check the Notion database to see saved journal entries
- Review the codebase to understand the journal processing workflow 