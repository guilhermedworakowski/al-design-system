#!/usr/bin/env node
// The package's command: npx al-design-system <validate|mcp|help>
//
//   validate <file.html ...>   checks the AL markup contract on each page;
//                              exits 1 when a rule breaks. --skip <selector>
//                              leaves a subtree out (default: [inert]);
//                              --json prints the findings per component
//   mcp                        an MCP server on stdio, for AI agents: lists the
//                              components, gives each one's markup, rules and
//                              guidelines, the tokens, and validates HTML
//
// Same version as the CSS it sits next to: the catalog it reads is
// ../components.json of this very package. No dependency, nothing runs on
// install - a project that only imports the CSS never touches this file.

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from './html.mjs';
import { checkAll } from './contract.mjs';
import { serve } from './server.mjs';

const DIST = join(dirname(fileURLToPath(import.meta.url)), '..');
const catalog = JSON.parse(readFileSync(join(DIST, 'components.json'), 'utf8'));

const HELP = `AL Design System ${catalog.version}

  npx al-design-system validate <file.html ...>   check the markup contract
      --json              findings per component, one JSON line per file
      --skip <selector>   leave a subtree out (default: [inert])
  npx al-design-system mcp                        MCP server on stdio

The rules are in node_modules/al-design-system/dist/components.json.`;

function validate(args) {
  const files = [];
  let skip = '[inert]';
  let json = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help' || args[i] === '-h') {
      console.log(HELP);
      return 0;
    }
    if (args[i] === '--skip') skip = args[++i];
    else if (args[i] === '--json') json = true;
    else files.push(args[i]);
  }
  if (!files.length) {
    console.error('validate: give one or more .html files');
    return 2;
  }
  let breaks = 0;
  for (const file of files) {
    const results = checkAll(parse(readFileSync(file, 'utf8')), catalog, { skip });
    if (json) {
      console.log(JSON.stringify({ file, results }));
      breaks += results.reduce((n, r) => n + r.findings.length, 0);
      continue;
    }
    const found = results.flatMap((r) => r.findings.map((f) => `${r.component}: ${f}`));
    const seen = results.filter((r) => r.seen).map((r) => r.component);
    breaks += found.length;
    console.log(`${file}: ${found.length ? found.length + ' break(s)' : 'ok'}` +
                ` (${seen.length ? seen.join(', ') : 'no AL component found'})`);
    for (const f of found) console.log('  ' + f);
  }
  return breaks ? 1 : 0;
}

const [cmd, ...args] = process.argv.slice(2);
if (cmd === 'validate') process.exitCode = validate(args);
else if (cmd === 'mcp') serve(catalog, DIST);
else console.log(HELP);
