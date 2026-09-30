# OfflineProof

Run explicit browser assertions through online, offline, offline reload and reconnect phases. Check that locally created data survives and remains unique after reconnection.

Version 0.1.0. [Deutsch](README.de.md). Python 3.11 or newer. MIT licence.

## Install

From a clone of this repository:

```sh
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell instead:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

## Run

```sh
offlineproof run examples/scenario.json --out outputs/check
```

In a separate terminal, run `python -m http.server 8765 --bind 127.0.0.1 --directory examples`. Install Chromium using `python -m playwright install chromium`, or pass `--browser /absolute/path/to/chrome`.

The example creates a synthetic note offline, reloads through a service worker, then checks the note count and queue state after reconnect. `fixed.html` passes. Change the URL to `broken.html` to see the duplicate-entry failure. The demo queue drains locally after an HTTP reachability check; it does not implement a backend sync service.

The scenario requires `phases.online`, `phases.offline`, `phases.offline_reload` and `phases.reconnect`. Each phase has optional `actions` and mandatory `assertions`. Actions are `click` with a selector, `fill` with selector/value, or `wait` with `ms`. Assertions are `visible`, `hidden`, `focused`, `count` or `text`; count and text require `value`. Assertions are repeated after `stability_ms` (default 250) to catch a state that was only briefly correct.

Reports are local JSON and self-contained HTML. Exit status is 0 for a pass, 1 for findings, and 2 for an input or runtime setup error. Commands do not publish reports or contact a model API.

## Boundaries

A fresh context is created for every run and retained through the four phases. Failed phases stop the run; later phases are marked unreached. No cookies, storage, response bodies or page console messages are written to reports. Scenario values and selectors stay in the local input file.

Only the selected loopback origin is permitted by default. `--allow-remote` permits one public origin. A local proxy restricts service-worker traffic as well as page requests; the resolved address is pinned for that run. External origins and WebSockets are blocked. This is application-level traffic control, not an operating-system sandbox.

Offline mode uses Playwright's browser network emulation. Service-worker caches and browser storage continue to work. The tool verifies explicit DOM contracts and a finite observation window; it does not prove backend delivery, conflict resolution or future behaviour. Choose assertions and stability timeouts that reflect your app's completion signals. Existing login sessions, imported storage and cross-origin apps are outside this version.

## Verify

```sh
python -m pytest -q
```

Set `BROWSER_TEST=1` after installing Chromium, or set `TEST_BROWSER` to an existing Chromium executable. The integration test verifies offline reload, duplicate detection after reconnect, and storage separation between runs.

GitHub Actions runs tests on Windows and Linux. Integration jobs use synthetic local fixtures. No deployment or package publication workflow is configured. Dependency installation and browser/image downloads are explicit setup steps that contact their respective package providers.

See [DESIGN.md](DESIGN.md) for the scope decisions and [SECURITY.md](SECURITY.md) for data handling.
