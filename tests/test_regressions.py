import http.client
import http.server
import os
import socket
import threading
from contextlib import contextmanager
from unittest.mock import MagicMock
import pytest
from offlineproof import browser, cli
from offlineproof.network import OriginProxy

def test_chromium_sandbox_enabled(monkeypatch):
    playwright = MagicMock()
    monkeypatch.setattr(browser,'sync_playwright',lambda: playwright)
    with browser.session('http://localhost'): pass
    assert playwright.__enter__.return_value.chromium.launch.call_args.kwargs.get('chromium_sandbox') is True

def test_localhost_reaches_ipv6_only_server():
    class Server(http.server.ThreadingHTTPServer): address_family = socket.AF_INET6
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b'ipv6')
        def log_message(self,*args): pass
    try: server = Server(('::1',0),Handler)
    except OSError: pytest.skip('IPv6 loopback unavailable')
    thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        with OriginProxy(f'http://localhost:{server.server_port}') as proxy:
            connection = http.client.HTTPConnection('127.0.0.1',proxy.server.server_port)
            connection.request('GET',f'http://localhost:{server.server_port}/')
            response = connection.getresponse()
            assert response.status == 200 and response.read() == b'ipv6'
            connection.close()
    finally: server.shutdown(); server.server_close(); thread.join()

def test_cli_setup_error_exit_two(tmp_path,monkeypatch):
    source=tmp_path/'scenario.json'; source.write_text('{}')
    monkeypatch.setattr(cli,'run',lambda *a: {'status':'error','cases':[],'phases':[]})
    assert cli.main(['run',str(source),'--out',str(tmp_path/'out')]) == 2

def test_cli_error_has_reason(tmp_path,capsys):
    source=tmp_path/'scenario.json'; source.write_text('{}')
    with pytest.raises(SystemExit) as error: cli.main(['run',str(source),'--out',str(tmp_path/'out')])
    assert error.value.code == 2
    assert 'scenario URL' in capsys.readouterr().err

@pytest.mark.integration
def test_mutually_exclusive_expectations_never_pass():
    if not os.environ.get('BROWSER_TEST') and not os.environ.get('TEST_BROWSER'): pytest.skip('Browser integration disabled')
    with browser.session('http://localhost',os.environ.get('TEST_BROWSER')) as (page,context,proxy):
        page.set_content('<p id="a">A</p><p id="b" hidden>B</p><script>setInterval(()=>{a.hidden=!a.hidden;b.hidden=!b.hidden},100)</script>')
        items=[{'kind':'visible','selector':'#a','timeout_ms':500},{'kind':'visible','selector':'#b','timeout_ms':500}]
        assert browser.assertions(page,items)

def test_cli_prints_setup_failure_reason(tmp_path,monkeypatch,capsys):
    source=tmp_path/'scenario.json'; source.write_text('{}')
    monkeypatch.setattr(cli,'run',lambda *a: {'status':'error','cases':[{'error':'Initial page returned HTTP 502'}],'phases':[{'error':'Initial page returned HTTP 502'}]})
    assert cli.main(['run',str(source),'--out',str(tmp_path/'out')]) == 2
    assert 'HTTP 502' in capsys.readouterr().err

@pytest.mark.integration
def test_unreachable_initial_page_is_setup_error(tmp_path):
    if not os.environ.get('BROWSER_TEST') and not os.environ.get('TEST_BROWSER'): pytest.skip('Browser integration disabled')
    from offlineproof.runner import run
    reservation=socket.socket(); reservation.bind(('127.0.0.1',0))
    url=f'http://127.0.0.1:{reservation.getsockname()[1]}'
    items=[{'kind':'count','selector':'#missing','value':0}]
    spec={'url':url,'trigger':'body','delays_ms':[0],'interruptions':[],'assertions':items,
          'phases':{phase:{'assertions':items} for phase in ('online','offline','offline_reload','reconnect')}}
    try: assert run(spec,os.environ.get('TEST_BROWSER'))['status']=='error'
    finally: reservation.close()
