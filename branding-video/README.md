# Branding finale

The fourth slide is a prerendered Remotion composition. Rendered output is
checked in at `../web/branding/branding-4.mp4`, so the production Python image
does not need Node, Chrome or a video-rendering step.

To regenerate it locally, run `npm ci` and `npm run render` in this directory.
Remotion downloads Chrome Headless Shell on first use. If that download is not
available, run the render command with a local `--browser-executable` path.

The clip is 814 × 792 at 30 fps for 11 seconds. It begins with
TypesetChatGPT, cycles through Claude, Gemini, Kimi.ai and DeepSeek with
increasing speed and blur, decelerates, and holds on TypesetLLM. Inter is
bundled from the repository's licensed font file. The original fourth image is
retained as `../web/branding/branding-4-poster.png`; the carousel uses a
rendered first-frame poster so playback does not flash the final title first.
