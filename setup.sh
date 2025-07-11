#!/bin/bash

# Step 1: Create virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
else
  echo ".venv already exists."
fi

# Step 2: Activate virtual environment
source .venv/bin/activate
echo "Environment activated."

# Step 3: Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
  echo "Creating .env file..."
  echo "GROQ_API_KEY=" > .env
  echo "DISCORD_BOT_TOKEN=" >> .env
  echo ".env file created with placeholder keys."
else
  echo ".env file already exists."
fi

# Step 4 (Optional): Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi

echo "Setup complete!"
