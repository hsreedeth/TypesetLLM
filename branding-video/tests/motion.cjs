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

wordTimeline.forEach(({at}, index) => {
  assert.ok(Math.abs(reelPositionAt(at) - index) < 1e-7, `Name ${index} reaches its keyframe`);
  if (index === 0 || index === wordTimeline.length - 1) return;
  const epsilon = 0.0001;
  const before = (reelPositionAt(at) - reelPositionAt(at - epsilon)) / epsilon;
  const after = (reelPositionAt(at + epsilon) - reelPositionAt(at)) / epsilon;
  assert.ok(Math.abs(before - after) < 0.05, `Velocity is continuous at name ${index}`);
});

let previous = reelPositionAt(0);
for (let frame = 1; frame < 810; frame++) {
  const position = reelPositionAt(frame / 60);
  assert.ok(position >= previous, `Reel never jumps backwards at frame ${frame}`);
  assert.ok(position - previous < 0.2, `Reel has no oversized jump at frame ${frame}`);
  previous = position;
}
assert.equal(reelPositionAt(13.5), wordTimeline.length - 1);
console.log('Smooth reel timing passed at 60 fps.');
