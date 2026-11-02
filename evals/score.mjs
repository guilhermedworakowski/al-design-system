#!/usr/bin/env node
// Scores one HTML page an AI agent wrote with AL, using the package under
// test - its own validator, catalog and CSS - so the eval measures the same
// contract a consumer gets from npm.
//
//   node evals/score.mjs <dist folder> <page.html ...>     prints JSON
//
// Four checks, all automatic (decided 2026-11-01):
//   contract      rules of the markup contract that break (the package's
//                 validator, the same one `al-design-system validate` runs)
//   unknown       al- classes that no AL stylesheet or markup contract names
//                 (invented)
//   hardcoded     colors written by hand (hex, rgb, hsl) in style attributes
//                 or <style> blocks instead of var(--al-...); px values are
//                 counted apart, as information, because layout can need them
//   missing       a component used without its CSS (al.css, or foundation.css
//                 plus components/<name>.css) or without its JS
// A page passes when all four are zero and it uses at least one component.

import { readFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

export async function loadContext(dist) {
  dist = resolve(dist);
  const { parse, walk, classes } = await import(pathToFileURL(join(dist, 'mcp', 'html.mjs')));
  const { checkAll } = await import(pathToFileURL(join(dist, 'mcp', 'contract.mjs')));
  const catalog = JSON.parse(readFileSync(join(dist, 'components.json'), 'utf8'));
  const known = new Set();
  const sheets = ['al.css', 'foundation.css',
    ...readdirSync(join(dist, 'components')).filter((f) => f.endsWith('.css')).map((f) => `components/${f}`)];
  for (const f of sheets) {
    for (const m of readFileSync(join(dist, f), 'utf8').matchAll(/\.(al-[\w-]+)/g)) known.add(m[1]);
  }
  // a class can be part of the contract without a style of its own (the
  // Breadcrumb root, the Toast live regions): the markup names it too
  for (const e of Object.values(catalog.components)) {
    for (const m of (e.markup || '').matchAll(/class="([^"]*)"/g)) {
      for (const c of m[1].split(/\s+/)) if (c.startsWith('al-')) known.add(c);
    }
  }
  return { parse, walk, classes, checkAll, catalog, known };
}

const COLOR = /#[0-9a-fA-F]{3,8}\b|\b(?:rgb|hsl)a?\(/g;
const PX = /(?<![\w.-])(?!0px)\d+(?:\.\d+)?px\b/g;

export function score(html, ctx) {
  const { parse, walk, classes, checkAll, catalog, known } = ctx;
  const root = parse(html);
  const nodes = [...walk(root)];

  const contract = checkAll(root, catalog, { skip: '[inert]' })
    .flatMap((r) => r.findings.map((f) => `${r.component}: ${f}`));

  const unknown = [...new Set(nodes.flatMap(classes)
    .filter((c) => c.startsWith('al-') && !known.has(c)))];

  // The package parser drops <style> and <script> (the contract never looks
  // inside them), so those two are read from the raw text.
  const blocks = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map((m) => m[1]);
  const scripts = [...html.matchAll(/<script\b[^>]*\bsrc\s*=\s*["']([^"']+)["']/gi)].map((m) => m[1]);
  const styles = [...nodes.filter((n) => n.attrs.style).map((n) => n.attrs.style), ...blocks].join('\n');
  // var(--al-x, #fff) fallbacks count too: the value is still written by hand
  const hardcoded = styles.match(COLOR) || [];
  const px = (styles.match(PX) || []).length;

  const refs = [
    ...nodes.filter((n) => n.tag === 'link').map((n) => n.attrs.href || ''),
    ...scripts,
    ...[...styles.matchAll(/@import\s+(?:url\()?["']?([^"')\s;]+)/g)].map((m) => m[1]),
  ];
  const has = (file) => refs.some((r) => r.endsWith(file) || r.includes(`/${file}`) || r.includes(`al-design-system/${file}`));
  const bundle = has('al.css');
  const used = Object.entries(catalog.components)
    .filter(([, e]) => nodes.some((n) => classes(n).includes(e.root)))
    .map(([name]) => name);
  const missing = [];
  if (used.length && !bundle && !has('foundation.css')) missing.push('foundation.css');
  for (const name of used) {
    const e = catalog.components[name];
    if (!bundle && !has(e.css)) missing.push(e.css);
    if (e.js && !has(e.js)) missing.push(e.js);
  }

  const pass = used.length > 0 && !contract.length && !unknown.length && !hardcoded.length && !missing.length;
  return { pass, used, contract, unknown, hardcoded, px, missing };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [dist, ...files] = process.argv.slice(2);
  if (!dist || !files.length) {
    console.error('usage: node evals/score.mjs <dist folder> <page.html ...>');
    process.exit(2);
  }
  const ctx = await loadContext(dist);
  for (const f of files) console.log(JSON.stringify({ file: f, ...score(readFileSync(f, 'utf8'), ctx) }));
}
