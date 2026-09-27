# MCP demo video

The 9-second, 1920 × 1080 Remotion composition shows a Codex connection, a conversion request, and a sample PDF with a table, equation, and code block. The checked-in H.264 output is `../web/branding/mcp-demo.mp4`; the Python deployment does not need Node or Chrome.

Run `npm ci`, then `npm run render` here to regenerate the clip. Pass a suitable `--browser-executable` if Remotion cannot find Chrome. Run `npm run test:motion` for the storyboard check.

The preview is illustrative. The actual MCP tool returns a temporary HTTPS download URL, which the client can save in its workspace.
