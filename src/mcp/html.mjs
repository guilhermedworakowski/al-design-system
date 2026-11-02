// HTML reader for the validator, the Node twin of tools/htmltree.py.
//
// Builds the same tree: each node is {tag, attrs, kids, text, line, parent}.
// What stays out: comments and the content of <style> and <script>.
// <template> goes in, because that is where the markup the JS inserts later
// lives (Toast, Alert). No dependency: the package installs nothing.

const VOID = new Set([
  'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
  'meta', 'source', 'track', 'wbr',
  // SVG shapes: a <path> without the slash must not swallow its siblings
  'path', 'circle', 'line', 'rect', 'polyline', 'polygon', 'ellipse',
]);
const RAW = new Set(['style', 'script']);
const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };

export function decode(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const n = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(n) ? String.fromCodePoint(n) : m;
    }
    return ENTITIES[e.toLowerCase()] ?? m;
  });
}

const ATTR = /([^\s"'>\/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g;

function parseAttrs(src) {
  const attrs = {};
  for (const m of src.matchAll(ATTR)) {
    const name = m[1].toLowerCase();
    const value = m[2] ?? m[3] ?? m[4] ?? '';
    if (!(name in attrs)) attrs[name] = decode(value);
  }
  return attrs;
}

export function parse(html) {
  const root = { tag: '#root', attrs: {}, kids: [], text: '', line: 0, parent: null };
  const stack = [root];
  let i = 0;
  let line = 1;
  const advance = (to) => {
    for (let k = i; k < to; k++) if (html.charCodeAt(k) === 10) line++;
    i = to;
  };

  while (i < html.length) {
    const lt = html.indexOf('<', i);
    if (lt === -1) {
      stack[stack.length - 1].text += decode(html.slice(i));
      break;
    }
    if (lt > i) {
      stack[stack.length - 1].text += decode(html.slice(i, lt));
      advance(lt);
    }
    if (html.startsWith('<!--', i)) {
      const end = html.indexOf('-->', i + 4);
      advance(end === -1 ? html.length : end + 3);
      continue;
    }
    if (html[i + 1] === '!' || html[i + 1] === '?') {
      const end = html.indexOf('>', i);
      advance(end === -1 ? html.length : end + 1);
      continue;
    }
    const close = html[i + 1] === '/';
    const m = /^<\/?([a-zA-Z][a-zA-Z0-9-]*)/.exec(html.slice(i, i + 64));
    if (!m) {
      stack[stack.length - 1].text += '<';
      advance(i + 1);
      continue;
    }
    // the end of the tag, skipping '>' inside quoted attribute values
    let j = i + m[0].length;
    let quote = null;
    for (; j < html.length; j++) {
      const ch = html[j];
      if (quote) { if (ch === quote) quote = null; }
      else if (ch === '"' || ch === "'") quote = ch;
      else if (ch === '>') break;
    }
    const tag = m[1].toLowerCase();
    const body = html.slice(i + m[0].length, j);
    const tagLine = line;
    advance(Math.min(j + 1, html.length));

    if (close) {
      if (VOID.has(tag)) continue;
      for (let k = stack.length - 1; k > 0; k--) {
        if (stack[k].tag === tag) { stack.length = k; break; }
      }
      continue;
    }
    if (RAW.has(tag)) {
      const end = html.toLowerCase().indexOf(`</${tag}`, i);
      const stop = end === -1 ? html.length : html.indexOf('>', end) + 1;
      advance(stop);
      continue;
    }
    const selfClosed = /\/\s*$/.test(body);
    const node = {
      tag, attrs: parseAttrs(selfClosed ? body.replace(/\/\s*$/, '') : body),
      kids: [], text: '', line: tagLine, parent: stack[stack.length - 1],
    };
    stack[stack.length - 1].kids.push(node);
    if (!VOID.has(tag) && !selfClosed) stack.push(node);
  }
  return root;
}

export function* walk(node) {
  for (const k of node.kids) {
    yield k;
    yield* walk(k);
  }
}

export const classes = (node) => (node.attrs.class || '').split(/\s+/).filter(Boolean);

export function* ancestors(node) {
  let p = node.parent;
  while (p && p.tag !== '#root') {
    yield p;
    p = p.parent;
  }
}

export const textOf = (node) => (node.text + node.kids.map(textOf).join('')).trim();
