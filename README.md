# Trinity Journaling App Backend

This is the backend server for the Trinity Journaling App, designed to provide intelligent journal prompt classification, processing, and storage with Notion integration.

## Features

- **AI-Powered Prompt Classification**: Intelligently classifies user responses into the correct prompt type (Gratitude, Desire, or Brag)
- **Dynamic Prompt Switching**: Detects when a user is responding to a different prompt and switches context accordingly
- **Prompt Refinement**: Offers guidance when users are stuck on a response
- **Response Formatting**: Cleanly formats user responses for improved readability
- **Notion Integration**: Stores journal entries in a structured Notion database

## Technology Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **LangGraph**: Framework for building structured LLM workflows
- **LangChain**: LLM application development framework
- **Anthropic Claude 3.5 Sonnet**: Advanced LLM for intelligent response processing
- **LangSmith**: Tracing and monitoring for LLM applications
- **Notion API**: Integration for storing journal entries

## Architecture

The backend follows a simple but effective design based on the principles outlined in [Anthropic's article on building effective agents](https://www.anthropic.com/research/building-effective-agents):

1. **Simple Building Blocks**: We use a straightforward workflow pattern where each step has a clearly defined purpose
2. **Transparency**: Each step in the processing pipeline is traceable and explainable
3. **Well-Documented Tools**: The Notion integration and LLM interactions are carefully documented

## Getting Started

### Prerequisites

- Anaconda or Miniconda
- Notion account with API access
- Anthropic API key
- LangSmith account (optional, for tracing)

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/trinity-server.git
   cd trinity-server
   ```

2. Create a conda environment:
   ```bash
   conda create -n trinity python=3.11
   conda activate trinity
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys and configuration.

### Running Locally

Start the development server:
```bash
python run.py
```

The API will be available at http://localhost:8000

### Additional Setup Documentation

For more detailed instructions, see the following docs:

- [Getting Started Guide](getting_started.md) - Quick start guide for setting up the project
- [Anaconda Setup Guide](anaconda_setup.md) - Detailed guide for using Anaconda
- [Deployment Guide](deployment.md) - Instructions for deploying to EC2

You can also use our automatic setup script:

```bash
# Make the script executable (if needed)
chmod +x setup_trinity.sh

# Run the setup script
./setup_trinity.sh
```

## API Endpoints

### Journal Processing

- **POST** `/api/v1/journal/process`: Process a journal entry
  - Request body:
    ```json
    {
      "transcription": "I'm grateful for my family",
      "current_prompt": "gratitude",
      "completed_prompts": []
    }
    ```
  - Response:
    ```json
    {
      "detected_prompt": "gratitude",
      "prompt_changed": false,
      "formatted_response": "I'm grateful for my family and their support.",
      "needs_refinement": false,
      "refinement_suggestion": null,
      "saved_to_notion": true
    }
    ```

### Health Check

- **GET** `/api/v1/health`: Check server health

## Deployment to EC2

### Setup EC2 Instance

1. Launch an EC2 instance with Amazon Linux 2 or Ubuntu
2. Install Anaconda/Miniconda:
   ```bash
   # Download Miniconda
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
   
   # Install Miniconda
   bash ~/miniconda.sh -b -p $HOME/miniconda
   
   # Initialize conda
   eval "$($HOME/miniconda/bin/conda shell.bash hook)"
   
   # Add conda to path permanently
   echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
   ```

3. Set up the application:
   ```bash
   git clone https://github.com/your-username/trinity-server.git
   cd trinity-server
   conda create -n trinity python=3.11
   conda activate trinity
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Configure systemd Service

Create a systemd service to run the application:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/trinity-server.service
   ```

2. Add the following content:
   ```
   [Unit]
   Description=Trinity Journaling App Backend
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/trinity-server
   # Set up conda environment
   ExecStart=/bin/bash -c 'source /home/ec2-user/miniconda/bin/activate && conda activate trinity && python run.py'
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable trinity-server
   sudo systemctl start trinity-server
   ```

4. Check the status:
   ```bash
   sudo systemctl status trinity-server
   ```

### Configure Nginx (Optional)

If you want to use Nginx as a reverse proxy:

1. Install Nginx:
   ```bash
   sudo yum install nginx -y  # Amazon Linux
   # or
   sudo apt install nginx -y  # Ubuntu
   ```

2. Configure Nginx:
   ```bash
   sudo nano /etc/nginx/conf.d/trinity-server.conf
   ```

3. Add the following:
   ```
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. Enable and start Nginx:
   ```bash
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

## Monitoring and Debugging

- View logs using systemd:
  ```bash
  sudo journalctl -u trinity-server -f
  ```
- Monitor LLM performance via the LangSmith dashboard
- Check application health via the health endpoint


