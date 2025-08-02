import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional, Union
import logging
from contextlib import asynccontextmanager

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
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that redirects to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FIX Dictionary API"}

# Search endpoints
@app.get("/api/search", response_model=SearchResponse)
async def search_all(
    query: str = Query(..., description="Search query string"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    search_type: SearchType = Query(SearchType.ALL, description="Type of entities to search"),
    match_abbr_only: bool = Query(False, description="Match abbreviated names only"),
    is_regex: bool = Query(False, description="Use regular expression matching"),
):
    """
    Search across all dictionary entities (messages, fields, components, enums).
    
    Examples:
    - `/api/search?query=Order` - Find all entities containing "Order"
    - `/api/search?query=^Order&is_regex=true` - Find entities starting with "Order"
    - `/api/search?query=Limit&search_type=field` - Find fields containing "Limit"
    """
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = fix_parser.search(query, search_type, version, match_abbr_only, is_regex)
        return SearchResponse(
            query=query,
            version=version,
            results=results,
            total_count=len(results)
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Message endpoints
@app.get("/api/messages", response_model=List[MessageSummary])
async def list_messages(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    category: Optional[str] = Query(None, description="Filter by category"),
    section: Optional[SectionID] = Query(None, description="Filter by section")
):
    """Get list of all messages with summary information"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        messages = fix_parser.get_messages(version)
        
        # Apply filters
        if category:
            messages = [m for m in messages if m.category_id.lower() == category.lower()]
        if section:
            messages = [m for m in messages if m.section_id == section]
        
        # Convert to summary format
        summaries = []
        for message in messages:
            pedigree = f"Added: {message.added or 'Unknown'}"
            if message.updated:
                pedigree += f", Updated: {message.updated}"
            if message.deprecated:
                pedigree += f", Deprecated: {message.deprecated}"
            
            summaries.append(MessageSummary(
                msg_type=message.msg_type,
                name=message.name,
                abbr_name=message.abbr_name,
                component_id=message.component_id,
                category_id=message.category_id,
                description=message.description[:200] + "..." if len(message.description) > 200 else message.description,
                pedigree=pedigree
            ))
        
        return summaries
    except Exception as e:
        logger.error(f"Error listing messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list messages: {str(e)}")

@app.get("/api/messages/{msg_type}", response_model=MessageDetail)
async def get_message(
    msg_type: str = Path(..., description="Message type (e.g., 'D', 'A', '8')"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get detailed information about a specific message"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        message = fix_parser.get_message_by_type(msg_type, version)
        if not message:
            raise HTTPException(status_code=404, detail=f"Message type '{msg_type}' not found")
        
        # Get message contents
        msgcontents = fix_parser.data[version].get('msgcontents', [])
        message_contents = [mc for mc in msgcontents if mc.component_id == message.component_id]
        message_contents.sort(key=lambda x: x.position)
        
        # Get related fields and components
        fields = []
        components = []
        all_fields = fix_parser.get_fields(version)
        all_components = fix_parser.get_components(version)
        
        for content in message_contents:
            # Try to parse tag_text as tag number first
            try:
                tag_num = int(content.tag_text)
                field = fix_parser.get_field_by_tag(tag_num, version)
                if field:
                    fields.append(field)
            except ValueError:
                # If not a number, might be a component name
                for comp in all_components:
                    if comp.name == content.tag_text:
                        components.append(comp)
                        break
        
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

# Field endpoints
@app.get("/api/fields", response_model=List[FieldSummary])
async def list_fields(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    datatype: Optional[str] = Query(None, description="Filter by datatype")
):
    """Get list of all fields with summary information"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        fields = fix_parser.get_fields(version)
        
        # Apply filters
        if datatype:
            fields = [f for f in fields if f.type.lower() == datatype.lower()]
        
        # Convert to summary format
        summaries = []
        for field in fields:
            pedigree = f"Added: {field.added or 'Unknown'}"
            if field.updated:
                pedigree += f", Updated: {field.updated}"
            if field.deprecated:
                pedigree += f", Deprecated: {field.deprecated}"
            
            summaries.append(FieldSummary(
                tag=field.tag,
                name=field.name,
                abbr_name=field.abbr_name,
                datatype=field.type,
                union_datatype=field.union_data_type,
                description=field.description[:200] + "..." if len(field.description) > 200 else field.description,
                pedigree=pedigree
            ))
        
        return summaries
    except Exception as e:
        logger.error(f"Error listing fields: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list fields: {str(e)}")

@app.get("/api/fields/{tag}", response_model=FieldDetail)
async def get_field_by_tag(
    tag: int = Path(..., description="Field tag number"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get detailed information about a field by tag number"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        field = fix_parser.get_field_by_tag(tag, version)
        if not field:
            raise HTTPException(status_code=404, detail=f"Field with tag {tag} not found")
        
        # Get enums for this field
        enums = fix_parser.get_enums_for_field(tag, version)
        
        # Get usage in messages and components (simplified)
        usage_messages = []
        usage_components = []
        
        # Check message contents for this field
        msgcontents = fix_parser.data[version].get('msgcontents', [])
        for mc in msgcontents:
            if mc.tag_text == str(tag):
                # Find the message name
                messages = fix_parser.get_messages(version)
                for msg in messages:
                    if msg.component_id == mc.component_id:
                        usage_messages.append(msg.name)
                        break
        
        return FieldDetail(
            **field.dict(),
            enums=enums,
            usage_in_messages=list(set(usage_messages)),
            usage_in_components=usage_components
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting field {tag}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get field: {str(e)}")

@app.get("/api/fields/name/{name}", response_model=FieldDetail)
async def get_field_by_name(
    name: str = Path(..., description="Field name"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get detailed information about a field by name"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        field = fix_parser.get_field_by_name(name, version)
        if not field:
            raise HTTPException(status_code=404, detail=f"Field '{name}' not found")
        
        # Get enums for this field
        enums = fix_parser.get_enums_for_field(field.tag, version)
        
        # Get usage in messages and components (simplified)
        usage_messages = []
        usage_components = []
        
        return FieldDetail(
            **field.dict(),
            enums=enums,
            usage_in_messages=usage_messages,
            usage_in_components=usage_components
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting field {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get field: {str(e)}")

# Component endpoints
@app.get("/api/components", response_model=List[ComponentSummary])
async def list_components(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version"),
    category: Optional[str] = Query(None, description="Filter by category"),
    component_type: Optional[ComponentType] = Query(None, description="Filter by component type")
):
    """Get list of all components with summary information"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        components = fix_parser.get_components(version)
        
        # Apply filters
        if category:
            components = [c for c in components if c.category_id.lower() == category.lower()]
        if component_type:
            components = [c for c in components if c.component_type == component_type]
        
        # Convert to summary format
        summaries = []
        for component in components:
            pedigree = f"Added: {component.added or 'Unknown'}"
            if component.updated:
                pedigree += f", Updated: {component.updated}"
            if component.deprecated:
                pedigree += f", Deprecated: {component.deprecated}"
            
            is_repeating = "Repeating" in component.component_type.value
            
            summaries.append(ComponentSummary(
                component_id=component.component_id,
                name=component.name,
                abbr_name=component.abbr_name,
                category_id=component.category_id,
                component_type=component.component_type,
                is_repeating_group=is_repeating,
                description=component.description[:200] + "..." if len(component.description) > 200 else component.description,
                pedigree=pedigree
            ))
        
        return summaries
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list components: {str(e)}")

@app.get("/api/components/{name}", response_model=ComponentDetail)
async def get_component(
    name: str = Path(..., description="Component name"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get detailed information about a component"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        component = fix_parser.get_component_by_name(name, version)
        if not component:
            raise HTTPException(status_code=404, detail=f"Component '{name}' not found")
        
        # Get component contents
        msgcontents = fix_parser.data[version].get('msgcontents', [])
        component_contents = [mc for mc in msgcontents if mc.component_id == component.component_id]
        component_contents.sort(key=lambda x: x.position)
        
        # Get related fields and nested components
        fields = []
        nested_components = []
        all_fields = fix_parser.get_fields(version)
        all_components = fix_parser.get_components(version)
        
        for content in component_contents:
            try:
                tag_num = int(content.tag_text)
                field = fix_parser.get_field_by_tag(tag_num, version)
                if field:
                    fields.append(field)
            except ValueError:
                for comp in all_components:
                    if comp.name == content.tag_text:
                        nested_components.append(comp)
                        break
        
        # Get usage information
        usage_messages = []
        usage_components = []
        
        return ComponentDetail(
            **component.dict(),
            contents=component_contents,
            fields=fields,
            nested_components=nested_components,
            usage_in_messages=usage_messages,
            usage_in_components=usage_components
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting component {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get component: {str(e)}")

# Enum/CodeSet endpoints
@app.get("/api/codesets", response_model=List[CodeSetSummary])
async def list_codesets(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get list of all code sets (fields that have enums)"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        fields = fix_parser.get_fields(version)
        enums = fix_parser.get_enums(version)
        
        # Group enums by tag to find fields that have codesets
        enum_tags = set(enum.tag for enum in enums)
        
        summaries = []
        for field in fields:
            if field.tag in enum_tags:
                pedigree = f"Added: {field.added or 'Unknown'}"
                if field.updated:
                    pedigree += f", Updated: {field.updated}"
                if field.deprecated:
                    pedigree += f", Deprecated: {field.deprecated}"
                
                summaries.append(CodeSetSummary(
                    tag=field.tag,
                    name=field.name,
                    base_datatype=field.type,
                    description=field.description[:200] + "..." if len(field.description) > 200 else field.description,
                    pedigree=pedigree
                ))
        
        return summaries
    except Exception as e:
        logger.error(f"Error listing codesets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list codesets: {str(e)}")

@app.get("/api/codesets/{tag}", response_model=List[Enum])
async def get_codeset(
    tag: int = Path(..., description="Field tag number"),
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get all enum values for a specific field tag"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        enums = fix_parser.get_enums_for_field(tag, version)
        if not enums:
            # Check if field exists
            field = fix_parser.get_field_by_tag(tag, version)
            if not field:
                raise HTTPException(status_code=404, detail=f"Field with tag {tag} not found")
            else:
                raise HTTPException(status_code=404, detail=f"No enum values found for field {tag}")
        
        return enums
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting codeset {tag}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get codeset: {str(e)}")

# Utility endpoints
@app.get("/api/versions", response_model=List[str])
async def get_versions():
    """Get list of available FIX versions"""
    return [version.value for version in FIXVersion]

@app.get("/api/sections", response_model=List[str])
async def get_sections():
    """Get list of available section IDs"""
    return [section.value for section in SectionID]

@app.get("/api/categories", response_model=List[str])
async def get_categories(
    version: FIXVersion = Query(FIXVersion.FIX_5_0_SP2, description="FIX version")
):
    """Get list of available categories for a version"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        categories = fix_parser.data[version].get('categories', [])
        return list(set(cat.category_id for cat in categories))
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

# Direct access endpoints (like FIXimate URLs)
@app.get("/api/{version}/msg/{component_id}", response_model=MessageDetail)
async def get_message_by_id(
    version: str = Path(..., description="FIX version"),
    component_id: int = Path(..., description="Message component ID")
):
    """Get message by component ID (FIXimate-style URL)"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        fix_version = FIXVersion(version)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid FIX version: {version}")
    
    try:
        messages = fix_parser.get_messages(fix_version)
        message = next((m for m in messages if m.component_id == component_id), None)
        
        if not message:
            raise HTTPException(status_code=404, detail=f"Message with ID {component_id} not found")
        
        return await get_message(message.msg_type, fix_version)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting message by ID {component_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get message: {str(e)}")

@app.get("/api/{version}/tag/{tag}", response_model=FieldDetail)
async def get_field_by_tag_direct(
    version: str = Path(..., description="FIX version"),
    tag: int = Path(..., description="Field tag number")
):
    """Get field by tag (FIXimate-style URL)"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        fix_version = FIXVersion(version)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid FIX version: {version}")
    
    return await get_field_by_tag(tag, fix_version)

@app.get("/api/{version}/cmp/{component_id}", response_model=ComponentDetail)
async def get_component_by_id(
    version: str = Path(..., description="FIX version"),
    component_id: int = Path(..., description="Component ID")
):
    """Get component by ID (FIXimate-style URL)"""
    if not fix_parser:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        fix_version = FIXVersion(version)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid FIX version: {version}")
    
    try:
        components = fix_parser.get_components(fix_version)
        component = next((c for c in components if c.component_id == component_id), None)
        
        if not component:
            raise HTTPException(status_code=404, detail=f"Component with ID {component_id} not found")
        
        return await get_component(component.name, fix_version)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting component by ID {component_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get component: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
