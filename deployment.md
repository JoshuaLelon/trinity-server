# Deploying Trinity Journaling App Backend to EC2

This guide provides step-by-step instructions for deploying the Trinity Journaling App backend to an AWS EC2 instance using Anaconda.

## Prerequisites

- An AWS account with EC2 access
- Basic familiarity with SSH and command line
- A domain name (optional, for using HTTPS)

## Step 1: Launch an EC2 Instance

1. Login to the AWS Management Console
2. Navigate to EC2 service
3. Click "Launch Instance"
4. Choose an Amazon Machine Image (AMI)
   - Recommended: Amazon Linux 2023 or Ubuntu 22.04
   - Instance type: t2.micro (free tier) or t2.small
5. Configure security groups:
   - SSH (Port 22) from your IP
   - HTTP (Port 80) from anywhere
   - HTTPS (Port 443) from anywhere
   - Custom TCP (Port 8000) from anywhere (if not using Nginx)
6. Create or select an existing key pair
7. Launch the instance

## Step 2: Connect to Your Instance

```bash
ssh -i /path/to/your-key.pem ec2-user@your-instance-public-dns
# Or for Ubuntu
# ssh -i /path/to/your-key.pem ubuntu@your-instance-public-dns
```

## Step 3: Install Miniconda

```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

# Install Miniconda
bash ~/miniconda.sh -b -p $HOME/miniconda

# Initialize conda
eval "$($HOME/miniconda/bin/conda shell.bash hook)"

# Add conda to path permanently
echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install git
sudo dnf install git -y  # For Amazon Linux
# or
# sudo apt install git -y  # For Ubuntu
```

## Step 4: Clone and Configure the Application

```bash
# Clone the repository
git clone https://github.com/your-username/trinity-server.git
cd trinity-server

# Create a conda environment
conda create -n trinity python=3.11
conda activate trinity

# Install dependencies
pip install -r requirements.txt

# Create and edit the .env file
cp .env.example .env
nano .env
```

Fill in your API keys and settings in the .env file:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=trinity-journal

ANTHROPIC_API_KEY=your_anthropic_api_key

NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id

LLM_MODEL=claude-3-5-sonnet-20240620
LLM_TEMPERATURE=0.0
```

## Step 5: Run the Application with systemd

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/trinity-server.service
```

Add the following content (adjust paths as needed):

```
[Unit]
Description=Trinity Journaling App Backend
After=network.target

[Service]
User=ec2-user  # Change to ubuntu for Ubuntu instances
WorkingDirectory=/home/ec2-user/trinity-server
ExecStart=/bin/bash -c 'source /home/ec2-user/miniconda/bin/activate && conda activate trinity && python run.py'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trinity-server
sudo systemctl start trinity-server
```

Check if the service is running:

```bash
sudo systemctl status trinity-server
```

## Step 6: Configure Nginx (Optional, but Recommended)

If you want to use a custom domain and HTTPS, install and configure Nginx:

```bash
# For Amazon Linux
sudo dnf install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# For Ubuntu
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

Create a Nginx configuration file:

```bash
sudo nano /etc/nginx/conf.d/trinity-server.conf
```

Add the following configuration:

```
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test and restart Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Set Up SSL with Certbot (Optional)

Install Certbot:

```bash
# For Amazon Linux
sudo dnf install certbot python3-certbot-nginx -y

# For Ubuntu
sudo apt install certbot python3-certbot-nginx -y
```

Obtain and install SSL certificate:

```bash
sudo certbot --nginx -d your-domain.com
```

## Step 8: Monitoring and Maintenance

View logs:

```bash
# View systemd logs
sudo journalctl -u trinity-server -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

Updating the application:

```bash
cd ~/trinity-server
git pull
conda activate trinity
pip install -r requirements.txt
sudo systemctl restart trinity-server
```

## Troubleshooting

- **Service won't start**: Check logs with `sudo journalctl -u trinity-server -e`
- **Can't connect to the API**: Ensure security groups allow traffic on port 80/443/8000
- **SSL certificate issues**: Ensure your domain's DNS is properly configured to point to your EC2 instance
- **Conda environment issues**: Make sure the conda environment is correctly activated in the systemd service file

## Security Considerations

- Keep your system and packages up to date
- Consider using AWS IAM roles instead of keys when possible
- Restrict your security groups to only necessary traffic
- Use environment variables for secrets, not hardcoded values
- Consider setting up a firewall with `ufw` (Ubuntu) or `firewalld` (Amazon Linux) 