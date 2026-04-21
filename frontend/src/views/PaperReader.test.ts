import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';

import PaperReader from './PaperReader.vue';

// Mock vue-router
const mockPush = vi.fn();
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock services
const mockZoteroGetPaper = vi.fn();
const mockZoteroGetPdfURL = vi.fn();
const mockZoteroSaveToZotero = vi.fn();
const mockArxivGetPaper = vi.fn();
const mockArxivGetPdfURL = vi.fn();

vi.mock('@/services/zoteroService', () => ({
  zoteroService: {
    getPaper: (...args: unknown[]) => mockZoteroGetPaper(...args),
    getPdfURL: (...args: unknown[]) => mockZoteroGetPdfURL(...args),
    saveToZotero: (...args: unknown[]) => mockZoteroSaveToZotero(...args),
  },
}));

vi.mock('@/services/arxivService', () => ({
  arxivService: {
    getPaper: (...args: unknown[]) => mockArxivGetPaper(...args),
    getPdfURL: (...args: unknown[]) => mockArxivGetPdfURL(...args),
  },
}));

// Mock child components
vi.mock('@/components/AIChat.vue', () => ({
  default: {
    name: 'AIChat',
    props: ['paperId', 'source'],
    template: '<div data-testid="ai-chat">AIChat</div>',
  },
}));

vi.mock('@/components/AIConfig.vue', () => ({
  default: {
    name: 'AIConfig',
    template: '<div data-testid="ai-config">AIConfig</div>',
  },
}));

vi.mock('@/components/PdfViewer.vue', () => ({
  default: {
    name: 'PdfViewer',
    props: ['src', 'spreadMode'],
    emits: ['update:spreadMode', 'ready', 'error'],
    template: `
      <div data-testid="pdf-viewer">
        <span data-testid="pdf-src">{{ src }}</span>
        <span data-testid="pdf-spread">{{ spreadMode }}</span>
        <button data-testid="emit-ready" @click="$emit('ready', {})">Ready</button>
      </div>
    `,
  },
}));

