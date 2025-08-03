# Zotero Connector API Documentation

This document provides comprehensive documentation for the **Zotero Connector API**, which allows programmatic interaction with the Zotero desktop application via local HTTP endpoints.

## Overview

The Zotero Connector exposes a local HTTP server on port `23119` when the Zotero desktop application is running. This API enables external applications to:

- Detect if Zotero is available
- Import academic papers and metadata
- Save attachments and snapshots
- Interact with Zotero collections and libraries

## Base Configuration

- **Base URL**: `http://127.0.0.1:23119/connector/`
- **Content-Type**: `application/json` for all POST requests
- **Port**: 23119 (configurable in Zotero preferences)
- **Authentication**: None required (local access only)

## Core Endpoints

### 1. Health Check

```http
GET /connector/ping
POST /connector/ping

{}
```

Returns simple string "Zotero is running" or JSON with version information.

**Response:**
```json
{
  "version": "7.0.0",
  "prefs": {...}
}
```

### 2. Detect Translators

```http
POST /connector/getTranslators
Content-Type: application/json

{}
```

Returns list of available translators for the given URL.

### 3. Detect Importable Content

```http
POST /connector/detect
Content-Type: application/json

{
  "uri": "https://arxiv.org/abs/2401.12345",
  "html": "<html>...</html>",
  "cookie": "session=..."
}
```

Returns array of matching translators and their priorities.

### 4. Save Items to Library

```http
POST /connector/saveItems
Content-Type: application/json

{
  "items": [{
    "itemType": "journalArticle",
    "title": "Paper Title",
    "creators": [
      {
        "creatorType": "author",
        "firstName": "John",
        "lastName": "Doe"
      }
    ],
    "abstractNote": "Abstract text...",
    "url": "https://arxiv.org/abs/2401.12345",
    "date": "2024-01-01",
    "archive": "arXiv",
    "extra": "arXiv: 2401.12345"
  }],
  "sessionID": "unique-session-id"
}
```

**Required Fields:**
- `id`: 8-character random string (uppercase letters A-Z + numbers 0-9, first character must be letter)

**Response:**
- `201 Created` - Items successfully saved
- `400 Bad Request` - Invalid payload
- `500 Internal Server Error` - Server error

### 5. Save Attachments

#### Save Standalone Attachment
```http
POST /connector/saveStandaloneAttachment
Headers:
  X-Metadata: {"url":"...","title":"...","sessionID":"..."}
Body: binary attachment data
```

#### Save Attachment to Existing Item
```http
POST /connector/saveAttachment
Headers:
  X-Metadata: {"parentItemID":"...","url":"...","title":"...","sessionID": "..."}
Body: binary attachment data
```

### 6. Get Collections

```http
POST /connector/getSelectedCollection
Content-Type: application/json

{
  "switchToReadableLibrary": true
}
```

Returns available libraries and collections structure.

## Integration Examples

### JavaScript/TypeScript

```typescript
interface ZoteroItem {
  itemType: string;
  title: string;
  creators: Array<{
    creatorType: string;
    firstName?: string;
    lastName?: string;
    name?: string;
  }>;
  abstractNote?: string;
  url?: string;
  date?: string;
  archive?: string;
  extra?: string;
  tags?: string[];
}

class ZoteroConnector {
  private baseUrl = 'http://127.0.0.1:23119/connector';

  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/ping`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async saveArxivPaper(arxivId: string, metadata: {
    title: string;
    authors: string[];
    abstract: string;
    date: string;
  }): Promise<{success: boolean; data?: any; error?: string}> {
    const authors = metadata.authors.map(name => {
      const parts = name.split(' ');
      return {
        creatorType: 'author',
        firstName: parts[0],
        lastName: parts.slice(1).join(' ')
      };
    });

    // Generate valid Zotero item ID
    function generateItemId() {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
      let id = '';
      id += chars[Math.floor(Math.random() * 26)]; // First must be letter
      for (let i = 0; i < 7; i++) {
        id += chars[Math.floor(Math.random() * 36)];
      }
      return id;
    }

    const payload = {
      items: [{
        itemType: 'preprint',
        id: generateItemId(),
        title: metadata.title,
        creators: authors,
        abstractNote: metadata.abstract,
        url: `https://arxiv.org/abs/${arxivId}`,
        date: metadata.date,
        publisher: 'arXiv',
        number: `arXiv:${arxivId}`,
        archiveID: `arXiv:${arxivId}`,
        DOI: `10.48550/arXiv.${arxivId}`
      }],
      sessionID: `aizotero-${Date.now()}`
    };

    try {
      const response = await fetch(`${this.baseUrl}/saveItems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.status === 201) {
        return { success: true, data: await response.json() };
      }
      return { success: false, error: `HTTP ${response.status}` };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getCollections() {
    const response = await fetch(`${this.baseUrl}/getSelectedCollection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ switchToReadableLibrary: true })
    });
    return response.json();
  }
}

