#!/bin/bash

# Remove .env file if it exists
if [ -f .env ]; then
  rm .env
fi

# Create an environment file using touch
touch .env

# Setup environment variables
echo "API_KEY=892RLERUEOGSNP0C" >> .env
echo "DATABASE=finance.db" >> .env
echo "API_TIME_TO_UPDATE=86400" >> .env

# Initialize the database
python init_db.py
