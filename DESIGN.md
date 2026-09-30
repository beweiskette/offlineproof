# Design

Check browser contracts through offline mode, reload and reconnection.

Chromium starts with its sandbox enabled. The selected `localhost` origin tries the pinned loopback addresses 127.0.0.1 and ::1. An unavailable initial page is a setup error (exit 2); a failed DOM contract is a finding (exit 1).

Assertion selectors must be standard CSS in the main document. All predicates are evaluated together in one JavaScript turn, sampled every 25 ms. They must pass together throughout the sampled `stability_ms` window (default 250 ms). A failed sample resets that window. The total deadline is the largest assertion `timeout_ms` (default 1000 ms, maximum 5000 ms) plus `stability_ms`. Changes between samples can be missed. Count checks all matching nodes; other predicates require one node, except that hidden also accepts no match. Text comparison collapses whitespace. Shadow-root and Playwright-specific assertion selectors are outside this version. Action selectors retain Playwright syntax.

## Scope

A fresh context is created for every run and retained through the four phases. Failed phases stop the run; later phases are marked unreached. No cookies, storage, response bodies or page console messages are written to reports. Scenario values and selectors stay in the local input file.

Only the selected loopback origin is permitted by default. `--allow-remote` permits one public origin. A local proxy restricts service-worker traffic as well as page requests; the resolved address is pinned for that run. External origins and WebSockets are blocked. This is application-level traffic control, not an operating-system sandbox.

Offline mode uses Playwright's browser network emulation. Service-worker caches and browser storage continue to work. The tool verifies explicit DOM contracts and a finite observation window; it does not prove backend delivery, conflict resolution or future behaviour. Choose assertions and stability timeouts that reflect your app's completion signals. Existing login sessions, imported storage and cross-origin apps are outside this version.
