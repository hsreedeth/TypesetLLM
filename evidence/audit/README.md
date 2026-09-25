# Audit verification — 25 September 2026

The supplied ZIP tested commit `2784529`. This revision starts from `4fa1871`,
which already adds `adjustbox` and checks required TeX packages. The ZIP's
local PDFs are historical baseline artifacts. The `*-after.pdf` files here
were generated with the revised code on macOS using Pandoc 3.7.0.1 and TeX
Live 2025. Docker was unavailable locally, so the production image build and
the revised live behavior remain unverified until Render redeploys this commit.

Before the revision, one bounded live POST of the supplied realistic report to
`https://typesetllm.onrender.com/convert` succeeded with HTTP 200 and a
29,094-byte PDF. This confirms the historical `adjustbox` outage was fixed in
the deployed `4fa1871` image; it does not verify the changes described below.

| Audit issue | Current status | Evidence |
| --- | --- | --- |
| Historical live conversion outage | Already fixed at `4fa1871` | One bounded realistic-report live POST returned HTTP 200. |
| Liveness despite broken renderer | Fixed locally; revised deployment unverified | Docker build smoke plus startup `/ready` render, independent `/health`. |
| Small and multipage tables | Fixed locally | Case 02: 3 pages to 1 portrait. Case 08: 5 pages to 2 portrait with repeated headers. |
| Wide table collisions and spare pages | Fixed for supplied case | Case 03 is one landscape page instead of three; tested headings do not intersect. |
| Realistic report label collision | Fixed locally | Case 16: 3 pages to 1 portrait without label/value overlap. |
| Long code clipping | Fixed locally | Case 07 end-of-line marker is visible and extractable. |
| Dollar and single-backslash math delimiters | Fixed locally | Cases 04 and 05 render equations; currency in case 14 remains literal. |
| Scientific superscript minus | Fixed locally | Case 06 shows the negative exponent in `10⁻³`. |
| Unsupported glyphs | Detected and warned | Case 06 lists specific Unicode code points; CJK, Arabic, Hindi and emoji still need full font support. |
| Missing image, unresolved citation, Mermaid | Detected and warned; unsupported input remains | Cases 10–12 surface actionable notices. |
| Title/author/date metadata | Fixed locally | Case 13 displays all three fields. |
| Malformed equation | Fixed error reporting | Case 15 returns an input error with reference; no PDF is presented. |
| Preview, retry, filename, stale output | Implemented locally; browser behavior on live deployment unverified | UI preview and warning display; source change aborts requests and clears old PDF. |
| Basic, lists, long prose, repeated output | Preserved | 17/18 cases compile; no missing sentinels; case 01/18 text and page pixels match. |

Selected comparisons:

- Small table: [before](02_small_table-before.pdf) · [after](02_small_table-after.pdf)
- Wide table: [before](03_wide_table-before.pdf) · [after](03_wide_table-after.pdf)
- Long code: [before](07_long_code-before.pdf) · [after](07_long_code-after.pdf)
- Realistic report: [before](16_realistic_report-before.pdf) · [after](16_realistic_report-after.pdf)

`findings.json` records before/after page counts, and
`current-all-results.json` records every supplied case. PNG page images are
included for review. The sample documents contain synthetic test data.
