# FIX Dictionary API - Deployment Guide

## Quick Start

This REST API provides FIXimate-like functionality for### Configuration

### uv Commands Reference

Common uv commands for this project:

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Install project in editable mode
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Alternative: Install without virtual environment (add --system flag)
uv pip install -r requirements.txt --system
uv pip install -e . --system

# Sync dependencies (ensures exact versions)
uv pip sync requirements.txt

# Generate lockfile
uv pip freeze > requirements.lock

# Run commands in virtual environment
uv run python test_api.py
uv run uvicorn api.main:app --reload

# Run commands without activating venv
uv run --python .venv/bin/python test_api.py
```

### Environment Variablesowsing FIX Protocol dictionary data.

### Why uv?

This project uses [uv](https://astral.sh/uv/) for Python package management, which provides:
- **10-100x faster** package installation than pip
- **Reliable dependency resolution** with lockfiles
- **Better caching** and disk space efficiency
- **Drop-in replacement** for pip commands

### Local Development

1. **Install uv (if not already installed)**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or via pip
   pip install uv
   ```

2. **Setup Environment and Install Dependencies**
   ```bash
   # Create virtual environment
   uv venv
   
   # Activate virtual environment
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate   # Windows
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

3. **Run Development Server**
   ```bash
   python3 run_dev.py
   ```

3. **Test the API**
   ```bash
   ./examples.sh
   ```

4. **View Documentation**
   Open http://localhost:8000/docs in your browser

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

4. **Troubleshooting Vercel Issues**

   If deployment fails or service doesn't start:
   
   ```bash
   # Check deployment logs
   vercel logs <deployment-url>
   
   # Test locally first with virtual environment
   source .venv/bin/activate
   vercel dev
   
   # Check if all files are included
   vercel --debug
   
   # Test the entry point locally
   source .venv/bin/activate
   python -c "from index import app; print('✓ Entry point works')"
   ```

   **Common issues:**
   - **Vercel config conflicts**: Cannot use both `functions` and `builds` - use only `builds`
   - **Virtual environment**: Always activate with `source .venv/bin/activate` before testing
   - **Cold start timeout**: The service loads ~4800+ entities on startup (can take 5-10 seconds)
   - **Missing dependencies**: Ensure httpx is in requirements.txt for TestClient support
   - **Resource path issues**: The service needs access to `resources/dict/` directory
   - **Import errors**: Check that all modules can be imported in the deployment environment
   - **Parser initialization**: The service may need time to initialize all FIX versions

5. **Update Examples Script**
   Edit `examples.sh` and change `BASE_URL` to your Vercel URL.

6. **Test Deployment**
   ```bash
   # Test your deployed service
   curl "https://tracodict.vercel.app/api/versions"
   curl "https://tracodict.vercel.app/health"
   
   # Test FIX.Z support
   curl "https://tracodict.vercel.app/api/search?version=FIX.Z&query=Order&limit=3"
   
   # Test specific FIX.Z endpoints
   curl "https://tracodict.vercel.app/api/messages/D?version=FIX.Z"
   curl "https://tracodict.vercel.app/api/fields/11?version=FIX.Z"
   curl "https://tracodict.vercel.app/api/codesets/54?version=FIX.Z"
   ```

## Project Structure

```
tracodict/
├── api/
│   └── main.py              # FastAPI application
├── resources/
│   └── dict/                # FIX dictionary XML files
│       ├── FIX.4.4/Base/    # FIX 4.4 data
│       ├── FIX.5.0SP2/Base/ # FIX 5.0 SP2 data
│       └── FIX.Z/Base/      # FIX.Z data
├── models.py                # Pydantic models
├── parser.py                # XML parser and data loader
├── index.py                 # Vercel entry point
├── vercel.json              # Vercel configuration
├── pyproject.toml           # Modern Python project config
├── requirements.txt         # Python dependencies (legacy)
├── test_api.py              # Test script
├── run_dev.py               # Development server
├── examples.sh              # API examples
└── README.md                # Documentation
```

## API Overview

### Core Endpoints

- **Search**: `/api/search?query=Order` - Find entities by name/description
- **Messages**: `/api/messages/D` - Get message details by type
- **Fields**: `/api/fields/11` - Get field details by tag
- **Components**: `/api/components/Instrument` - Get component details
- **Enums**: `/api/codesets/54` - Get enum values for a field

### URL Patterns (FIXimate-style)

- `/api/FIX.5.0SP2/msg/14` - Message by ID
- `/api/FIX.5.0SP2/tag/11` - Field by tag
- `/api/FIX.5.0SP2/cmp/1003` - Component by ID

### Query Parameters

- `version`: `FIX.4.4`, `FIX.5.0SP2`, or `FIX.Z`
- `query`: Search string
- `search_type`: `message`, `field`, `component`, `enum`, `all`
- `is_regex`: `true` for regex matching
- `match_abbr_only`: `true` to match only abbreviated names

## Configuration

### Environment Variables

No environment variables required. The service auto-detects the XML dictionary location.

### Resource Loading

The service loads FIX dictionary data from:
1. `resources/dict/` (relative to script)
2. `/home/data/git/tracodict/resources/dict/` (absolute fallback)

### Supported FIX Versions

- **FIX.4.4**: 93 messages, 912 fields, 106 components
- **FIX.5.0SP2**: 116 messages, 1452 fields, 176 components
- **FIX.Z**: 116 messages, 1452 fields, 176 components

All versions fully loaded and operational.

## Performance

### Cold Start
- Vercel cold start: ~3-5 seconds
- Data loading: ~1-2 seconds per version
- Total: ~5-7 seconds for first request

### Warm Requests
- Typical response time: 50-200ms
- Search queries: 100-500ms
- Memory usage: ~50-100MB

### Optimization Tips

1. **Caching**: Responses are internally cached
2. **Filtering**: Use specific search types to reduce results
3. **Pagination**: Results limited to 100 items
4. **Compression**: Enable gzip in production

## Error Handling

The API provides detailed error responses:

```json
{
  "detail": "Message type 'X' not found",
  "error": "not_found",
  "message": "The requested resource was not found"
}
```

Common HTTP status codes:
- `200`: Success
- `404`: Resource not found
- `422`: Invalid parameters
- `500`: Server error
- `503`: Service unavailable

## Security

### CORS
CORS is enabled for all origins in development. For production, configure specific origins in `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

