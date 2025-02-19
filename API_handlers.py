from dotenv import load_dotenv

# take environment variables from .env.
load_dotenv()  
# Retrieve the API key
api_key = os.getenv("API_KEY")

