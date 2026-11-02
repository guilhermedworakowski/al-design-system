#!/usr/bin/env node
// Runs the AL evals: real requests (tasks.json) to Claude Code in headless
// mode, inside a throwaway project that has the package under test installed,
// then scores every page with score.mjs and writes a report.
//
//   node evals/run.mjs [--runs 3] [--modes plain,mcp] [--tasks login,signup]
//                      [--parallel 3] [--claude claude] [--dist dist]
//   node evals/run.mjs --rescore evals/results/<run>     score again, no AI
//
// Each request runs in two modes (decided 2026-11-01):
//   plain   the agent only knows the package is installed; it may read
//           node_modules like any agent would
//   mcp     the same, plus the package's MCP server (list_components,
//           get_component, get_tokens, validate_markup)
// The difference between the two is what the AI-ready layer is worth.
//
// It is not a build gate: an AI answers differently each time and a run uses
// the person's Claude plan. Run it before a release and keep the report in
// evals/results/ to compare versions. Node 18+, no dependency.

import { spawn } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadContext, score } from './score.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..');
// Same instruction for every request and both modes: where the package is,
// what file to write, and no questions back (nobody answers in headless mode).
const OUTPUT = '\n\nThis project uses the npm package al-design-system, already installed in '
  + 'node_modules. Write the whole page as one HTML file named page.html in the current folder. '
  + 'Do not ask questions: decide and write the file.';
const TOOLS = ['Read', 'Glob', 'Grep', 'Write', 'Edit'];

function args(argv) {
  const o = { runs: 3, modes: ['plain', 'mcp'], tasks: null, parallel: 3, claude: 'claude', dist: 'dist', rescore: null };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i].replace(/^--/, ''), v = argv[i + 1];
    if (k === 'runs' || k === 'parallel') { o[k] = Number(v); i++; }
    else if (k === 'modes' || k === 'tasks') { o[k] = v.split(','); i++; }
    else if (k in o) { o[k] = v; i++; }
    else throw new Error(`unknown option ${argv[i]}`);
  }
  return o;
}

function workspace(dist, mode) {
  const ws = mkdtempSync(join(tmpdir(), 'al-eval-'));
  const pkg = join(ws, 'node_modules', 'al-design-system');
  mkdirSync(pkg, { recursive: true });
  cpSync(join(ROOT, 'package.json'), join(pkg, 'package.json'));
  cpSync(dist, join(pkg, 'dist'), { recursive: true });
  writeFileSync(join(ws, 'package.json'), JSON.stringify({ name: 'eval-app', private: true,
    dependencies: { 'al-design-system': JSON.parse(readFileSync(join(ROOT, 'package.json'))).version } }, null, 2));
  const servers = mode === 'mcp'
    ? { al: { command: 'node', args: [join(pkg, 'dist', 'mcp', 'al.mjs'), 'mcp'] } } : {};
  writeFileSync(join(ws, 'mcp.json'), JSON.stringify({ mcpServers: servers }));
  return ws;
}

function claude(bin, ws, mode, prompt) {
  const tools = mode === 'mcp' ? [...TOOLS, 'mcp__al'] : TOOLS;
  const argv = ['-p', prompt + OUTPUT, '--output-format', 'stream-json', '--verbose',
    '--mcp-config', join(ws, 'mcp.json'), '--strict-mcp-config',
    '--allowedTools', tools.join(','), '--permission-mode', 'acceptEdits'];
  return new Promise((done) => {
    const p = spawn(bin, argv, { cwd: ws, stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '', err = '';
    p.stdout.on('data', (d) => { out += d; });
    p.stderr.on('data', (d) => { err += d; });
    p.on('error', (e) => done({ error: String(e) }));
    p.on('close', (code) => {
      const events = out.split('\n').filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
      const calls = events.filter((e) => e.type === 'assistant')
        .flatMap((e) => (e.message?.content || []).filter((c) => c.type === 'tool_use').map((c) => c.name));
      const result = events.find((e) => e.type === 'result') || {};
      done({ code, calls, turns: result.num_turns, cost: result.total_cost_usd,
             seconds: result.duration_ms && Math.round(result.duration_ms / 1000),
             error: code ? (err || result.result || 'exit ' + code).slice(0, 500) : undefined });
    });
  });
}

async function pool(jobs, n) {
  let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < jobs.length) await jobs[i++](); }));
}

