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
};
