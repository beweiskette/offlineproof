# Version 0.1 design

Run explicit browser assertions through online, offline, offline reload and reconnect phases. Check that locally created data survives and remains unique after reconnection.

The design was reviewed once through a read-only Claude adapter before implementation. That consultation received feature proposals and synthetic examples, not repository contents or credentials. Implementation and local verification were performed separately; the consultation was a design review, not a code audit.

The selected scope favours explicit user contracts and local evidence. Automatic uploads, model-generated pass criteria, background monitoring and publishing are excluded. This version makes no claim that the idea is unique or that it will attract a particular number of GitHub stars.

## Acceptance evidence

Set `BROWSER_TEST=1` after installing Chromium, or set `TEST_BROWSER` to an existing Chromium executable. The integration test verifies offline reload, duplicate detection after reconnect, and storage separation between runs.

## Deliberate limits

A fresh context is created for every run and retained through the four phases. Failed phases stop the run; later phases are marked unreached. No cookies, storage, response bodies or page console messages are written to reports. Scenario values and selectors stay in the local input file.

Only the selected loopback origin is permitted by default. `--allow-remote` permits one public origin. A local proxy restricts service-worker traffic as well as page requests; the resolved address is pinned for that run. External origins and WebSockets are blocked. This is application-level traffic control, not an operating-system sandbox.

Offline mode uses Playwright's browser network emulation. Service-worker caches and browser storage continue to work. The tool verifies explicit DOM contracts and a finite observation window; it does not prove backend delivery, conflict resolution or future behaviour. Choose assertions and stability timeouts that reflect your app's completion signals. Existing login sessions, imported storage and cross-origin apps are outside this version.