function report(dir, rows, version) {
  const tasks = [...new Set(rows.map((r) => r.task))];
  const modes = ['plain', 'mcp'].filter((m) => rows.some((r) => r.mode === m));
  const avg = (xs) => (xs.length ? (xs.reduce((a, b) => a + b, 0) / xs.length).toFixed(1) : '-');
  const cell = (rs) => `${rs.filter((r) => r.pass).length}/${rs.length}`
    + ` · ${avg(rs.map((r) => r.contract.length))} / ${avg(rs.map((r) => r.unknown.length))}`
    + ` / ${avg(rs.map((r) => r.hardcoded.length))} / ${avg(rs.map((r) => r.missing.length))}`;
  const lines = [`# AL evals - ${version}`, '',
    'Each cell: pages that pass / runs · average contract breaks / invented classes / hand-written colors / missing CSS or JS.', '',
    `| task | ${modes.join(' | ')} |`, `|---|${modes.map(() => '---').join('|')}|`];
  for (const t of tasks) lines.push(`| ${t} | ${modes.map((m) => cell(rows.filter((r) => r.task === t && r.mode === m))).join(' | ')} |`);
  lines.push(`| **all** | ${modes.map((m) => cell(rows.filter((r) => r.mode === m))).join(' | ')} |`, '');
  for (const m of modes) {
    const rs = rows.filter((r) => r.mode === m);
    lines.push(`- ${m}: ${rs.filter((r) => !r.page).length} run(s) wrote no page; `
      + `MCP calls per run ${avg(rs.map((r) => (r.calls || []).filter((c) => c.startsWith('mcp__')).length))}; `
      + `px values per page ${avg(rs.map((r) => r.px || 0))}`);
  }
  writeFileSync(join(dir, 'report.md'), lines.join('\n') + '\n');
  return lines.join('\n');
}

async function rescore(dir, dist) {
  const ctx = await loadContext(dist);
  const meta = JSON.parse(readFileSync(join(dir, 'scores.json'), 'utf8'));
  const rows = meta.rows.map((r) => {
    const file = join(dir, 'pages', `${r.task}.${r.mode}.${r.run}.html`);
    const page = existsSync(file);
    const s = page ? score(readFileSync(file, 'utf8'), ctx)
      : { pass: false, used: [], contract: [], unknown: [], hardcoded: [], px: 0, missing: ['no page'] };
    return { ...r, page, ...s };
  });
  writeFileSync(join(dir, 'scores.json'), JSON.stringify({ ...meta, rows }, null, 1));
  console.log(report(dir, rows, meta.version));
}

const o = args(process.argv.slice(2));
const dist = resolve(ROOT, o.dist);
if (o.rescore) {
  await rescore(resolve(o.rescore), dist);
} else {
  const version = JSON.parse(readFileSync(join(dist, 'components.json'), 'utf8')).version;
  const stamp = new Date().toISOString().slice(0, 16).replace(/[-:]/g, '').replace('T', '-');
  const dir = join(HERE, 'results', `${version}-${stamp}`);
  mkdirSync(join(dir, 'pages'), { recursive: true });
  const all = JSON.parse(readFileSync(join(HERE, 'tasks.json'), 'utf8')).tasks;
  const tasks = o.tasks ? all.filter((t) => o.tasks.includes(t.id)) : all;
  const rows = [];
  const jobs = tasks.flatMap((t) => o.modes.flatMap((mode) => Array.from({ length: o.runs }, (_, k) => async () => {
    const ws = workspace(dist, mode);
    const r = await claude(o.claude, ws, mode, t.prompt);
    const page = join(ws, 'page.html');
    const wrote = existsSync(page);
    if (wrote) cpSync(page, join(dir, 'pages', `${t.id}.${mode}.${k + 1}.html`));
    rows.push({ task: t.id, mode, run: k + 1, ...r });
    rmSync(ws, { recursive: true, force: true });
    console.error(`${t.id} ${mode} ${k + 1}: ${r.error ? 'error' : wrote ? 'ok' : 'no page'} (${rows.length}/${jobs.length})`);
  })));
  await pool(jobs, o.parallel);
  rows.sort((a, b) => `${a.task}.${a.mode}.${a.run}`.localeCompare(`${b.task}.${b.mode}.${b.run}`));
  writeFileSync(join(dir, 'scores.json'), JSON.stringify({ version, date: stamp, runs: o.runs, rows }, null, 1));
  await rescore(dir, dist);
}