// Usage example
const connector = new ZoteroConnector();
if (await connector.isAvailable()) {
  await connector.saveArxivPaper('2401.12345', {
    title: 'Attention Is All You Need',
    authors: ['Ashish Vaswani', 'Noam Shazeer'],
    abstract: 'We propose a new simple network architecture, the Transformer...',
    date: '2017-06-12'
  });
}
```

### Python Integration

```python
import requests
import json
from typing import Dict, List, Any

class ZoteroConnector:
    def __init__(self, base_url="http://127.0.0.1:23119/connector"):
        self.base_url = base_url

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/ping", timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def save_arxiv_paper(self, arxiv_id: str, title: str, authors: List[str],
                        abstract: str, date: str) -> Dict[str, Any]:
        authors_list = []
        for author in authors:
            parts = author.split(' ', 1)
            authors_list.append({
                "creatorType": "author",
                "firstName": parts[0] if len(parts) > 1 else "",
                "lastName": parts[1] if len(parts) > 1 else parts[0]
            })

        # Generate valid Zotero item ID
        def generate_item_id():
            chars = string.ascii_uppercase + string.digits
            # First character must be a letter
            id_str = random.choice(string.ascii_uppercase)
            # Remaining 7 characters
            id_str += ''.join(random.choice(chars) for _ in range(7))
            return id_str

        payload = {
            "items": [{
                "itemType": "preprint",
                "id": generate_item_id(),
                "title": title,
                "creators": authors_list,
                "abstractNote": abstract,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "date": date,
                "publisher": "arXiv",
                "number": f"arXiv:{arxiv_id}",
                "archiveID": f"arXiv:{arxiv_id}",
                "DOI": "10.48550/arXiv." + arxiv_id,
            }],
            "sessionID": f"aizotero-{hash(arxiv_id) % 10000}"
        }

        response = requests.post(
            f"{self.base_url}/saveItems",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

# Usage
connector = ZoteroConnector()
if connector.is_available():
    result = connector.save_arxiv_paper(
        "2401.12345",
        "Attention Is All You Need",
        ["Ashish Vaswani", "Noam Shazeer"],
        "We propose a new simple network architecture...",
        "2017-06-12"
    )
    print(result)
```

## Error Handling

### Common HTTP Status Codes
- `200 OK` - Successful operation
- `201 Created` - Item successfully saved
- `400 Bad Request` - Invalid JSON payload
- `404 Not Found` - Endpoint doesn't exist
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Zotero not running

### Error Response Format
```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Testing and Debugging

### Quick Health Check
```bash
# Test if Zotero is running
curl http://127.0.0.1:23119/connector/ping

# Test collection retrieval
curl -X POST http://127.0.0.1:23119/connector/getSelectedCollection \
  -H "Content-Type: application/json" \
  -d '{"switchToReadableLibrary": true}'
```

### Browser Testing
```javascript
// In browser console
fetch('http://127.0.0.1:23119/connector/ping')
  .then(r => r.text())
  .then(console.log)
  .catch(console.error);
```

## Security Considerations

- **Local only**: API only accessible from localhost
- **No authentication**: Assumes same-machine access
- **HTTPS not supported**: Uses plain HTTP for local communication
- **CORS**: No CORS restrictions for localhost requests

## Integration with AIZotero

This API can be integrated into your AIZotero application to provide "Save to Zotero" functionality when users discover interesting papers through the AI interface. The implementation should:

1. Check if Zotero is available via `/ping`
2. Allow users to select target collection via `/getSelectedCollection`
3. Save papers with complete metadata via `/saveItems`
4. Handle errors gracefully with fallback options

## References

- [Zotero Connector Source Code](https://github.com/zotero/zotero-connectors)
- [Official Zotero Documentation](https://www.zotero.org/support/)
- [Zotero Developer Community](https://groups.google.com/g/zotero-dev)