describe('PaperReader', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.title = '';
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const createZoteroPaper = () => ({
    id: '12345',
    title: 'Test Zotero Paper',
    authors: 'Alice, Bob',
    year: '2024',
    journal: 'Nature',
    abstract: 'An abstract',
    pdf_path: '/path/to/pdf.pdf',
    url: 'https://example.com/paper',
  });

  const createArxivPaper = () => ({
    id: '2401.12345',
    title: 'Test ArXiv Paper',
    authors: 'Charlie, Dave',
    year: '2024',
    journal: 'arXiv',
    abstract: 'An arXiv abstract',
    pdf_path: 'https://arxiv.org/pdf/2401.12345.pdf',
    url: 'https://arxiv.org/abs/2401.12345',
  });

  it('renders PdfViewer with correct src for zotero source', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    const pdfViewer = wrapper.find('[data-testid="pdf-viewer"]');
    expect(pdfViewer.exists()).toBe(true);
    expect(wrapper.find('[data-testid="pdf-src"]').text()).toBe('http://localhost:23119/12345/pdf');
  });

  it('renders PdfViewer with correct src for arxiv source', async () => {
    mockArxivGetPaper.mockResolvedValue(createArxivPaper());
    mockArxivGetPdfURL.mockReturnValue('https://arxiv.org/pdf/2401.12345.pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'arxiv',
        paperId: '2401.12345',
      },
    });
    await flushPromises();

    const pdfViewer = wrapper.find('[data-testid="pdf-viewer"]');
    expect(pdfViewer.exists()).toBe(true);
    expect(wrapper.find('[data-testid="pdf-src"]').text()).toBe('https://arxiv.org/pdf/2401.12345.pdf');
  });

  it('default spread mode is odd', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    expect(wrapper.find('[data-testid="pdf-spread"]').text()).toBe('odd');
  });

  it('shows PDF unavailable when pdf_path is missing', async () => {
    const paper = createZoteroPaper() as Record<string, unknown>;
    paper.pdf_path = undefined;
    mockZoteroGetPaper.mockResolvedValue(paper);

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    expect(wrapper.find('[data-testid="pdf-viewer"]').exists()).toBe(false);
    expect(wrapper.text()).toContain('PDF文件不可用');
  });

  it('refetches paper when paperId changes', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();
    expect(mockZoteroGetPaper).toHaveBeenCalledTimes(1);

    mockZoteroGetPaper.mockClear();
    const paper2 = createZoteroPaper();
    paper2.id = '67890';
    paper2.title = 'Another Paper';
    mockZoteroGetPaper.mockResolvedValue(paper2);
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/67890/pdf');

    await wrapper.setProps({ paperId: '67890' });
    await flushPromises();

    expect(mockZoteroGetPaper).toHaveBeenCalledTimes(1);
    expect(wrapper.find('[data-testid="pdf-src"]').text()).toBe('http://localhost:23119/67890/pdf');
  });

  it('refetches paper when source changes', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    mockArxivGetPaper.mockResolvedValue(createArxivPaper());
    mockArxivGetPdfURL.mockReturnValue('https://arxiv.org/pdf/2401.12345.pdf');

    await wrapper.setProps({ source: 'arxiv', paperId: '2401.12345' });
    await flushPromises();

    expect(mockArxivGetPaper).toHaveBeenCalledTimes(1);
    expect(wrapper.find('[data-testid="pdf-src"]').text()).toBe('https://arxiv.org/pdf/2401.12345.pdf');
  });

  it('shows save to zotero button for arxiv papers', async () => {
    mockArxivGetPaper.mockResolvedValue(createArxivPaper());
    mockArxivGetPdfURL.mockReturnValue('https://arxiv.org/pdf/2401.12345.pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'arxiv',
        paperId: '2401.12345',
      },
    });
    await flushPromises();

    expect(wrapper.text()).toContain('保存到Zotero');
  });

  it('does not show save to zotero button for zotero papers', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    expect(wrapper.text()).not.toContain('保存到Zotero');
  });

  it('navigates to zotero page after saving arxiv paper', async () => {
    mockArxivGetPaper.mockResolvedValue(createArxivPaper());
    mockArxivGetPdfURL.mockReturnValue('https://arxiv.org/pdf/2401.12345.pdf');
    mockZoteroSaveToZotero.mockResolvedValue({ item_id: '99999' });

    const wrapper = mount(PaperReader, {
      props: {
        source: 'arxiv',
        paperId: '2401.12345',
      },
    });
    await flushPromises();

    // Find the save button by checking text content
    const buttons = wrapper.findAll('button');
    const saveToZoteroBtn = buttons.find((b) => b.text().includes('保存到Zotero'));
    expect(saveToZoteroBtn).toBeDefined();
    await saveToZoteroBtn!.trigger('click');
    await flushPromises();

    expect(mockZoteroSaveToZotero).toHaveBeenCalledWith('2401.12345', true);
    expect(mockPush).toHaveBeenCalledWith('/read/zotero/99999');
  });

  it('displays paper title in header', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    expect(wrapper.text()).toContain('Test Zotero Paper');
  });

  it('updates document title with paper title', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    expect(document.title).toBe('Test Zotero Paper - AI论文助手');
  });

  it('hides PdfViewer during resize', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
      attachTo: document.body,
    });
    await flushPromises();

    const pdfViewer = wrapper.find('[data-testid="pdf-viewer"]');
    expect(pdfViewer.exists()).toBe(true);
    expect(pdfViewer.classes()).not.toContain('invisible');

    // Trigger resize start
    const resizeHandle = wrapper.find('.cursor-col-resize');
    await resizeHandle.trigger('mousedown');

    expect(wrapper.find('[data-testid="pdf-viewer"]').classes()).toContain('invisible');

    // Trigger resize stop via document mouseup
    document.dispatchEvent(new MouseEvent('mouseup'));
    await flushPromises();

    expect(wrapper.find('[data-testid="pdf-viewer"]').classes()).not.toContain('invisible');

    wrapper.unmount();
  });

  it('shows original link button when url is available', async () => {
    mockZoteroGetPaper.mockResolvedValue(createZoteroPaper());
    mockZoteroGetPdfURL.mockReturnValue('http://localhost:23119/12345/pdf');

    const wrapper = mount(PaperReader, {
      props: {
        source: 'zotero',
        paperId: '12345',
      },
    });
    await flushPromises();

    const link = wrapper.find('a[href="https://example.com/paper"]');
    expect(link.exists()).toBe(true);
    expect(link.text()).toContain('原文');
  });
});
