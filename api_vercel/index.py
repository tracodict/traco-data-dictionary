import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the FastAPI app
from api.main import app

# Vercel serverless function handler
def handler(request):
    return app
