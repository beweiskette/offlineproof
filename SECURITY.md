# Data handling

OfflineProof has no telemetry, update checks, cloud account or model API integration. Reports are written only to the chosen local output directory. HTML uses no remote scripts, fonts or images.

A fresh context is created for every run and retained through the four phases. Failed phases stop the run; later phases are marked unreached. No cookies, storage, response bodies or page console messages are written to reports. Scenario values and selectors stay in the local input file.

Only the selected loopback origin is permitted by default. `--allow-remote` permits one public origin. A local proxy restricts service-worker traffic as well as page requests; the resolved address is pinned for that run. External origins and WebSockets are blocked. This is application-level traffic control, not an operating-system sandbox.

Offline mode uses Playwright's browser network emulation. Service-worker caches and browser storage continue to work. The tool verifies explicit DOM contracts and a finite observation window; it does not prove backend delivery, conflict resolution or future behaviour. Choose assertions and stability timeouts that reflect your app's completion signals. Existing login sessions, imported storage and cross-origin apps are outside this version.

Dependencies are installed separately from package providers. GitHub Actions checks out the source and runs the test suite on GitHub-hosted runners. Workflows receive read-only repository permissions and publish no artifacts. Review inputs and reports before sharing them. Keep synthetic examples in this repository; do not commit real credentials, exports or receipts.

If you find a security issue, report it privately to the repository owner without including live credentials or personal data.
