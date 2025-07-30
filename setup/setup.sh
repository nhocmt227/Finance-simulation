#!/bin/bash

# # Remove .env file if it exists
# if [ -f .env ]; then
#   rm .env
# fi

# # Create an environment file using touch
# touch .env

# # Setup environment variables. this API is just a testing API
# echo "API_KEY_ALPHA_VANTAGE=XXXXXXXXXXXX" >> .env
# echo "API_KEY_FINNHUB=XXXXXXXXXXXX" >> .env
# echo "API_KEY_TWELVE_DATA=XXXXXXXXXXXX" >> .env

# Set PYTHONPATH so Python can find the internal package
export PYTHONPATH=.

# Initialize the database
python setup/init_db.py
