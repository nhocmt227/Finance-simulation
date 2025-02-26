:: Remove .env file if not exist
if exist .env del .env

:: Create an environment file
type nul > .env

:: setup environment variables
echo API_KEY=892RLERUEOGSNP0C >> .env
echo DATABASE = "finance.db" >> .env
echo API_TIME_TO_UPDATE = "86400" >> .env

:: initialize the database
python init_db.py