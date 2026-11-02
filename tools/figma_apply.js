// Applies build/figma-descriptions.json to one page of the Figma library.
// tools/figma_desc.py writes build/figma-apply.js from this file with the
// data in place of __DATA__; run it through the Figma MCP (use_figma) once per
// page, with the page id in place of __PAGE__.
//
// A component set (or a component outside a set) is matched by its name in
// kebab case ("Icon Button" -> icon-button); internal pieces by their exact
// name. The generated block is replaced; a designer note below the separator
// line stays. A description with no separator is a note only if it was not
// generated - otherwise reapplying would keep the old block as a note.
const M = __DATA__;
const SEP = '\n' + M.separator + '\n';
const page = await figma.getNodeByIdAsync('__PAGE__');
await figma.setCurrentPageAsync(page);
const nodes = page.findAllWithCriteria({ types: ['COMPONENT_SET', 'COMPONENT'] })
  .filter(n => n.type === 'COMPONENT_SET' || n.parent.type !== 'COMPONENT_SET');
const generated = t => /MCP get_component |^Internal piece of /.test(t);
// The getter returns the text escaped as HTML; writing it back as is would
// escape it twice (&amp;quot;).
const unescape = t => t.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
  .replace(/&#39;/g, "'").replace(/&amp;/g, '&');
const updated = [], skipped = [];
for (const n of nodes) {
  const key = n.name.startsWith('_') ? n.name : n.name.toLowerCase().replace(/ /g, '-');
  const entry = M.components[key] || M.internal[key];
  if (!entry) { skipped.push(n.name); continue; }
  const old = unescape(n.description || '');
  const note = old.includes(SEP) ? old.split(SEP).slice(1).join(SEP).trim()
    : (generated(old) ? '' : old.trim());
  n.description = entry.description + (note ? SEP + note : '');
  n.documentationLinks = [{ uri: entry.link }];
  updated.push({ id: n.id, name: n.name, note: !!note });
}
return { page: page.name, updated, skipped };
