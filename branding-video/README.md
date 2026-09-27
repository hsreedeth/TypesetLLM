# Branding finale

The fourth slide is a prerendered Remotion composition. Rendered output is
checked in at `../web/branding/branding-4.mp4`, so the production Python image
does not need Node, Chrome or a video-rendering step.

To regenerate it locally, run `npm ci` and `npm run render` in this directory.
Remotion downloads Chrome Headless Shell on first use. If that download is not
available, run the render command with a local `--browser-executable` path.

The clip is 2160 × 1536 at 60 fps for 3.8 seconds, matching the new image slides. It begins with
TypesetChatGPT, keeps `Typeset` fixed while Claude, Gemini, Kimi.ai and
DeepSeek each receive one readable pass, runs through one short rapid roll,
then decelerates and holds on `TypesetLLM`. There is no per-name opacity
animation or blur filter; only the slot edges fade gently. Run
`npm run test:motion` to check
that the reel never moves backwards or jumps between names. Inter is
bundled from the repository's licensed font file. The original fourth image is
retained as `../web/branding/branding-4-poster.png`; the carousel uses a
rendered first-frame poster so playback does not flash the final title first.
