# Data handling

offlineproof writes reports to the selected local directory. It has no telemetry or model API integration. HTML reports contain no remote assets.

A fresh context is created for every run and retained through the four phases. Failed phases stop the run; later phases are marked unreached. No cookies, storage, response bodies or page console messages are written to reports. Scenario values and selectors stay in the local input file.

Only the selected loopback origin is permitted by default. `--allow-remote` permits one public origin. A local proxy restricts service-worker traffic as well as page requests; the resolved address is pinned for that run. External origins and WebSockets are blocked. This is application-level traffic control, not an operating-system sandbox.

Offline mode uses Playwright's browser network emulation. Service-worker caches and browser storage continue to work. The tool verifies explicit DOM contracts and a finite observation window; it does not prove backend delivery, conflict resolution or future behaviour. Choose assertions and stability timeouts that reflect your app's completion signals. Existing login sessions, imported storage and cross-origin apps are outside this version.

Chromium uses its sandbox. Error summaries may contain the selected URL or selector; review reports before sharing.

GitHub Actions uses read-only repository permissions and publishes no artifacts. Dependency installation contacts package providers. Report security issues privately to the repository owner without live credentials.
