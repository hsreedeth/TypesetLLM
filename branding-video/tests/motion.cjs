const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../src/scene.tsx'), 'utf8');
const root = fs.readFileSync(path.join(__dirname, '../src/root.tsx'), 'utf8');
assert.match(root, /durationInFrames=\{270\} fps=\{30\} width=\{1920\} height=\{1080\}/);
for (const text of ['codex mcp add typesetllm --url', 'convert_markdown_to_pdf', 'report.pdf saved', 'Quarterly report', 'E = mc²', "print('ready')"]) assert.ok(source.includes(text), text);
console.log('MCP demo storyboard: 9 seconds at 1080p.');
