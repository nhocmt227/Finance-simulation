:: Remove .env file if not exist
:: if exist .env del .env

:: Create an environment file
:: type nul > .env

:: setup environment variables. this API is just a testing API
:: echo "API_KEY_ALPHA_VANTAGE=XXXXXXXXXXXX" >> .env 
:: echo "API_KEY_FINNHUB=XXXXXXXXXXXX" >> .env
:: echo "API_KEY_TWELVE_DATA=XXXXXXXXXXXX" >> .env

:: Set PYTHONPATH so Python can find the internal package
set PYTHONPATH=.

:: initialize the database
python setup/init_db.py