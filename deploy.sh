#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying CVBoost function to AWS Lambda...${NC}"

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo -e "${RED}Serverless Framework is not installed. Installing...${NC}"
    npm install -g serverless
    
    # Verify installation was successful
    if ! command -v serverless &> /dev/null; then
        echo -e "${RED}Failed to install Serverless Framework. Please install it manually.${NC}"
        exit 1
    fi
fi

# Check if AWS credentials are configured
if ! serverless config credentials --provider aws --key test --secret test 2>&1 | grep -q "overwrite"; then
    echo -e "${RED}AWS credentials are not configured. Please configure them:${NC}"
    echo "serverless config credentials --provider aws --key YOUR_ACCESS_KEY --secret YOUR_SECRET_KEY"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}The .env file does not exist. Creating an example...${NC}"
    echo "OPENAI_API_KEY=your_openai_api_key" > .env
    echo -e "${YELLOW}Please edit the .env file with your own values.${NC}"
    exit 1
fi

# Check if OPENAI_API_KEY is set in .env
if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=your_openai_api_key" .env; then
    echo -e "${RED}OPENAI_API_KEY is not properly set in .env file.${NC}"
    echo -e "${YELLOW}Please edit the .env file with your actual OpenAI API key.${NC}"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Check if pip install was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Please check the errors above.${NC}"
    exit 1
fi

# Deploy to AWS
echo -e "${YELLOW}Deploying to AWS...${NC}"
serverless deploy

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${YELLOW}You can now use the API URL provided above to call the function.${NC}"
    echo -e "${YELLOW}The function will automatically detect the language of the resume content.${NC}"
else
    echo -e "${RED}Deployment failed. Please check the errors above.${NC}"
    exit 1
fi

echo -e "${GREEN}All done!${NC}" 