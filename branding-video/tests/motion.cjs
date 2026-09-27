const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');

const source = fs.readFileSync(path.join(__dirname, '../src/scene.tsx'), 'utf8');
const {outputText} = ts.transpileModule(source, {
  compilerOptions: {module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX},
});
const scene = {exports: {}};
new Function('require', 'module', 'exports', outputText)(require, scene, scene.exports);
const {reelPositionAt, wordTimeline} = scene.exports;

assert.deepEqual(wordTimeline.slice(0, 5).map(({name}) => name), ['ChatGPT', 'Claude', 'Gemini', 'Kimi.ai', 'DeepSeek']);
assert.ok(wordTimeline.slice(1, 5).every(({at}, index) => at - wordTimeline[index].at >= 0.399));

wordTimeline.forEach(({at}, index) => {
  assert.ok(Math.abs(reelPositionAt(at) - index) < 1e-7, `Name ${index} reaches its keyframe`);
  if (index === 0 || index === wordTimeline.length - 1) return;
  const epsilon = 0.0001;
  const before = (reelPositionAt(at) - reelPositionAt(at - epsilon)) / epsilon;
  const after = (reelPositionAt(at + epsilon) - reelPositionAt(at)) / epsilon;
  assert.ok(Math.abs(before - after) < 0.05, `Velocity is continuous at name ${index}`);
});

let previous = reelPositionAt(0);
for (let frame = 1; frame < 228; frame++) {
  const position = reelPositionAt(frame / 60);
  assert.ok(position >= previous, `Reel never jumps backwards at frame ${frame}`);
  assert.ok(position - previous < 0.2, `Reel has no oversized jump at frame ${frame}`);
  previous = position;
}
assert.equal(reelPositionAt(3.8), wordTimeline.length - 1);
console.log('Smooth reel timing passed at 60 fps.');
