# AL evals

Real requests to an AI agent working in a project that has `al-design-system` installed, scored by the package's own checks. They answer one question with a number: does the AI-ready layer (the catalog, the guidelines and the MCP server) make an agent write correct AL?

Each request in [`tasks.json`](tasks.json) runs in two modes, three times each:

- **plain**: the agent only knows the package is installed (it can read `node_modules`);
- **mcp**: the same, plus the package's MCP server.

[`score.mjs`](score.mjs) gives every page four counts, all automatic: markup contract breaks (the package's validator), invented `al-` classes, colors written by hand instead of `var(--al-...)`, and component CSS or JS left out. A page passes when all four are zero.

## Run

Needs Node 18+ and [Claude Code](https://docs.claude.com/en/docs/claude-code) signed in (`claude` on the PATH). A full run is 72 requests on your Claude plan.

```bash
python3 build.py                       # the package under test is dist/
node evals/run.mjs                     # 12 tasks x 2 modes x 3 runs
node evals/run.mjs --tasks login --runs 1   # a quick check
```

Each run writes `evals/results/<version>-<date>/`: the pages, `scores.json` and `report.md`. Keep the folder in git to compare versions. `node evals/run.mjs --rescore <folder>` scores a run again without calling the AI.

This is not a build gate: an AI answers differently each time, and a run costs plan usage. Run it before a release.