### Rate Limiting
Consider adding rate limiting for production use:

```bash
uv pip install slowapi
```

## Monitoring

### Health Check
`GET /health` returns service status

### Logging
Logs are available in Vercel dashboard or locally via console

### Metrics
- Request count
- Response times
- Error rates
- Memory usage

## Troubleshooting

### Common Issues

1. **uv Virtual Environment Errors**
   ```bash
   # Error: "No virtual environment found"
   # Solution: Create and activate virtual environment
   uv venv
   source .venv/bin/activate
   
   # Or use --system flag for system-wide install
   uv pip install -r requirements.txt --system
   ```

2. **Import Errors**
   - Check Python path configuration
   - Ensure all dependencies installed
   - Verify virtual environment is activated

3. **XML Parse Errors**
   - Verify XML file integrity
   - Check file permissions

3. **Missing Resources**
   - Ensure `resources/dict/` exists
   - Verify FIX version directories

4. **Vercel Timeout**
   - Optimize data loading
   - Consider caching strategies

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing

Run the test suite:

```bash
python3 test_api.py
```

## Extending the API

### Adding New FIX Versions

1. Add version to `FIXVersion` enum in `models.py`
2. Place XML files in `resources/dict/{VERSION}/Base/`
3. Test with new version parameter

### Custom Endpoints

Add new endpoints in `api/main.py`:

```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"message": "Custom functionality"}
```

### Additional Data Sources

Extend the parser in `parser.py` to support:
- Additional XML schemas
- Database backends
- External APIs

## Support

- GitHub Issues: Create issues for bugs/features
- Documentation: See README.md
- Examples: Run `./examples.sh`
- API Docs: Visit `/docs` endpoint
