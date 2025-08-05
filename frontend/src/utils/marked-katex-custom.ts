/* eslint-disable */
import type { KatexOptions } from 'katex';
import type { MarkedExtension } from 'marked';
import katex from 'katex';

const inlineRule = /^(\${1,2})(?!\$)((?:\\.|[^\\\n])*?(?:\\.|[^\\\n\$]))\1(?=[\s?!\.,:？！。，：]|$)/;
const inlineRuleNonStandard = /^(\${1,2})(?!\$)((?:\\.|[^\\\n])*?(?:\\.|[^\\\n\$]))\1/; // Non-standard, even if there are no spaces before and after $ or $$, try to parse

const blockRule = /^(\${1,2})\n((?:\\[^]|[^\\])+?)\n\1(?:\n|$)/;
const blockRuleNonStandard = /^(\${1,2})\n?((?:\\[^]|[^\\])+?)\n?\1(?:\n|$)/;

const inlineRuleParenthes = /^(\\\()\s*((?:\\[^]|[^\\\]])+?)\s*(\\\))/;
const blockRuleBracket = /^(\\\[)\s*((?:\\[^]|[^\\\]])+?)\s*(\\\])(?:\n|[\s?!\.,:？！。，：]|$)/;

export interface MarkedKatexOptions extends KatexOptions {
  nonStandard?: boolean;
}

export default function markedKatex(options?: MarkedKatexOptions): MarkedExtension {
  return {
    extensions: [
      inlineKatex(options || {}, createRenderer(options || {}, false)),
      blockKatex(options || {}, createRenderer(options || {}, true)),
      inlineKatexParenthes(options || {}, createRenderer(options || {}, false)),
      blockKatexBracket(options || {}, createRenderer(options || {}, true)),
      inlineKatexBracket(options || {}, createRenderer(options || {}, true)),
    ],
  };
}

function createRenderer(options: MarkedKatexOptions, newlineAfter: boolean) {
  return (token: any) =>
    katex.renderToString(token.text, { ...options, displayMode: token.displayMode }) + (newlineAfter ? '\n' : '');
}

function inlineKatex(options: MarkedKatexOptions, renderer: any) {
  const nonStandard = options && options.nonStandard;
  const ruleReg = nonStandard ? inlineRuleNonStandard : inlineRule;
  return {
    name: 'inlineKatex',
    level: 'inline' as const,
    start(src: string) {
      let index;
      let indexSrc = src;

      while (indexSrc) {
        index = indexSrc.indexOf('$');
        if (index === -1) {
          return;
        }
        const f = nonStandard ? index > -1 : index === 0 || indexSrc.charAt(index - 1) === ' ';
        if (f) {
          const possibleKatex = indexSrc.substring(index);

          if (possibleKatex.match(ruleReg)) {
            return index;
          }
        }

        indexSrc = indexSrc.substring(index + 1).replace(/^\$+/, '');
      }
    },
    tokenizer(src: string, tokens: any) {
      const match = src.match(ruleReg);
      if (match) {
        return {
          type: 'inlineKatex',
          raw: match[0],
          text: match[2].trim(),
          displayMode: match[1].length === 2,
        };
      }
    },
    renderer,
  };
}

function inlineKatexParenthes(options: MarkedKatexOptions, renderer: any) {
  return {
    name: 'inlineKatexParenthes',
    level: 'inline' as const,

    start(src: string) {
      let index,
        indexSrc = src;
      while (indexSrc) {
        index = indexSrc.indexOf('(');
        if (index === -1 || index < 1) {
          return;
        }

        if (indexSrc.charAt(index - 1) !== '\\') {
          return;
        }

        const possibleKatex = indexSrc.substring(index - 1);
        if (possibleKatex.match(inlineRuleParenthes)) {
          return index - 1;
        }

        indexSrc = indexSrc.substring(index + 1).replace(/^(\\\()+/, '');
      }
    },
    tokenizer(src: string, tokens: any) {
      const match = src.match(inlineRuleParenthes);
      if (match) {
        return {
          type: 'inlineKatex',
          raw: match[0],
          text: match[2].trim(),
          displayMode: false,
        };
      }
    },
    renderer,
  };
}

function blockKatex(options: MarkedKatexOptions, renderer: any) {
  const nonStandard = options && options.nonStandard;
  const ruleReg = nonStandard ? blockRuleNonStandard : blockRule;
  return {
    name: 'blockKatex',
    level: 'block' as const,
    start(src: string) {
      let index;
      let indexSrc = src;

      while (indexSrc) {
        index = indexSrc.indexOf('$');
        if (index === -1) {
          return;
        }
        if (indexSrc.charAt(index + 1) !== '$') {
          return;
        }
        const lineStart = indexSrc.substring(0, index).lastIndexOf('\n') + 1;
        if (!/^\s*$/.test(indexSrc.substring(lineStart, index))) {
          return;
        }
        const possibleKatex = indexSrc.substring(index);

        if (possibleKatex.match(ruleReg)) {
          return index;
        }

        indexSrc = indexSrc.substring(index + 1).replace(/^\$+/, '');
      }
    },
    tokenizer(src: string, tokens: any) {
      const match = src.match(ruleReg);
      if (match) {
        return {
          type: 'blockKatex',
          raw: match[0],
          text: match[2].trim(),
          displayMode: match[1].length === 2,
        };
      }
    },
    renderer,
  };
}

function blockKatexBracket(options: MarkedKatexOptions, renderer: any) {
  return {
    name: 'blockKatexBracket',
    level: 'block' as const,

    start(src: string) {
      let index,
        indexSrc = src;
      while (indexSrc) {
        index = indexSrc.indexOf('[');

        if (index === -1 || index < 1) {
          return;
        }

        if (indexSrc.charAt(index - 1) !== '\\') {
          return;
        }

        const possibleKatex = indexSrc.substring(index - 1);
        if (possibleKatex.match(blockRuleBracket)) {
          return index - 1;
        }

        indexSrc = indexSrc.substring(index + 1).replace(/^(\\\[)+/, '');
      }
    },
    tokenizer(src: string, tokens: any) {
      const match = src.match(blockRuleBracket);

      if (match) {
        return {
          type: 'blockKatex',
          raw: match[0],
          text: match[2].trim(),
          displayMode: true,
        };
      }
    },
    renderer,
  };
}

function inlineKatexBracket(options: MarkedKatexOptions, renderer: any) {
  return {
    name: 'inlineKatexBracket',
    level: 'inline' as const,

    start(src: string) {
      let index,
        indexSrc = src;
      while (indexSrc) {
        index = indexSrc.indexOf('[');

        if (index === -1 || index < 1) {
          return;
        }

        if (indexSrc.charAt(index - 1) !== '\\') {
          return;
        }

        const possibleKatex = indexSrc.substring(index - 1);
        if (possibleKatex.match(blockRuleBracket)) {
          return index - 1;
        }

        indexSrc = indexSrc.substring(index + 1).replace(/^(\\\[)+/, '');
      }
    },
    tokenizer(src: string, tokens: any) {
      const match = src.match(blockRuleBracket);

      if (match) {
        return {
          type: 'blockKatex',
          raw: match[0],
          text: match[2].trim(),
          displayMode: true,
        };
      }
    },
    renderer,
  };
}
