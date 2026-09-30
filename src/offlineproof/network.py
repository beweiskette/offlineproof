"""Per-run HTTP proxy that permits a single pinned origin, including worker traffic.

This is application-level traffic control, not an operating-system sandbox.
"""
import http.client
import http.server
import ipaddress
import select
import socket
import threading
import time
from urllib.parse import urlsplit

class OriginProxy:
    def __init__(self, url, allow_remote=False):
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.query:
            raise ValueError('Use an HTTP(S) URL without credentials, query or fragment')
        self.scheme, self.host = parsed.scheme, parsed.hostname.lower()
        self.port = parsed.port or (443 if self.scheme == 'https' else 80)
        local = self.host in ('localhost', '127.0.0.1', '::1')
        if not local and not allow_remote:
            raise ValueError('Remote origins require --allow-remote')
        if local:
            self.ip = '::1' if self.host == '::1' else '127.0.0.1'
        else:
            addresses = [a[4][0] for a in socket.getaddrinfo(self.host, self.port, type=socket.SOCK_STREAM)]
            if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
                raise ValueError('Remote origins must resolve exclusively to public IP addresses')
            self.ip = addresses[0]
        self.blocked = 0
        self.server = None

    def matches(self, url):
        try:
            p = urlsplit(url)
            return (p.scheme, p.hostname, p.port or (443 if p.scheme == 'https' else 80)) == (self.scheme, self.host, self.port) and not p.username and not p.password
        except ValueError:
            return False

    def __enter__(self):
        owner = self
        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.0'
            def log_message(self, *args):
                pass
            def denied(self):
                owner.blocked += 1
                self.send_error(403, 'Origin blocked')
            def do_CONNECT(self):
                try:
                    target = urlsplit('https://' + self.path)
                    allowed = owner.scheme == 'https' and target.hostname == owner.host and (target.port or 443) == owner.port and not target.username and not target.password and not target.path
                except ValueError:
                    allowed = False
                if not allowed:
                    return self.denied()
                try:
                    with socket.create_connection((owner.ip, owner.port), timeout=10) as upstream:
                        self.send_response(200, 'Connection Established'); self.end_headers()
                        streams = [self.connection, upstream]
                        deadline = time.monotonic() + 120
                        while time.monotonic() < deadline:
                            ready, _, _ = select.select(streams, [], [], 1)
                            for stream in ready:
                                data = stream.recv(65536)
                                if not data:
                                    return
                                (upstream if stream is self.connection else self.connection).sendall(data)
                except OSError:
                    return
            def forward(self):
                if not owner.matches(self.path):
                    return self.denied()
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if length < 0 or length > 2 * 1024 * 1024 or self.headers.get('Transfer-Encoding'):
                        return self.send_error(413)
                    p = urlsplit(self.path)
                    headers = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'connection', 'proxy-connection', 'proxy-authorization', 'transfer-encoding', 'upgrade')}
                    headers['Host'] = p.netloc
                    connection = http.client.HTTPConnection(owner.ip, owner.port, timeout=15)
                    try:
                        connection.request(self.command, p.path or '/' if not p.query else (p.path or '/') + '?' + p.query,
                                           self.rfile.read(length) if length else None, headers)
                        response = connection.getresponse()
                        data = response.read(16 * 1024 * 1024 + 1)
                        if len(data) > 16 * 1024 * 1024:
                            return self.send_error(502)
                        self.send_response(response.status)
                        for k, v in response.getheaders():
                            if k.lower() not in ('connection', 'transfer-encoding', 'content-length'):
                                self.send_header(k, v)
                        self.send_header('Content-Length', str(len(data)))
                        self.end_headers()
                        if self.command != 'HEAD':
                            self.wfile.write(data)
                    finally:
                        connection.close()
                except (OSError, ValueError, http.client.HTTPException):
                    try: self.send_error(502)
                    except OSError: pass
            do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = forward
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.address = f'http://127.0.0.1:{self.server.server_port}'
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
