import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from typing import List, Optional, Union, Dict, Any
import logging
from contextlib import asynccontextmanager
import pandas as pd

from models import *
from parser import FIXDictionaryParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global parser instance
fix_parser: Optional[FIXDictionaryParser] = None

def init_parser():
    """Initialize the FIX parser - called on module import for Vercel compatibility"""
    global fix_parser
    if fix_parser is not None:
        return fix_parser
        
    logger.info("Starting FIX Dictionary Service...")
    
    # Try to load from current directory first, then from resources
    resources_path = "resources/dict"
    if not os.path.exists(resources_path):
        resources_path = "/home/data/git/tracodict/resources/dict"
    
    # For Vercel, try relative to the file location
    if not os.path.exists(resources_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        resources_path = os.path.join(parent_dir, "resources", "dict")
    
    if not os.path.exists(resources_path):
        logger.error(f"Resources path not found: {resources_path}")
        raise RuntimeError("FIX dictionary resources not found")
    
    logger.info(f"Loading FIX dictionary from: {resources_path}")
    fix_parser = FIXDictionaryParser(resources_path)
    logger.info("FIX Dictionary Service started successfully")
    return fix_parser

# Initialize parser immediately for Vercel compatibility
try:
    init_parser()
except Exception as e:
    logger.error(f"Failed to initialize parser: {e}")
    # Don't raise here to allow the app to start, but endpoints will return 503

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - try to initialize if not already done
    global fix_parser
    if fix_parser is None:
        try:
            init_parser()
        except Exception as e:
            logger.error(f"Failed to initialize parser in lifespan: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FIX Dictionary Service...")

app = FastAPI(
    title="FIX Dictionary API",
    description="""
    A REST API service for FIX Protocol Dictionary data, providing FIXimate-like functionality.
    
    This service provides access to FIX protocol messages, fields, components, enums, and other dictionary data
    across multiple FIX versions (FIX.4.4, FIX.5.0SP2, and FIX.Z) with advanced pagination, sorting, and filtering.
    
    ## Features
    
    - **Search**: Find messages, fields, components, and enums by name or description
    - **Browse**: List all entities by category or type with pagination
    - **Details**: Get comprehensive information about specific entities
    - **Multi-version**: Support for multiple FIX protocol versions
    - **Regular Expressions**: Advanced search with regex support
    - **Pagination**: Efficient data loading with limit/offset parameters
    - **Sorting**: Sort results by any field in ascending/descending order
    - **Filtering**: Advanced filtering capabilities for all entity types
    
    ## FIX Versions Supported
    - FIX.4.4
    - FIX.5.0SP2
    - FIX.Z
    """,
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "arta",
        "tryItOutEnabled": True,
        "filter": True,
        "displayRequestDuration": True,
        "theme": "dark"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pagination models
class PaginatedResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

class PaginatedMessageResponse(PaginatedResponse):
    data: List[MessageSummary]

class PaginatedFieldResponse(PaginatedResponse):
    data: List[FieldSummary]

class PaginatedComponentResponse(PaginatedResponse):
    data: List[ComponentSummary]

# Helper function for DataFrame to dict conversion
def df_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert DataFrame to list of dictionaries, handling NaN values"""
    return df.fillna('').to_dict('records')

def create_paginated_response(df: pd.DataFrame, page: int, page_size: int, response_class):
    """Create paginated response from DataFrame"""
    total_count = len(df)
    has_next = (page * page_size) < total_count
    has_previous = page > 1
    
    return response_class(
        data=df_to_dict_list(df),
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_previous=has_previous
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that redirects to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FIX Dictionary API"}

@app.api_route("/single-spa-entry.js", methods=["GET", "HEAD"])
async def serve_single_spa_entry():
    """Serve the single-spa entry file for the UI"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    entry_file = os.path.join(static_dir, "single-spa-entry.js")
    
    if not os.path.exists(entry_file):
        raise HTTPException(status_code=404, detail="Single-spa entry file not found")
    
    return FileResponse(
        path=entry_file,
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )

@app.api_route("/ui-styles.css", methods=["GET", "HEAD"])
async def serve_ui_styles():
    """Serve the UI styles for the single-spa application"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    style_file = os.path.join(static_dir, "style.css")
    
    if not os.path.exists(style_file):
        raise HTTPException(status_code=404, detail="Style file not found")
    
    return FileResponse(
        path=style_file,
        media_type="text/css",
        headers={"Cache-Control": "no-cache"}
    )

@app.api_route("/test-ui.html", methods=["GET", "HEAD"])
async def serve_test_ui():
    """Serve the test UI page for single-spa application testing"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    test_file = os.path.join(static_dir, "test-ui.html")
    
    if not os.path.exists(test_file):
        raise HTTPException(status_code=404, detail="Test UI file not found")
    
    return FileResponse(
        path=test_file,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )

# Search endpoints with pagination
@app.get("/api/gateway/proxy/dict/search", response_model=SearchResponse)
async def search_all(
    query: str = Query(..., description="Search query string"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    search_type: SearchType = Query(SearchType.ALL, description="Type of entities to search"),
    match_abbr_only: bool = Query(False, description="Match abbreviated names only"),
    is_regex: bool = Query(False, description="Use regular expression matching"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """
    Search across all dictionary entities with pagination.
    
    Examples:
    - `/api/gateway/proxy/dict/search?query=Order&limit=20&offset=0` - First 20 results
    - `/api/gateway/proxy/dict/search?query=^Order&is_regex=true` - Regex search
    - `/api/gateway/proxy/dict/search?query=Limit&search_type=field` - Field-only search
    """
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = fix_parser.search(query, search_type, version, match_abbr_only, is_regex, limit, offset)
        return SearchResponse(
            query=query,
            version=version,
            results=results,
            total_count=len(results)
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Message endpoints with pagination, sorting, and filtering
@app.get("/api/gateway/proxy/dict/messages", response_model=PaginatedMessageResponse)
async def list_messages(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    category: Optional[str] = Query(None, description="Filter by category"),
    section: Optional[str] = Query(None, description="Filter by section"),
    msg_type: Optional[str] = Query(None, description="Filter by message type"),
    name_contains: Optional[str] = Query(None, description="Filter by name containing text"),
):
    """Get paginated list of messages with advanced filtering and sorting"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Build filters
        filters = {}
        if category:
            filters['category_id'] = category
        if section:
            filters['section_id'] = section
        if msg_type:
            filters['msg_type'] = msg_type
        if name_contains:
            filters['name'] = name_contains
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get data
        df = fix_parser.get_messages(version, page_size, offset, sort_by, sort_dir, filters)
        
        # Convert to response format
        summaries = []
        for _, row in df.iterrows():
            pedigree = f"Added: {row.get('added') or 'Unknown'}"
            if row.get('updated'):
                pedigree += f", Updated: {row.get('updated')}"
            if row.get('deprecated'):
                pedigree += f", Deprecated: {row.get('deprecated')}"
            
            summaries.append(MessageSummary(
                msg_type=row.get('msg_type', ''),
                name=row.get('name', ''),
                abbr_name=row.get('abbr_name', ''),
                component_id=row.get('component_id', 0),
                category_id=row.get('category_id', ''),
                description=(row.get('description', '')[:200] + "..." if len(str(row.get('description', ''))) > 200 else row.get('description', '')),
                pedigree=pedigree
            ))
        
        # Get total count for pagination
        total_df = fix_parser.get_messages(version, limit=10000, filters=filters)  # Get all for count
        total_count = len(total_df)
        
        return PaginatedMessageResponse(
            data=summaries,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total_count,
            has_previous=page > 1
        )
    except Exception as e:
        logger.error(f"Error listing messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list messages: {str(e)}")

# Field endpoints with pagination, sorting, and filtering
@app.get("/api/gateway/proxy/dict/fields", response_model=PaginatedFieldResponse)
async def list_fields(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("tag", description="Field to sort by"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    datatype: Optional[str] = Query(None, description="Filter by datatype"),
    tag_min: Optional[int] = Query(None, description="Minimum tag number"),
    tag_max: Optional[int] = Query(None, description="Maximum tag number"),
    name_contains: Optional[str] = Query(None, description="Filter by name containing text"),
):
    """Get paginated list of fields with advanced filtering and sorting"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Build filters
        filters = {}
        if datatype:
            filters['type'] = datatype
        if name_contains:
            filters['name'] = name_contains
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get data
        df = fix_parser.get_fields(version, page_size, offset, sort_by, sort_dir, filters)
        
        # Apply tag range filters
        if tag_min is not None:
            df = df[df['tag'] >= tag_min]
        if tag_max is not None:
            df = df[df['tag'] <= tag_max]
        
        # Convert to response format
        summaries = []
        for _, row in df.iterrows():
            pedigree = f"Added: {row.get('added') or 'Unknown'}"
            if row.get('updated'):
                pedigree += f", Updated: {row.get('updated')}"
            if row.get('deprecated'):
                pedigree += f", Deprecated: {row.get('deprecated')}"
            
            summaries.append(FieldSummary(
                tag=row.get('tag', 0),
                name=row.get('name', ''),
                abbr_name=row.get('abbr_name', ''),
                datatype=row.get('type', ''),
                union_datatype=row.get('union_data_type', ''),
                description=(row.get('description', '')[:200] + "..." if len(str(row.get('description', ''))) > 200 else row.get('description', '')),
                pedigree=pedigree
            ))
        
        # Get total count for pagination
        total_df = fix_parser.get_fields(version, limit=10000, filters=filters)
        if tag_min is not None:
            total_df = total_df[total_df['tag'] >= tag_min]
        if tag_max is not None:
            total_df = total_df[total_df['tag'] <= tag_max]
        total_count = len(total_df)
        
        return PaginatedFieldResponse(
            data=summaries,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total_count,
            has_previous=page > 1
        )
    except Exception as e:
        logger.error(f"Error listing fields: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list fields: {str(e)}")

# Component endpoints with pagination, sorting, and filtering
@app.get("/api/gateway/proxy/dict/components", response_model=PaginatedComponentResponse)
async def list_components(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    category: Optional[str] = Query(None, description="Filter by category"),
    component_type: Optional[str] = Query(None, description="Filter by component type"),
    name_contains: Optional[str] = Query(None, description="Filter by name containing text"),
):
    """Get paginated list of components with advanced filtering and sorting"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Build filters
        filters = {}
        if category:
            filters['category_id'] = category
        if component_type:
            filters['component_type'] = component_type
        if name_contains:
            filters['name'] = name_contains
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get data
        df = fix_parser.get_components(version, page_size, offset, sort_by, sort_dir, filters)
        
        # Convert to response format
        summaries = []
        for _, row in df.iterrows():
            pedigree = f"Added: {row.get('added') or 'Unknown'}"
            if row.get('updated'):
                pedigree += f", Updated: {row.get('updated')}"
            if row.get('deprecated'):
                pedigree += f", Deprecated: {row.get('deprecated')}"
            
            is_repeating = "Repeating" in str(row.get('component_type', ''))
            
            summaries.append(ComponentSummary(
                component_id=row.get('component_id', 0),
                name=row.get('name', ''),
                abbr_name=row.get('abbr_name', ''),
                category_id=row.get('category_id', ''),
                component_type=row.get('component_type', ''),
                is_repeating_group=is_repeating,
                description=(row.get('description', '')[:200] + "..." if len(str(row.get('description', ''))) > 200 else row.get('description', '')),
                pedigree=pedigree
            ))
        
        # Get total count for pagination
        total_df = fix_parser.get_components(version, limit=10000, filters=filters)
        total_count = len(total_df)
        
        return PaginatedComponentResponse(
            data=summaries,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=(page * page_size) < total_count,
            has_previous=page > 1
        )
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list components: {str(e)}")

# Continue with existing endpoints but update them to use DataFrame operations...
@app.get("/api/gateway/proxy/dict/messages/{msg_type}", response_model=MessageDetail)
async def get_message(
    msg_type: str = Path(..., description="Message type (e.g., 'D', 'A', '8')"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get detailed information about a specific message"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        message_row = fix_parser.get_message_by_type(msg_type, version)
        if message_row is None:
            raise HTTPException(status_code=404, detail=f"Message type '{msg_type}' not found")
        
        # Convert Series to Message object
        message = Message(
            component_id=message_row.get('component_id', 0),
            msg_type=message_row.get('msg_type', ''),
            name=message_row.get('name', ''),
            category_id=message_row.get('category_id', ''),
            section_id=SectionID(message_row.get('section_id', 'Other')),
            abbr_name=message_row.get('abbr_name', ''),
            not_req_xml=message_row.get('not_req_xml', False),
            description=message_row.get('description', ''),
            elaboration=message_row.get('elaboration', ''),
            added=message_row.get('added'),
            updated=message_row.get('updated'),
            deprecated=message_row.get('deprecated'),
            addedEP=message_row.get('addedEP'),
            updatedEP=message_row.get('updatedEP'),
            deprecatedEP=message_row.get('deprecatedEP')
        )
        
        # Get message contents
        msgcontents_df = fix_parser.data[version].get('msgcontents', pd.DataFrame())
        message_contents = []
        if not msgcontents_df.empty:
            contents_df = msgcontents_df[msgcontents_df['component_id'] == message.component_id].sort_values('position')
            for _, row in contents_df.iterrows():
                message_contents.append(MsgContent(
                    component_id=row.get('component_id', 0),
                    tag_text=row.get('tag_text', ''),
                    indent=row.get('indent', 0),
                    position=row.get('position', 0.0),
                    reqd=row.get('reqd', False),
                    inlined=row.get('inlined'),
                    description=row.get('description', ''),
                    added=row.get('added'),
                    updated=row.get('updated'),
                    deprecated=row.get('deprecated'),
                    addedEP=row.get('addedEP'),
                    updatedEP=row.get('updatedEP'),
                    deprecatedEP=row.get('deprecatedEP')
                ))
        
        # Get related fields and components
        fields = []
        components = []
        fields_df = fix_parser.data[version].get('fields', pd.DataFrame())
        components_df = fix_parser.data[version].get('components', pd.DataFrame())
        
        for content in message_contents:
            # Try to parse tag_text as tag number first
            try:
                tag_num = int(content.tag_text)
                if not fields_df.empty:
                    field_matches = fields_df[fields_df['tag'] == tag_num]
                    if not field_matches.empty:
                        row = field_matches.iloc[0]
                        fields.append(Field(
                            tag=row.get('tag', 0),
                            name=row.get('name', ''),
                            type=row.get('type', ''),
                            abbr_name=row.get('abbr_name', ''),
                            not_req_xml=row.get('not_req_xml', False),
                            description=row.get('description', ''),
                            elaboration=row.get('elaboration', ''),
                            base_category=row.get('base_category', ''),
                            base_category_abbr_name=row.get('base_category_abbr_name', ''),
                            union_data_type=row.get('union_data_type', ''),
                            added=row.get('added'),
                            updated=row.get('updated'),
                            deprecated=row.get('deprecated'),
                            addedEP=row.get('addedEP'),
                            updatedEP=row.get('updatedEP'),
                            deprecatedEP=row.get('deprecatedEP')
                        ))
            except ValueError:
                # If not a number, might be a component name
                if not components_df.empty:
                    comp_matches = components_df[components_df['name'] == content.tag_text]
                    if not comp_matches.empty:
                        row = comp_matches.iloc[0]
                        components.append(Component(
                            component_id=row.get('component_id', 0),
                            component_type=ComponentType(row.get('component_type', 'Block')),
                            category_id=row.get('category_id', ''),
                            name=row.get('name', ''),
                            abbr_name=row.get('abbr_name', ''),
                            not_req_xml=row.get('not_req_xml', False),
                            description=row.get('description', ''),
                            elaboration=row.get('elaboration', ''),
                            added=row.get('added'),
                            updated=row.get('updated'),
                            deprecated=row.get('deprecated'),
                            addedEP=row.get('addedEP'),
                            updatedEP=row.get('updatedEP'),
                            deprecatedEP=row.get('deprecatedEP')
                        ))
        
        return MessageDetail(
            **message.dict(),
            contents=message_contents,
            fields=fields,
            components=components
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting message {msg_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get message: {str(e)}")

# Add remaining endpoints here - field details, component details, etc.
# [Previous endpoints remain the same but should be updated to use DataFrame operations]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
