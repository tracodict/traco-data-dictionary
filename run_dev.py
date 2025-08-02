#!/usr/bin/env python3
"""
Local development server for the FIX Dictionary API
"""
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import uvicorn
    from api.main import app
    
    if __name__ == "__main__":
        print("Starting FIX Dictionary API server...")
        print("API Documentation will be available at: http://localhost:8000/docs")
        print("API Root: http://localhost:8000/")
        print()
        
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
except ImportError:
    print("FastAPI and uvicorn are required for local development.")
    print("Install them with: uv pip install fastapi uvicorn")
    print("Or with pip: pip install fastapi uvicorn")
    print()
    print("To install uv (recommended for faster package management):")
    print("curl -LsSf https://astral.sh/uv/install.sh | sh")
    print()
    print("For production deployment to Vercel, use: vercel --prod")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
