// MCP server on stdio, written by hand: JSON-RPC 2.0, one message per line.
// No SDK, so the package keeps zero dependencies.
//
// Tools:
//   list_components   name, title, one-line summary and root class of each
//   get_component     imports, the markup to write, the contract rules and
//                     the usage guidelines of one component
//   get_tokens        the Foundation tokens, semantic colors first
//   validate_markup   checks HTML against the markup contract

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { createInterface } from 'node:readline';
import { parse } from './html.mjs';
import { check, checkAll } from './contract.mjs';

const PROTOCOLS = ['2025-06-18', '2025-03-26', '2024-11-05'];

const TOOLS = [
  {
    name: 'list_components',
    description: 'Lists every AL Design System component: name, title, one-line summary and root CSS class. Start here to pick a component.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'get_component',
    description: 'Everything needed to use one component: the CSS (and JS) to import, the exact HTML to write with its modifiers, the markup rules a validator enforces, and the usage guidelines.',
    inputSchema: {
      type: 'object',
      properties: { name: { type: 'string', description: 'Component name, as in list_components (e.g. "button", "number-field").' } },
      required: ['name'],
    },
  },
  {
    name: 'get_tokens',
    description: 'The Foundation design tokens as CSS custom properties. "semantic" (default) gives the color roles with their light and dark values and when to use each - use these, never raw hex; "all" adds the palette, type, space, radius, motion and elevation.',
    inputSchema: {
      type: 'object',
      properties: { scope: { type: 'string', enum: ['semantic', 'all'] } },
    },
  },
  {
    name: 'validate_markup',
    description: 'Checks HTML against the AL markup contract (the same rules the AL build enforces). Returns each break with the line, the element and the rule. Run it on every snippet you write.',
    inputSchema: {
      type: 'object',
      properties: {
        html: { type: 'string', description: 'An HTML page or fragment.' },
        component: { type: 'string', description: 'Only this component\'s rules (optional).' },
      },
      required: ['html'],
    },
  },
];

function rulesText(entry) {
  const line = (r) => `- ${r.id}${r.rule ? ` (guideline rule ${r.rule})` : ''}: ${r.why}`;
  return [
    'Checked by validate_markup:', ...entry.rules.map(line),
    ...(entry.manual.length ? ['', 'Not checked automatically - follow them yourself:', ...entry.manual.map(line)] : []),
  ].join('\n');
}

function getComponent(catalog, dist, name) {
  const entry = catalog.components[name];
  if (!entry) {
    throw new Error(`no component "${name}". Known: ${Object.keys(catalog.components).join(', ')}`);
  }
  const imports = [
    'al-design-system/foundation.css   (once, before any component)',
    `al-design-system/${entry.css}`,
    ...(entry.js ? [`al-design-system/${entry.js}   (behavior; load it as a module)`] : []),
    'or everything at once: al-design-system/al.css',
  ];
  const guide = entry.guidelines && existsSync(join(dist, entry.guidelines))
    ? readFileSync(join(dist, entry.guidelines), 'utf8') : '(no usage guidelines for this component)';
  return [
    `# ${entry.title} (.${entry.root})`, '', entry.summary, '',
    '## Import', ...imports, '',
    '## Markup', entry.markup, '',
    '## Markup rules', rulesText(entry), '',
    '## Usage guidelines', guide,
  ].join('\n');
}

function getTokens(dist, scope) {
  const tokens = JSON.parse(readFileSync(join(dist, 'tokens.json'), 'utf8'));
  const semantic = Object.entries(tokens.color.semantic)
    .map(([k, v]) => `--al-${k}: light ${v[0]}, dark ${v[1]}`
      + (tokens.color.usage?.[k] ? ` - ${tokens.color.usage[k]}` : ''));
  const out = [
    `AL Design System ${tokens.meta.version} - tokens. Use var(--al-<name>); the dark values apply`,
    'under [data-theme="dark"] or prefers-color-scheme, never write them by hand.', '',
    '## Semantic colors', ...semantic,
  ];
  if (scope === 'all') {
    const { meta, contrastReport, ...rest } = tokens;
    out.push('', '## Everything else (JSON)', JSON.stringify(rest, null, 1));
  }
  return out.join('\n');
}

function validateMarkup(catalog, html, component) {
  const root = parse(html);
  let results;
  if (component) {
    const entry = catalog.components[component];
    if (!entry) throw new Error(`no component "${component}"`);
    results = [{ component, ...check(root, entry.rules) }];
  } else {
    results = checkAll(root, catalog);
  }
  const found = results.flatMap((r) => r.findings.map((f) => `${r.component}: ${f}`));
  const seen = results.filter((r) => r.seen).map((r) => r.component);
  if (!seen.length) return 'No AL component found in this HTML - nothing was checked.';
  return found.length
    ? `${found.length} break(s):\n${found.join('\n')}`
    : `ok - ${seen.join(', ')} follow the markup contract.`;
}

function callTool(catalog, dist, name, args = {}) {
  switch (name) {
    case 'list_components':
      return Object.entries(catalog.components)
        .map(([k, e]) => `${k} (.${e.root}) - ${e.title}: ${e.summary}`).join('\n');
    case 'get_component': return getComponent(catalog, dist, args.name);
    case 'get_tokens': return getTokens(dist, args.scope);
    case 'validate_markup': return validateMarkup(catalog, String(args.html ?? ''), args.component);
    default: throw new Error(`unknown tool "${name}"`);
  }
}

export function handle(catalog, dist, msg) {
  const { id, method, params = {} } = msg;
  const reply = (result) => ({ jsonrpc: '2.0', id, result });
  switch (method) {
    case 'initialize':
      return reply({
        protocolVersion: PROTOCOLS.includes(params.protocolVersion) ? params.protocolVersion : PROTOCOLS[0],
        capabilities: { tools: {} },
        serverInfo: { name: 'al-design-system', version: catalog.version },
        instructions: 'AL Design System: plain CSS components. Call list_components, then get_component before writing markup, use semantic tokens from get_tokens, and run validate_markup on what you write.',
      });
    case 'ping': return reply({});
    case 'tools/list': return reply({ tools: TOOLS });
    case 'tools/call':
      try {
        return reply({ content: [{ type: 'text', text: callTool(catalog, dist, params.name, params.arguments) }] });
      } catch (e) {
        return reply({ content: [{ type: 'text', text: e.message }], isError: true });
      }
    default:
      if (id === undefined) return null; // a notification: no answer
      return { jsonrpc: '2.0', id, error: { code: -32601, message: `method not found: ${method}` } };
  }
}

export function serve(catalog, dist) {
  const rl = createInterface({ input: process.stdin });
  rl.on('line', (line) => {
    if (!line.trim()) return;
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'parse error' } }) + '\n');
      return;
    }
    const out = handle(catalog, dist, msg);
    if (out) process.stdout.write(JSON.stringify(out) + '\n');
  });
}
