# Audit verification — 25 September 2026

The supplied ZIP tested commit `2784529`. This revision starts from `4fa1871`,
which already adds `adjustbox` and checks required TeX packages. The ZIP's
local PDFs are historical baseline artifacts. The `*-after.pdf` files here
were generated with the revised code on macOS using Pandoc 3.7.0.1 and TeX
Live 2025. Docker was unavailable locally. Render subsequently deployed commit
`6a6b125`, and `/ready` returned HTTP 200 with Pandoc 3.2, XeTeX (TeX Live
2026), and no startup warnings. This confirms the production image completed
the build/startup smoke render, but not every audit case has been tested live.

Before the revision, one bounded live POST of the supplied realistic report to
`https://typesetllm.onrender.com/convert` succeeded with HTTP 200 and a
29,094-byte PDF. This confirms the historical `adjustbox` outage was fixed in
the deployed `4fa1871` image; it does not verify the changes described below.

| Audit issue | Current status | Evidence |
| --- | --- | --- |
| Historical live conversion outage | Already fixed at `4fa1871` | One bounded realistic-report live POST returned HTTP 200. |
| Liveness despite broken renderer | Confirmed live | Docker build smoke plus startup `/ready` render; live `/ready` returned HTTP 200. `/health` remains independent liveness. |
| Small and multipage tables | Fixed locally | Case 02: 3 pages to 1 portrait. Case 08: 5 pages to 2 portrait with repeated headers. |
| Wide table collisions and spare pages | Confirmed live for supplied case | Case 03 is one landscape page instead of three; tested headings do not intersect. Live PDF is one landscape page with its end marker. |
| Realistic report label collision | Confirmed live for supplied case | Case 16: 3 pages to 1 portrait without label/value overlap. Live PDF is one portrait page with metadata and end marker. |
| Long code clipping | Confirmed live for supplied case | Case 07 end-of-line marker is visible and extractable in local and live PDFs. |
| Dollar and single-backslash math delimiters | Fixed locally | Cases 04 and 05 render equations; currency in case 14 remains literal. |
| Scientific superscript minus | Fixed locally | Case 06 shows the negative exponent in `10⁻³`. |
| Unsupported glyphs | Detected and warned | Case 06 lists specific Unicode code points; CJK, Arabic, Hindi and emoji still need full font support. |
| Missing image, unresolved citation, Mermaid | Detected and warned; unsupported input remains | Cases 10–12 surface actionable notices. |
| Title/author/date metadata | Fixed locally | Case 13 displays all three fields. |
| Malformed equation | Fixed error reporting | Case 15 returns an input error with reference; no PDF is presented. |
| Preview, retry, filename, stale output | Implemented locally; live browser interaction unverified | UI preview and warning display; source change aborts requests and clears old PDF. Live API returned `basic-formatting.pdf` filename and `X-Typeset-Warnings` header. |
| Basic, lists, long prose, repeated output | Preserved | 17/18 cases compile; no missing sentinels; case 01/18 text and page pixels match. |

Selected comparisons:

- Small table: [before](02_small_table-before.pdf) · [after](02_small_table-after.pdf)
- Wide table: [before](03_wide_table-before.pdf) · [after](03_wide_table-after.pdf)
- Long code: [before](07_long_code-before.pdf) · [after](07_long_code-after.pdf)
- Realistic report: [before](16_realistic_report-before.pdf) · [after](16_realistic_report-after.pdf)

`findings.json` records before/after page counts, and
`current-all-results.json` records every supplied case. PNG page images are
included for review. The sample documents contain synthetic test data.

Post-deployment live tests were sequential and bounded: `/ready` passed, then
cases 01, 16, 03, and 07 each returned HTTP 200 PDFs. PDF text extraction
confirmed their end markers; case 16 was one portrait page, case 03 one
landscape page, and case 07 preserved `END_LONG_LINE_927`. These do not imply
the remaining cases or interactive browser workflow were verified live.
