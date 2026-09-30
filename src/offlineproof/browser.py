import time
from contextlib import contextmanager
from playwright.sync_api import sync_playwright
from .network import OriginProxy

@contextmanager
def session(url, executable=None, allow_remote=False, workers='block'):
    with OriginProxy(url, allow_remote) as proxy, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, chromium_sandbox=True, executable_path=executable,
            proxy={'server': proxy.address}, args=['--proxy-bypass-list=<-loopback>', '--disable-quic',
                '--force-webrtc-ip-handling-policy=disable_non_proxied_udp', '--disable-background-networking'])
        context = browser.new_context(service_workers=workers, accept_downloads=False,
                                      viewport={'width': 1000, 'height': 750})
        context.route_web_socket('**/*', lambda ws: ws.close())
        try:
            page = context.new_page()
            page.set_default_timeout(3000)
            page.set_default_navigation_timeout(10000)
            yield page, context, proxy
        finally:
            context.close()
            browser.close()

def actions(page, items):
    for item in items:
        kind = item['kind']
        if kind == 'click': page.locator(item['selector']).click()
        elif kind == 'fill': page.locator(item['selector']).fill(item['value'])
        elif kind == 'wait': page.wait_for_timeout(item['ms'])

# All CSS predicates run in one JavaScript turn, so an alternating DOM cannot
# satisfy contradictory expectations in successive Playwright waits.
_CHECK = r"""items => items.map(item => {
    let nodes;
    try { nodes = [...document.querySelectorAll(item.selector)]; }
    catch { return {invalid: true}; }
    const el = nodes[0];
    const visible = el && getComputedStyle(el).visibility !== 'hidden' &&
        getComputedStyle(el).visibility !== 'collapse' &&
        el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0;
    const norm = text => text.replace(/\s+/g, ' ').trim();
    if (item.kind === 'count') return nodes.length === item.value;
    if (item.kind === 'hidden') return !nodes.length || (nodes.length === 1 && !visible);
    if (nodes.length !== 1) return false;
    if (item.kind === 'visible') return !!visible;
    if (item.kind === 'focused') return document.activeElement === el;
    if (item.kind === 'text') return norm(el.textContent || '') === norm(item.value);
    return false;
})"""

def assertions(page, items, stability_ms=0):
    start = time.monotonic()
    deadline = start + max(item.get('timeout_ms', 1000) for item in items) / 1000 + stability_ms / 1000
    stable_since = None
    while True:
        states = page.evaluate(_CHECK, items)
        if any(isinstance(state, dict) for state in states):
            raise ValueError('Assertion selectors must be valid CSS selectors')
        failures = [{'assertion': i, 'kind': item['kind']} for i, (item, ok) in enumerate(zip(items, states)) if not ok]
        now = time.monotonic()
        if not failures:
            if stable_since is None: stable_since = now
            if now - stable_since >= stability_ms / 1000: return []
        else:
            stable_since = None
        if now >= deadline:
            return failures or [{'assertion': i, 'kind': item['kind'], 'reason': 'unstable'} for i, item in enumerate(items)]
        page.wait_for_timeout(25)
