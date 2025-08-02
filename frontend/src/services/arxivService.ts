export interface ArxivPaper {
  id: string;
  title: string;
  authors: string;
  year?: string;
  journal?: string;
  abstract: string;
  doi?: string;
  url?: string;
  tags: string[];
  pdf_path?: string;
  has_pdf: boolean;
}

export interface CacheInfo {
  pdf_cached: boolean;
  metadata_cached: boolean;
  pdf_size: number;
  cache_age_hours: number;
}

export const arxivService = {
  async getPaper(arxivId: string): Promise<ArxivPaper> {
    const response = await fetch(`/api/v1/arxiv/${arxivId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  },

  async getPdf(arxivId: string): Promise<Response> {
    return fetch(`/api/v1/arxiv/${arxivId}/pdf`);
  },

  getPdfURL(arxivId: string): string {
    return `/api/v1/arxiv/${arxivId}/pdf`;
  },

  async getMarkdown(arxivId: string): Promise<{ arxiv_id: string; markdown: string }> {
    const response = await fetch(`/api/v1/arxiv/${arxivId}/markdown`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  },

  async getCacheInfo(arxivId: string): Promise<CacheInfo> {
    const response = await fetch(`/api/v1/arxiv/${arxivId}/info`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  },

  async clearCache(arxivId: string): Promise<void> {
    const response = await fetch(`/api/v1/arxiv/${arxivId}/cache`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  },
};
