# FIX Dictionary REST API

A Python REST service that provides FIXimate-like functionality for browsing FIX Protocol dictionary data.

## Features

- **Multi-version Support**: FIX.4.4, FIX.5.0SP2, and FIX.Z
- **Comprehensive Search**: Search across messages, fields, components, and enums
- **RESTful API**: Clean REST endpoints with OpenAPI/Swagger documentation
- **FIXimate Compatibility**: URLs that mirror FIXimate's direct access patterns
- **Vercel Deployment**: Optimized for serverless deployment

## API Endpoints

### Search
- `GET /api/search` - Search all dictionary entities
- `GET /api/search?query=Order&search_type=message` - Search messages containing "Order"
- `GET /api/search?query=^Order&is_regex=true` - Regex search for entities starting with "Order"

### Messages
- `GET /api/messages` - List all messages
- `GET /api/messages/{msg_type}` - Get message details by type (e.g., 'D', 'A', '8')
- `GET /api/messages?category=Trade` - Filter messages by category

### Fields
- `GET /api/fields` - List all fields
- `GET /api/fields/{tag}` - Get field details by tag number
- `GET /api/fields/name/{name}` - Get field details by name
- `GET /api/fields?datatype=String` - Filter fields by datatype

### Components
- `GET /api/components` - List all components
- `GET /api/components/{name}` - Get component details by name
- `GET /api/components?category=Common` - Filter components by category

### Code Sets (Enums)
- `GET /api/codesets` - List all fields that have enum values
- `GET /api/codesets/{tag}` - Get enum values for a field tag

### Direct Access (FIXimate-style)
- `GET /api/{version}/msg/{id}` - Get message by ID
- `GET /api/{version}/tag/{tag}` - Get field by tag
- `GET /api/{version}/cmp/{id}` - Get component by ID

### Utility
- `GET /api/versions` - List available FIX versions
- `GET /api/sections` - List section IDs
- `GET /api/categories` - List categories for a version

## Query Parameters

Most endpoints support these common parameters:

- `version`: FIX version (`FIX.4.4`, `FIX.5.0SP2`, or `FIX.Z`)
- `query`: Search query string
- `search_type`: Type to search (`message`, `field`, `component`, `enum`, `all`)
- `is_regex`: Enable regular expression matching
- `match_abbr_only`: Match only abbreviated names

## Examples

### Search for all entities containing "Order"
```bash
curl "https://your-domain.vercel.app/api/search?query=Order"
```

### Get details of message type 'D' (NewOrderSingle)
```bash
curl "https://your-domain.vercel.app/api/messages/D"
```

### Get field details for tag 11 (ClOrdID)
```bash
curl "https://your-domain.vercel.app/api/fields/11"
```

### Get enum values for field tag 54 (Side)
```bash
curl "https://your-domain.vercel.app/api/codesets/54"
```

### Search using regex
```bash
curl "https://your-domain.vercel.app/api/search?query=^Nested.*&is_regex=true"
```

## Deployment to Vercel

1. Install Vercel CLI: `npm install -g vercel`
2. Deploy: `vercel --prod`

The service will automatically load FIX dictionary data from the `resources/dict` directory.

## Local Development

```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Run development server
cd api
python main.py
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

## Data Structure

The service loads XML files from the FIX dictionary:
- Messages.xml - FIX message definitions
- Fields.xml - Field definitions with tags and types
- Components.xml - Reusable component blocks
- Enums.xml - Enumerated values for fields
- Categories.xml - Message/component categories
- Sections.xml - Protocol sections
- Datatypes.xml - Base data types
- Abbreviations.xml - Abbreviated terms
- MsgContents.xml - Message composition data

## Response Models

All endpoints return structured JSON with consistent models:
- Pedigree information (added/updated/deprecated versions)
- Comprehensive field details including enums
- Message composition with fields and components
- Usage tracking across messages and components
