import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Unified configuration for the Statement Parser."""
    
    @staticmethod
    def _get_val(key, default):
        # Try Streamlit secrets first if we are in a streamlit context
        try:
            import streamlit as st
            if key in st.secrets:
                return st.secrets[key]
        except:
            pass
        
        # Fallback to environment variables
        return os.getenv(key, default)

    def __init__(self):
        self.PORT = int(self._get_val("PORT", 8000))
        self.HOST = self._get_val("HOST", "0.0.0.0")
        self.API_KEY = str(self._get_val("API_KEY", "1234567890"))
        self.DEBUG = str(self._get_val("DEBUG", "False")).lower() == "true"

# Single instance to be used across the app
config = Config()
