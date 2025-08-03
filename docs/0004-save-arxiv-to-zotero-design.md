# Save arXiv Papers to Zotero - Design Document

## Overview

This document outlines the design for adding "Save to Zotero" functionality for arXiv papers in the AI-powered paper reading assistant. The feature allows users to save arXiv papers directly to their Zotero library via the Zotero Connector API.

## Goals

1. **Seamless Integration**: Allow users to save arXiv papers to Zotero with one click
2. **API Compatibility**: Design endpoints consistent with existing API architecture
3. **Robust Error Handling**: Graceful handling of Zotero connectivity and API failures
4. **User Experience**: Clear feedback on save status and success/failure states

## Architecture

### Component Overview

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Frontend (Vue)    │    │   Backend (FastAPI)  │    │   Zotero Desktop    │
│                     │    │                      │    │                     │
│ PaperReader.vue     │───→│ POST /arxiv/{id}/    │───→│ Connector API       │
│                     │    │   save-to-zotero     │    │ (localhost:23119)   │
│ Save Button         │←───│ Returns PaperResponse│←───│ Saves Paper         │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### API Design

#### New Endpoint
```http
POST /api/v1/arxiv/{arxiv_id}/save-to-zotero
```

**Path Parameters:**
- `arxiv_id`: arXiv paper identifier (e.g., "2401.12345")

**Response:**
- `200 OK`: Returns `PaperResponse` with new Zotero paper details
- `404 Not Found`: arXiv paper not found
- `503 Service Unavailable`: Zotero not running
- `500 Internal Server Error`: Save operation failed

**Response Format:**
```json
{
  "id": "ABC12345",
  "title": "Paper Title",
  "authors": "Author1, Author2",
  "year": "2024",
  "journal": "arXiv",
  "abstract": "Abstract text...",
  "doi": "10.48550/arXiv.2401.12345",
  "url": "https://arxiv.org/abs/2401.12345",
  "tags": ["cs.AI", "cs.LG"],
  "pdf_path": "/path/to/pdf",
  "has_pdf": true
}
```

### Service Layer

#### New Services

1. **ZoteroConnectorService** (`app/services/zotero_connector.py`)
   - Handles Zotero Connector API communication
   - Manages ID generation and field mapping
   - Provides health check functionality

2. **SaveToZoteroService** (`app/services/save_to_zotero.py`)
   - Orchestrates the save process
   - Coordinates between arXivService and ZoteroConnectorService
   - Handles error recovery and retry logic

### Data Flow

#### Save Process

1. **Frontend Request**
   ```typescript
   // PaperReader.vue
   const saveToZotero = async (arxivId: string) => {
     const response = await fetch(`/api/v1/arxiv/${arxivId}/save-to-zotero`, {
       method: 'POST'
     });
     return response.json(); // Returns PaperResponse
   };
   ```

2. **Backend Processing**
   ```python
   # 1. Get complete arXiv metadata via ArxivService
   metadata = await arxiv_service.get_arxiv_paper(arxiv_id)

   # 2. Map to Zotero format
   zotero_item = map_arxiv_to_zotero(metadata)
   # 2.1 Generate Zotero item ID
   zotero_item['itemID'] = generate_zotero_item_id(arxiv_id)
   # > random string with uppercase letters and digits, letters first
   # > check if ID already exists in Zotero

   # 3. Save via Zotero Connector
   #  first create item, then add attachment
   result = await zotero_connector.save_item(zotero_item)

   # 4. Return as PaperResponse
   return PaperResponse(...)
   ```

3. **Field Mapping**
   ```python
   {
     "itemType": "preprint",
     "title": arxiv_metadata.title,
     "creators": [
       {
         "creatorType": "author",
         "firstName": "First",
         "lastName": "Last"
       }
     ],
     "abstractNote": arxiv_metadata.abstract,
     "url": f"https://arxiv.org/abs/{arxiv_id}",
     "date": arxiv_metadata.published[:10],  # YYYY-MM-DD
     "archiveID": f"arXiv:{arxiv_id}",
     "DOI": f"10.48550/arXiv.{arxiv_id}",
     "publisher": "arXiv"
   }
   ```

### Error Handling

#### Error Types and Responses

| Error Type | HTTP Status | Frontend Response |
|------------|-------------|-------------------|
| arXiv paper not found | 404 | "Paper not found on arXiv" |
| Zotero not running | 503 | "Please start Zotero to save papers" |
| Network timeout | 504 | "Connection to Zotero timed out" |
| Invalid arXiv ID | 400 | "Invalid arXiv paper ID" |
| Save failed | 500 | "Failed to save paper to Zotero" |

#### Retry Logic
- **Zotero health check**: Before attempting save
- **Retry attempts**: 3 attempts with exponential backoff
- **Fallback**: Graceful degradation with clear error messages

### Frontend Integration

#### UI Components

1. **Save Button** (`PaperReader.vue`)
   - Only visible for arXiv papers (`source === 'arxiv'`)
   - States: idle, loading, success, error
   - Position: Next to "Home" button in title bar

2. **Status Feedback**
   ```typescript
   enum SaveStatus {
     IDLE = 'idle',
     SAVING = 'saving',
     SUCCESS = 'success',
     ERROR = 'error'
   }
   ```

3. **User Feedback**
   - Loading: Button shows spinner
   - Success: Button changes to "Saved" with checkmark
   - Error: Tooltip shows error message on hover

### Security Considerations

1. **Local Access Only**: Zotero Connector only accepts localhost connections
2. **No Authentication**: Relies on local machine trust model
3. **Input Validation**: Strict arXiv ID format validation
4. **Rate Limiting**: Basic rate limiting to prevent abuse

### Testing Strategy

#### Manual Testing
- Zotero desktop running/not running
- Various arXiv paper types
- Different author name formats

### Future Enhancements

1. **Collection Selection**: Allow users to choose target collection
2. **Duplicate Detection**: Check if paper already exists in Zotero
3. **Batch Operations**: Save multiple papers at once
4. **Metadata Enrichment**: Add tags based on arXiv categories

## Dependencies

### Backend
- `aiohttp`: For Zotero Connector API calls
- `xml.etree.ElementTree`: For arXiv XML parsing (existing)

### Frontend
- No new dependencies required
- Uses existing fetch API and UI components

## Success Metrics

1. **Functional**: Successful save to Zotero for standard arXiv papers
2. **Reliable**: 99% uptime for save functionality
3. **User Experience**: <3 seconds response time for save operation
4. **Error Handling**: Clear, actionable error messages for all failure modes
