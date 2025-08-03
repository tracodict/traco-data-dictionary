# Pagination Event Handling Fix

## Issue
The `handlePageChange` function was always triggering REST API calls with `page=1&page_size=50` instead of the updated page number.

## Root Cause
The wx-svelte-core Pager component sends pagination events with `{from, to}` structure, not a direct `page` property.

## Solution
Updated the `handlePageChange` function in all three components to correctly extract the page number:

```javascript
function handlePageChange(event: any) {
  // wx-svelte-core Pager sends { from, to } in the event
  // We need to calculate the page number from the 'from' value
  const { from, to } = event;
  const page = Math.floor(from / pageSize) + 1;
  console.log('Page change event:', { from, to, page, pageSize });
  
  if (onPageChange) {
    onPageChange(page);
  }
}
```

## How It Works
1. **Event Structure**: Pager sends `{from: 0, to: 50}` for page 1, `{from: 50, to: 100}` for page 2, etc.
2. **Page Calculation**: `Math.floor(from / pageSize) + 1` converts the 0-based `from` index to 1-based page number
3. **API Call**: The calculated page number is passed to the parent component's `onPageChange` handler
4. **Backend Request**: API client uses the correct page number in the query string

## Components Updated
- **MessageList.svelte**: Fixed page calculation
- **ComponentList.svelte**: Fixed page calculation  
- **FieldList.svelte**: Fixed page calculation

## Testing
- Page 1: `from=0, to=50` → `page=1` → API: `?page=1&page_size=50`
- Page 2: `from=50, to=100` → `page=2` → API: `?page=2&page_size=50`
- Page 3: `from=100, to=150` → `page=3` → API: `?page=3&page_size=50`

## Result
Now pagination correctly sends the updated page number to the backend API, enabling proper server-side pagination.
