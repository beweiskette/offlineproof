from contextlib import contextmanager
from playwright.sync_api import sync_playwright, expect
from .network import OriginProxy

@contextmanager
def session(url, executable=None, allow_remote=False, workers='block'):
    with OriginProxy(url, allow_remote) as proxy, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable,
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

def assertions(page, items):
    failures = []
    for index, item in enumerate(items):
        loc = page.locator(item['selector'])
        try:
            timeout = item.get('timeout_ms', 1000)
            kind = item['kind']
            if kind == 'hidden': expect(loc).to_be_hidden(timeout=timeout)
            elif kind == 'visible': expect(loc).to_be_visible(timeout=timeout)
            elif kind == 'focused': expect(loc).to_be_focused(timeout=timeout)
            elif kind == 'count': expect(loc).to_have_count(item['value'], timeout=timeout)
            elif kind == 'text': expect(loc).to_have_text(item['value'], timeout=timeout)
        except Exception:
            # Playwright diagnostics may contain page contents. Retain only contract identity.
            failures.append({'assertion': index, 'kind': item['kind']})
    return failures
