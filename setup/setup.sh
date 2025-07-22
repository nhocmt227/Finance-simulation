#!/bin/bash

# Remove .env file if it exists
if [ -f .env ]; then
  rm .env
fi

# Create an environment file using touch
touch .env

# Setup environment variables. this API is just a testing API
echo "API_KEY=892RLERUEOGSNP0C" >> .env
echo "DATABASE=finance.db" >> .env
echo "API_TIME_TO_UPDATE=86400" >> .env

# Set PYTHONPATH so Python can find the internal package
export PYTHONPATH=.

# Initialize the database
python setup/init_db.py
