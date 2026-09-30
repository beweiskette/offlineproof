import os
from pathlib import Path
from functools import partial
import http.server
import threading
import pytest
from offlineproof.scenario import validate
from offlineproof.runner import run

def test_all_phases_and_assertions_required():
    with pytest.raises(ValueError): validate({'url': 'http://localhost', 'phases': {}})

@pytest.mark.integration
def test_real_offline_reload_and_duplicate_detection():
    executable = os.environ.get('TEST_BROWSER')
    if not executable and not os.environ.get('BROWSER_TEST'):
        pytest.skip('Set TEST_BROWSER or BROWSER_TEST=1')
    import json
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(Path(__file__).parents[1] / 'examples')))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        spec = json.loads((Path(__file__).parents[1] / 'examples' / 'scenario.json').read_text())
        spec['url'] = f'http://127.0.0.1:{server.server_port}/fixed.html'
        good = run(spec, executable)
        assert good['status'] == 'pass', good
        spec['url'] = spec['url'].replace('fixed.html', 'broken.html')
        bad = run(spec, executable)
        assert bad['status'] == 'fail', bad
        assert [p['status'] for p in bad['phases']] == ['pass', 'pass', 'pass', 'fail'], bad
        # A new invocation must not inherit the previous localStorage or worker.
        spec['url'] = spec['url'].replace('broken.html', 'fixed.html')
        assert run(spec, executable)['status'] == 'pass'
    finally:
        server.shutdown(); server.server_close(); thread.join()
