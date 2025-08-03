export interface ZoteroPaper {
  id: string;
  title: string;
  authors: string;
  year?: string;
  journal?: string;
  abstract?: string;
  doi?: string;
  url?: string;
  tags: string[];
  pdf_path?: string;
  has_pdf: boolean;
}

export interface SaveToZoteroResponse {
  item_id: string;
  status: string;
}

export const zoteroService = {
  async getPaper(paperId: string): Promise<ZoteroPaper> {
    const response = await fetch(`/api/v1/papers/${paperId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  },

  async getPdf(paperId: string): Promise<Response> {
    return fetch(`/api/v1/papers/${paperId}/pdf`);
  },

  getPdfURL(paperId: string): string {
    return `/api/v1/papers/${paperId}/pdf`;
  },

  async getMarkdown(paperId: string): Promise<{ paper_id: string; markdown: string }> {
    const response = await fetch(`/api/v1/papers/${paperId}/markdown`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  },

  async getPapers(query?: string, tag?: string | null): Promise<ZoteroPaper[]> {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (tag) params.set('tag', tag);

    const response = await fetch(`/api/v1/papers?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  },

  async saveToZotero(arxivId: string, includePdf: boolean = true): Promise<SaveToZoteroResponse> {
    const response = await fetch(`/api/v1/arxiv/${arxivId}/save-to-zotero`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ include_pdf: includePdf }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },
};
