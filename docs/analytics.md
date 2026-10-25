# Usage analytics

Analytics is optional and disabled until `POSTHOG_PROJECT_KEY` is set. No new Python dependencies are required. Events use PostHog's capture API: https://posthog.com/docs/api/capture.

## Enable on Render

1. Create a PostHog project. Copy its **project token**, not a personal API key.
2. In the Render service's Environment settings, set `POSTHOG_PROJECT_KEY` to that token.
3. Set `POSTHOG_HOST` to `https://us.i.posthog.com` or `https://eu.i.posthog.com`, matching the project region. US is the default.
4. Deploy this change. Open the website, generate one PDF, click Download, then perform one MCP conversion. Confirm the events in PostHog's activity feed.
5. Create a dashboard with the insights below. Remove the project key to disable delivery.

## Dashboard

| Insight | Event | Measure |
|---|---|---|
| Visitors | `page_view` | Unique distinct IDs, filter channel=web |
| Page views | `page_view` | Total events |
| Successful conversions | `conversion_succeeded` | Total, break down by channel |
| Failed conversions | `conversion_failed` | Total, break down by channel and status_code |
| Download clicks | `download_clicked` | Total, channel=web |

Channels are `web`, `api` and `mcp`. Conversion outcomes are emitted by the server, including invalid API requests. MCP success is emitted only after the download has been prepared; protocol-level invalid tool arguments are rejected before our tool runs and are not counted. Health checks and status calls do not count.

Visitors are anonymous browser profiles, not verified people. A random UUID is stored in localStorage and reused for website conversion events. Clearing storage or using another browser creates another visitor. API requests without a browser ID and all MCP conversions get fresh IDs: use **total events**, not unique users, for those channels. Do not add MCP IDs to the website visitor count.

## Privacy and limitations

No Markdown, filenames, error messages, email addresses, IP addresses or referrers are included. `$ip: null` prevents PostHog from deriving client location; requests originate from the application server. There is no autocapture, fingerprinting or session recording. Local storage contains the random browser ID. The browser respects Do Not Track. To opt out locally, run `localStorage.setItem('typesetllm-analytics', 'off')` and reload. To re-enable, remove that entry and reload. Document the analytics in the site's privacy notice before enabling if appropriate to your audience.

Delivery uses one daemon worker and a bounded 256-event queue with a two-second HTTP timeout. Failures and full queues are logged without event contents. There are no retries or durable event storage: events can be lost on restart, network failure or overload. Treat the dashboard as usage estimates, not billing records. Public event endpoints can receive synthetic/bot traffic; visitor IDs are not authentication. Download clicks do not prove a file was saved. Browser cancellation can differ from server completion. No historical usage is recovered.

The integrations landing page is not counted; the converter page is. Do not enable PostHog's automatic site tracking in addition to this instrumentation unless you intend to change these privacy and counting semantics.
