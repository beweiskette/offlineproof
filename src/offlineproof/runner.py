from .browser import session, actions, assertions
from .scenario import validate, PHASES

def run(spec, executable=None, allow_remote=False):
    validate(spec)
    results = [{'phase': phase, 'status': 'unreached'} for phase in PHASES]
    with session(spec['url'], executable, allow_remote, workers='allow') as (page, context, proxy):
        for entry in results:
            name = entry['phase']
            try:
                if name == 'online':
                    response = page.goto(spec['url'], wait_until='domcontentloaded')
                    if response is not None and response.status >= 400:
                        raise ValueError(f'Initial page returned HTTP {response.status}; check the server and URL')
                elif name == 'offline': context.set_offline(True)
                elif name == 'offline_reload': page.reload(wait_until='domcontentloaded')
                elif name == 'reconnect': context.set_offline(False)
                actions(page, spec['phases'][name].get('actions', []))
                entry['failures'] = assertions(page, spec['phases'][name]['assertions'], spec.get('stability_ms', 250))
                entry['status'] = 'fail' if entry['failures'] else 'pass'
            except Exception as exc:
                entry['status'] = 'error'
                entry['error'] = str(exc).splitlines()[0]
            if entry['status'] != 'pass': break
    return {'schema': 1, 'status': 'pass' if all(p['status'] == 'pass' for p in results) else 'error' if any(p['status'] == 'error' for p in results) else 'fail',
            'phases': results, 'scope': 'Browser network emulation and explicit DOM contracts. Backend delivery is not inferred.'}
