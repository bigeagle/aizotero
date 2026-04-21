<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { marked } from 'marked';
import markedKatex from '@/utils/marked-katex-custom';
import 'katex/dist/katex.css';

const markedWithKatex = marked.use(
  markedKatex({
    throwOnError: false,
    displayMode: false,
    nonStandard: true,
  })
);

// Test cases for markdown + LaTeX rendering
interface TestCase {
  name: string;
  markdown: string;
}

const testCases: TestCase[] = [
  {
    name: 'Basic Inline Math ($)',
    markdown: 'The energy is given by $E = mc^2$ where $m$ is mass and $c$ is light speed.',
  },
  {
    name: 'Basic Inline Math (\\(\\))',
    markdown: 'The gradient is \\( \\nabla f(x) \\) and the divergence is \\( \\nabla \\cdot \\mathbf{v} \\).',
  },
  {
    name: 'Block Math ($$)',
    markdown: 'The quadratic formula:\n\n$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n\nis well known.',
  },
  {
    name: 'Block Math (\\[\\])',
    markdown: 'The integral form:\n\n\\[\\int_{a}^{b} f(x) \\, dx = F(b) - F(a)\\]\n\nwhere $F$ is the antiderivative.',
  },
  {
    name: 'MiniLLM-style Complex Formulas',
    markdown: `The forward KL divergence:

$$\\mathrm{KL}[p \\,||\\, q_\\theta] = \\mathbb{E}_{x\\sim p_x, y\\sim p} \\log \\frac{p(y|x)}{q_\\theta(y|x)}$$

And the reverse KL:

$$\\theta = \\arg\\min_\\theta \\mathcal{L}(\\theta) = \\arg\\min_\\theta \\mathrm{KL}[q_\\theta \\,||\\, p]$$

With policy gradient:

$$\\nabla \\mathcal{L}(\\theta) = -\\mathbb{E}_{x\\sim p_x, y\\sim q_\\theta(\\cdot|x)} \\sum_{t=1}^T (R_t - 1) \\nabla \\log q_\\theta(y_t|y_{<t}, x)$$`,
  },
  {
    name: 'Fractions and Sums',
    markdown:
      'The average is $\\bar{x} = \\frac{1}{n} \\sum_{i=1}^{n} x_i$ and the variance is $\\sigma^2 = \\frac{1}{n} \\sum_{i=1}^{n} (x_i - \\bar{x})^2$.',
  },
  {
    name: 'Matrices',
    markdown:
      'A rotation matrix: $R = \\begin{pmatrix} \\cos\\theta & -\\sin\\theta \\\\ \\sin\\theta & \\cos\\theta \\end{pmatrix}$',
  },
  {
    name: 'Greek Letters and Symbols',
    markdown:
      '$\\alpha, \\beta, \\gamma, \\delta, \\epsilon, \\varepsilon, \\zeta, \\eta, \\theta, \\vartheta, \\iota, \\kappa, \\lambda, \\mu, \\nu, \\xi, \\pi, \\varpi, \\rho, \\varrho, \\sigma, \\varsigma, \\tau, \\upsilon, \\phi, \\varphi, \\chi, \\psi, \\omega$',
  },
  {
    name: 'Markdown + Math Mixed',
    markdown: `## Section Title

Here is a list with math:

1. First item: $a^2 + b^2 = c^2$
2. Second item: $$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$
3. Third item with \\( \\prod_{i=1}^{n} x_i \\)

> Blockquote with math: $e^{i\\pi} + 1 = 0$

\`\`\`python
# Some code
import math
result = math.sqrt(2)
\`\`\`

And inline code \`$x^2$\` should not render as math.`,
  },
  {
    name: 'Edge: Adjacent Dollars',
    markdown: 'Price is $5 and $10 means $5 + $10 = $15. Also $a$ and $b$ are variables.',
  },
  {
    name: 'Edge: Empty and Single Char',
    markdown: '$x$, $y$, $z$, and $\\alpha$',
  },
  {
    name: 'Edge: Escaped vs Unescaped',
    markdown: 'Escaped dollar: \\$5.00. Math: $5 \\times 10 = 50$. Backslash before paren: \\( \\)(not math).',
  },
  {
    name: 'Edge: Multi-line Block',
    markdown: `Multi-line block:

$$
f(x) = \\begin{cases}
x^2 & \\text{if } x > 0 \\\
0 & \\text{otherwise}
\\end{cases}
$$

Another:

\\[
\\begin{aligned}
\\dot{x} &= \\sigma(y - x) \\\\
\\dot{y} &= \\rho x - y - xz \\\\
\\dot{z} &= -\\beta z + xy
\\end{aligned}
\\]`,
  },
  {
    name: 'Edge: Unicode and Punctuation',
    markdown: '温度是 $T = 300\\,\\mathrm{K}$，速度是 $v = 10\\,\\mathrm{m/s}$。检查标点：$x$。$y$！$z$？',
  },
  {
    name: 'Real-world: Paper Summary Style',
    markdown: `这篇论文提出了 **MiniLLM**，一种面向大规模生成式语言模型的白盒知识蒸馏方法。

核心公式——前向 KL 散度：

$$\\mathrm{KL}[p \\,||\\, q_\\theta] = \\mathbb{E}_{x\\sim p_x, y\\sim p} \\log \\frac{p(y|x)}{q_\\theta(y|x)}$$

反向 KL 散度：

$$\\theta = \\arg\\min_\\theta \\mathrm{KL}[q_\\theta \\,||\\, p]$$

策略梯度：

$$\\nabla \\mathcal{L}(\\theta) = -\\mathbb{E}_{x\\sim p_x, y\\sim q_\\theta(\\cdot|x)} \\sum_{t=1}^T (R_t - 1) \\nabla \\log q_\\theta(y_t|y_{<t}, x)$$`,
  },
];

