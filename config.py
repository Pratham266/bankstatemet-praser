import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Unified configuration for the Statement Parser."""
    
    # Server Settings
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # Security
    API_KEY = os.getenv("API_KEY", "1234567890")
    
    # App Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Single instance to be used across the app
config = Config()
