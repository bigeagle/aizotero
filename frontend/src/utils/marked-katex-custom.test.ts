import { describe, it, expect } from 'vitest';
import { marked } from 'marked';
import markedKatex, { extractDelimited } from './marked-katex-custom';

describe('extractDelimited', () => {
  it('matches simple bracket block', () => {
    const result = extractDelimited('\\[a\\]', '\\[', '\\]');
    expect(result).not.toBeNull();
    expect(result!.content).toBe('a');
    expect(result!.raw).toBe('\\[a\\]');
  });

  it('matches simple inline paren', () => {
    const result = extractDelimited('\\(x^2\\)', '\\(', '\\)');
    expect(result).not.toBeNull();
    expect(result!.content).toBe('x^2');
  });

  it('handles content with square brackets (regression)', () => {
    const result = extractDelimited('\\[ \\mathrm{KL}[p \\,||\\, q_\\theta] \\]', '\\[', '\\]');
    expect(result).not.toBeNull();
    expect(result!.content.trim()).toBe('\\mathrm{KL}[p \\,||\\, q_\\theta]');
  });

  it('handles content with parentheses inside inline paren', () => {
    const result = extractDelimited('\\( \\mathrm{KL}[p||q_\\theta] \\)', '\\(', '\\)');
    expect(result).not.toBeNull();
    expect(result!.content.trim()).toBe('\\mathrm{KL}[p||q_\\theta]');
  });

  it('handles escaped end marker in content', () => {
    const result = extractDelimited('\\[ a\\\\]b \\]', '\\[', '\\]');
    expect(result).not.toBeNull();
    expect(result!.content.trim()).toBe('a\\\\]b');
  });

  it('handles cases environment with backslashes', () => {
    const result = extractDelimited(
      '\\[ f(x) = \\begin{cases} 1 & x > 0 \\\\ 0 & x \\le 0 \\end{cases} \\]',
      '\\[',
      '\\]'
    );
    expect(result).not.toBeNull();
    expect(result!.content).toContain('\\begin{cases}');
    expect(result!.content).toContain('\\\\');
  });

  it('returns null for unclosed delimiter', () => {
    const result = extractDelimited('\\[ unclosed', '\\[', '\\]');
    expect(result).toBeNull();
  });

  it('returns null when src does not start with startMarker', () => {
    const result = extractDelimited('hello \\[x\\]', '\\[', '\\]');
    expect(result).toBeNull();
  });
});

describe('markedKatex integration', () => {
  const mk = marked.use(markedKatex({ throwOnError: false, nonStandard: true }));

  it('renders block bracket formula with square brackets', () => {
    const html = mk.parse('\\[ \\mathrm{KL}[p \\,||\\, q_\\theta] \\]') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
  });

  it('renders inline paren formula with square brackets', () => {
    const html = mk.parse('\\( \\mathrm{KL}[p||q_\\theta] \\)') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
  });

  it('renders simple block formula', () => {
    const html = mk.parse('\\[a+b=c\\]') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
  });

  it('renders simple inline formula', () => {
    const html = mk.parse('\\(x^2\\)') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
  });

  it('renders dollar inline formula', () => {
    const html = mk.parse('$E = mc^2$') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
  });

  it('renders double-dollar block formula', () => {
    const html = mk.parse('$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
  });

  it('renders mixed markdown and math', () => {
    const html = mk.parse('The energy is $E = mc^2$ and the sum is \\[ \\sum_{i=1}^{n} x_i \\].') as string;
    expect(html).toContain('class="katex');
    expect(html).not.toContain('katex-error');
    expect(html).toContain('<p>');
  });

  it('does not break on plain text without math', () => {
    const html = mk.parse('Hello world, no math here.') as string;
    expect(html).toContain('<p>Hello world, no math here.</p>');
    expect(html).not.toContain('katex-error');
  });
});
