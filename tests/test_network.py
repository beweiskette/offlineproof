import http.client
import http.server
import threading
import pytest
from offlineproof.network import OriginProxy

def test_remote_and_credentials_require_explicit_boundary():
    for url in ('https://example.com', 'http://user:pass@localhost', 'file:///secret', 'http://localhost/?token=x'):
        with pytest.raises(ValueError): OriginProxy(url)

def test_proxy_passes_only_selected_origin():
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b'local test')
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    try:
        with OriginProxy(url) as proxy:
            c = http.client.HTTPConnection('127.0.0.1', proxy.server.server_port)
            c.request('GET', url + '/'); response = c.getresponse()
            assert response.status == 200 and response.read() == b'local test'; c.close()
            c = http.client.HTTPConnection('127.0.0.1', proxy.server.server_port)
            c.request('GET', 'http://forbidden.invalid/private'); response = c.getresponse()
            assert response.status == 403; response.read(); c.close()
            c = http.client.HTTPConnection('127.0.0.1', proxy.server.server_port)
            c.request('CONNECT', 'forbidden.invalid:443'); response = c.getresponse()
            assert response.status == 403; response.read(); c.close()
            assert proxy.blocked == 2
    finally:
        server.shutdown(); server.server_close(); thread.join()

@pytest.mark.integration
def test_browser_and_worker_cannot_reach_second_local_origin():
    import os
    import json
    from offlineproof.browser import session
    executable = os.environ.get('TEST_BROWSER')
    if not executable and not os.environ.get('BROWSER_TEST'):
        pytest.skip('Set TEST_BROWSER or BROWSER_TEST=1')
    hits = []
    class Forbidden(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            hits.append(self.path)
            self.send_response(200); self.end_headers(); self.wfile.write(b'SYNTHETIC_PRIVATE')
        def log_message(self, *args): pass
    other = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Forbidden)
    other_thread = threading.Thread(target=other.serve_forever, daemon=True); other_thread.start()
    forbidden = f'http://127.0.0.1:{other.server_port}/private'
    class Fixture(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/sw.js':
                body = ("self.addEventListener('install',()=>self.skipWaiting());"
                        "self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));"
                        "self.addEventListener('message',async event=>{try{await fetch(FORBIDDEN,{mode:'no-cors'});event.source.postMessage('leaked')}catch{event.source.postMessage('blocked')}});").replace('FORBIDDEN', json.dumps(forbidden))
                self.send_response(200); self.send_header('Content-Type', 'application/javascript')
            else:
                body = '<!doctype html><title>Synthetic network boundary fixture</title>'
                self.send_response(200); self.send_header('Content-Type', 'text/html')
            self.end_headers(); self.wfile.write(body.encode())
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        with session(f'http://127.0.0.1:{server.server_port}/', executable, workers='allow') as (page, context, proxy):
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            result = page.evaluate("""async url => { try {await fetch(url,{mode:'no-cors'});return 'leaked'} catch {return 'blocked'} }""", forbidden)
            # no-cors responses can resolve as opaque even for a proxy 403.
            assert hits == []
            page.evaluate("""async () => {await navigator.serviceWorker.register('/sw.js');await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(r=>navigator.serviceWorker.addEventListener('controllerchange',r,{once:true}));} """)
            result = page.evaluate("""() => new Promise(resolve=>{navigator.serviceWorker.addEventListener('message',e=>resolve(e.data),{once:true});navigator.serviceWorker.controller.postMessage('test');})""")
            assert hits == []
            assert proxy.blocked >= 2
    finally:
        server.shutdown(); server.server_close(); thread.join()
        other.shutdown(); other.server_close(); other_thread.join()
