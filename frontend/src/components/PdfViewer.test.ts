import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import PdfViewer from './PdfViewer.vue';

// Mock @embedpdf/vue-pdf-viewer
vi.mock('@embedpdf/vue-pdf-viewer', () => ({
  PDFViewer: {
    name: 'PDFViewer',
    props: ['config'],
    emits: ['init', 'ready'],
    template: '<div data-testid="pdf-embed-inner">Mock PDFViewer: {{ config.src }}</div>',
  },
}));

describe('PdfViewer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders empty state when src is null', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: null,
      },
    });
    expect(wrapper.find('[data-testid="pdf-empty"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="pdf-embed"]').exists()).toBe(false);
  });

  it('renders embed viewer when src is provided', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
      },
    });
    expect(wrapper.find('[data-testid="pdf-empty"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="pdf-embed"]').exists()).toBe(true);
  });

  it('passes correct config to PDFViewer component', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
        spreadMode: 'odd',
        disabledCategories: ['annotation'],
      },
    });
    const embed = wrapper.find('[data-testid="pdf-embed"]');
    expect(embed.exists()).toBe(true);
    // The mock renders config.src in its template
    expect(embed.text()).toContain('https://example.com/test.pdf');
  });

  it('emits ready event when PDFViewer is ready', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
      },
    });
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    const mockRegistry = { getEngine: vi.fn() };
    embed.vm.$emit('ready', mockRegistry);
    await nextTick();
    expect(wrapper.emitted('ready')).toHaveLength(1);
    expect(wrapper.emitted('ready')![0][0]).toBe(mockRegistry);
  });

  it('resets loading state when src changes', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/old.pdf',
      },
    });
    // Simulate ready
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    embed.vm.$emit('ready', {});
    await nextTick();
    expect(wrapper.find('[data-testid="pdf-loading"]').exists()).toBe(false);

    await wrapper.setProps({ src: 'https://example.com/new.pdf' });
    await nextTick();
    expect(wrapper.find('[data-testid="pdf-loading"]').exists()).toBe(true);
  });

  it('uses default disabled categories', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
      },
    });
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    const categories = embed.props('config').disabledCategories;
    expect(categories).toContain('redaction');
    expect(categories).toContain('print');
    expect(categories).toContain('insert');
    expect(categories).toContain('form');
    expect(categories).toContain('document-open');
    expect(categories).toContain('document-close');
    expect(categories).not.toContain('panel');
  });

  it('allows custom disabled categories', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
        disabledCategories: ['zoom'],
      },
    });
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').disabledCategories).toEqual(['zoom']);
  });

  it('configures spread mode in PDFViewer config', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
        spreadMode: 'odd',
      },
    });
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').spread).toEqual({ defaultSpreadMode: 'odd' });
  });

  it('sets tabBar to never in config', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
      },
    });
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').tabBar).toBe('never');
  });

  it('enables annotation rendering for clickable links', () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
      },
    });
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').render).toEqual({ withAnnotations: true });
  });

  it('updates config when spreadMode prop changes', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
        spreadMode: 'none',
      },
    });
    let embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').spread).toEqual({ defaultSpreadMode: 'none' });

    await wrapper.setProps({ spreadMode: 'odd' });
    embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').spread).toEqual({ defaultSpreadMode: 'odd' });
  });

  it('applies spread mode via registry capability when spreadMode prop changes after ready', async () => {
    const setSpreadMode = vi.fn();
    const mockRegistry = {
      getPlugin: vi.fn(() => ({
        provides: () => ({
          setSpreadMode,
        }),
      })),
    };

    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
        spreadMode: 'none',
      },
    });

    // Simulate ready
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    embed.vm.$emit('ready', mockRegistry);
    await nextTick();

    expect(mockRegistry.getPlugin).not.toHaveBeenCalled();

    // Change spread mode
    await wrapper.setProps({ spreadMode: 'odd' });
    await nextTick();

    expect(mockRegistry.getPlugin).toHaveBeenCalledWith('spread');
    expect(setSpreadMode).toHaveBeenCalledWith('odd');
  });

  it('does not call registry when spreadMode changes but registry is not ready', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/test.pdf',
        spreadMode: 'none',
      },
    });

    // No ready event emitted, registry is null
    await wrapper.setProps({ spreadMode: 'odd' });
    await nextTick();

    // Should not throw and should just update config
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    expect(embed.props('config').spread).toEqual({ defaultSpreadMode: 'odd' });
  });

  it('resets registry when src changes', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        src: 'https://example.com/old.pdf',
      },
    });

    const mockRegistry = { getEngine: vi.fn() };
    const embed = wrapper.findComponent({ name: 'PDFViewer' });
    embed.vm.$emit('ready', mockRegistry);
    await nextTick();

    await wrapper.setProps({ src: 'https://example.com/new.pdf' });
    await nextTick();

    // After src change, the old registry should be cleared, so changing spreadMode should not call old registry
    const setSpreadMode = vi.fn();
    Object.assign(mockRegistry, {
      getPlugin: vi.fn(() => ({
        provides: () => ({ setSpreadMode }),
      })),
    });

    await wrapper.setProps({ spreadMode: 'even' });
    await nextTick();
    expect(setSpreadMode).not.toHaveBeenCalled();
  });
});