const customInput = ref(`## 自定义测试

在这里输入任意 Markdown + LaTeX 内容来测试渲染效果。

例如行内公式：$E = mc^2$ 和 \\( a^2 + b^2 = c^2 \\)。

块级公式：

$$\\int_{-\\infty}^{+\\infty} e^{-x^2} \\, dx = \\sqrt{\\pi}$$

\\[\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}\\]`);

const selectedTest = ref<string>('all');

const filteredTests = computed(() => {
  if (selectedTest.value === 'all') return testCases;
  if (selectedTest.value === 'custom') return [];
  return testCases.filter((t) => t.name === selectedTest.value);
});

function renderMarkdown(content: string): string {
  if (!content.trim()) return '';
  try {
    return markedWithKatex.parse(content) as string;
  } catch (err) {
    return `<div class="text-red-500">Render Error: ${err instanceof Error ? err.message : String(err)}</div>`;
  }
}

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

const showSource = ref<Record<string, boolean>>({});

function toggleSource(name: string) {
  showSource.value[name] = !showSource.value[name];
}

// Auto-expand first test on mount
watch(
  filteredTests,
  () => {
    if (filteredTests.value.length > 0) {
      showSource.value[filteredTests.value[0].name] = true;
    }
  },
  { once: true }
);
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Markdown + LaTeX 渲染测试</h1>
      <div class="flex items-center gap-4">
        <label class="text-sm text-gray-600">选择测试:</label>
        <select
          v-model="selectedTest"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">全部测试 ({{ testCases.length }})</option>
          <option value="custom">自定义输入</option>
          <optgroup label="单项测试">
            <option v-for="tc in testCases" :key="tc.name" :value="tc.name">
              {{ tc.name }}
            </option>
          </optgroup>
        </select>
      </div>
    </div>

    <!-- Custom input section -->
    <div v-if="selectedTest === 'custom'" class="mb-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <h2 class="text-sm font-semibold text-gray-700 mb-2">输入 (Markdown + LaTeX)</h2>
          <textarea
            v-model="customInput"
            class="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="输入 Markdown + LaTeX..."
          ></textarea>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-gray-700 mb-2">渲染结果</h2>
          <div
            class="w-full h-96 p-4 border border-gray-200 rounded-lg bg-white overflow-auto text-sm [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:mb-2 [&>ol]:list-decimal [&>ol]:pl-5 [&>ol]:mb-2 [&>h1]:text-lg [&>h1]:font-bold [&>h1]:mb-2 [&>h2]:text-base [&>h2]:font-bold [&>h2]:mb-2 [&>h3]:text-sm [&>h3]:font-bold [&>h3]:mb-1 [&>blockquote]:border-l-4 [&>blockquote]:border-gray-300 [&>blockquote]:pl-4 [&>blockquote]:italic [&>blockquote]:mb-2 [&>code]:bg-gray-100 [&>code]:px-1 [&>code]:py-0.5 [&>code]:rounded [&>code]:text-sm [&>pre]:bg-gray-50 [&>pre]:p-2 [&>pre]:rounded [&>pre]:overflow-x-auto [&>pre]:mb-2"
            v-html="renderMarkdown(customInput)"
          ></div>
        </div>
      </div>
    </div>

    <!-- Test cases grid -->
    <div v-else class="space-y-6">
      <div v-for="tc in filteredTests" :key="tc.name" class="border border-gray-200 rounded-lg overflow-hidden">
        <div
          class="bg-gray-50 px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-100"
          @click="toggleSource(tc.name)"
        >
          <h2 class="font-semibold text-sm">{{ tc.name }}</h2>
          <div class="flex items-center gap-2">
            <span v-if="showSource[tc.name]" class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
              显示源码
            </span>
            <span class="text-gray-400 text-lg">{{ showSource[tc.name] ? '▼' : '▶' }}</span>
          </div>
        </div>

        <div class="p-4">
          <!-- Rendered output -->
          <div class="mb-4">
            <div class="text-xs text-gray-500 mb-2 font-semibold">渲染结果</div>
            <div
              class="p-4 bg-white border border-gray-100 rounded text-sm [&>p]:mb-2 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:mb-2 [&>ol]:list-decimal [&>ol]:pl-5 [&>ol]:mb-2 [&>h1]:text-lg [&>h1]:font-bold [&>h1]:mb-2 [&>h2]:text-base [&>h2]:font-bold [&>h2]:mb-2 [&>h3]:text-sm [&>h3]:font-bold [&>h3]:mb-1 [&>blockquote]:border-l-4 [&>blockquote]:border-gray-300 [&>blockquote]:pl-4 [&>blockquote]:italic [&>blockquote]:mb-2 [&>code]:bg-gray-100 [&>code]:px-1 [&>code]:py-0.5 [&>code]:rounded [&>code]:text-sm [&>pre]:bg-gray-50 [&>pre]:p-2 [&>pre]:rounded [&>pre]:overflow-x-auto [&>pre]:mb-2"
              v-html="renderMarkdown(tc.markdown)"
            ></div>
          </div>

          <!-- Source code -->
          <div v-if="showSource[tc.name]" class="border-t border-gray-100 pt-4">
            <div class="text-xs text-gray-500 mb-2 font-semibold">原始 Markdown</div>
            <pre class="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-auto max-h-64 font-mono">{{
              tc.markdown
            }}</pre>
            <div class="text-xs text-gray-500 mb-2 mt-4 font-semibold">转义后的 HTML 源码</div>
            <pre class="bg-gray-100 text-gray-800 p-4 rounded text-xs overflow-auto max-h-64 font-mono">{{
              escapeHtml(renderMarkdown(tc.markdown))
            }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Tips section -->
    <div class="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 class="font-semibold text-sm text-blue-800 mb-2">调试提示</h3>
      <ul class="text-sm text-blue-700 space-y-1 list-disc pl-5">
        <li>点击每个测试的标题可以展开/收起原始 Markdown 和渲染后的 HTML 源码</li>
        <li>选择「自定义输入」可以在左侧编辑内容，右侧实时预览渲染效果</li>
        <li>如果公式渲染失败，会显示红色错误信息</li>
        <li>打开浏览器 DevTools 可以检查具体的 DOM 结构和 CSS 样式</li>
      </ul>
    </div>
  </div>
</template>
