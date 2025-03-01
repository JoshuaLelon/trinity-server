#!/bin/bash
# Trinity Journaling App Setup Script
# This script helps set up the Trinity Journaling App using Anaconda

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Trinity Journaling App Setup Script${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Conda is not installed or not in your PATH.${NC}"
    echo -e "Please install Anaconda or Miniconda first:"
    echo -e "${YELLOW}https://docs.conda.io/en/latest/miniconda.html${NC}"
    exit 1
fi

echo -e "\n${GREEN}Conda is installed! Creating environment...${NC}"

# Create the conda environment
conda create -y -n trinity python=3.11

# Check if environment creation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create conda environment.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Environment created! Activating environment...${NC}"

# Activate the environment (this works differently in scripts)
eval "$(conda shell.bash hook)"
conda activate trinity

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate conda environment.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Environment activated! Installing dependencies...${NC}"

# Install dependencies
pip install -r requirements.txt

# Check if pip install was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Dependencies installed!${NC}"

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "\n${YELLOW}Creating .env file from example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}Please edit the .env file with your API keys before running the server.${NC}"
    else
        echo -e "\n${RED}.env.example file not found. Please create a .env file manually.${NC}"
    fi
else
    echo -e "\n${GREEN}.env file already exists.${NC}"
fi

echo -e "\n${BLUE}======================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "\nTo activate the environment in the future, run:"
echo -e "${YELLOW}conda activate trinity${NC}"
echo -e "\nTo run the server, use:"
echo -e "${YELLOW}python run.py${NC}"
echo -e "\nTo test the API, use:"
echo -e "${YELLOW}python test_api.py${NC}"
echo -e "\nFor more information, see the documentation files:"
echo -e "${YELLOW}README.md${NC}"
echo -e "${YELLOW}getting_started.md${NC}"
echo -e "${YELLOW}anaconda_setup.md${NC}" 