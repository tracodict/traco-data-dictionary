import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional, Union
import logging

from models import *
from parser import FIXDictionaryParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize parser on module load for Vercel
def init_parser():
    # Try to load from current directory first, then from resources
    resources_path = "resources/dict"
    if not os.path.exists(resources_path):
        resources_path = "/home/data/git/tracodict/resources/dict"
    
    if not os.path.exists(resources_path):
        # Try relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_path = os.path.join(os.path.dirname(current_dir), "resources", "dict")
    
    if not os.path.exists(resources_path):
        logger.error(f"Resources path not found: {resources_path}")
        raise RuntimeError("FIX dictionary resources not found")
    
    logger.info(f"Loading FIX dictionary from: {resources_path}")
    return FIXDictionaryParser(resources_path)

# Global parser instance - initialize immediately for Vercel
fix_parser = init_parser()
logger.info("FIX Dictionary Service started successfully")

app = FastAPI(
    title="FIX Dictionary API",
    description="""
    A REST API service for FIX Protocol Dictionary data, providing FIXimate-like functionality.
    
    This service provides access to FIX protocol messages, fields, components, enums, and other dictionary data
    across multiple FIX versions (FIX.4.4, FIX.5.0SP2, and FIX.Z).
    
    ## Features
    
    - **Search**: Find messages, fields, components, and enums by name or description
    - **Browse**: List all entities by category or type  
    - **Details**: Get comprehensive information about specific entities
    - **Multi-version**: Support for multiple FIX protocol versions
    - **Regular Expressions**: Advanced search with regex support
    
    ## FIX Versions Supported
    - FIX.4.4
    - FIX.5.0SP2
    - FIX.Z
    """,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Copy all the endpoint definitions from the original main.py
# This is a simplified version for Vercel compatibility
