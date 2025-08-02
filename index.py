import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the FastAPI app
from api.main import app

# For Vercel deployment, the app must be accessible
# This is the ASGI application that Vercel will run
