from .browser import session, actions, assertions
from .scenario import validate, PHASES

def run(spec, executable=None, allow_remote=False):
    validate(spec)
    results = [{'phase': phase, 'status': 'unreached'} for phase in PHASES]
    with session(spec['url'], executable, allow_remote, workers='allow') as (page, context, proxy):
        for entry in results:
            name = entry['phase']
            try:
                if name == 'online': page.goto(spec['url'], wait_until='domcontentloaded')
                elif name == 'offline': context.set_offline(True)
                elif name == 'offline_reload': page.reload(wait_until='domcontentloaded')
                elif name == 'reconnect': context.set_offline(False)
                actions(page, spec['phases'][name].get('actions', []))
                entry['failures'] = assertions(page, spec['phases'][name]['assertions'])
                if not entry['failures']:
                    page.wait_for_timeout(spec.get('stability_ms', 250))
                    entry['failures'] = assertions(page, spec['phases'][name]['assertions'])
                entry['status'] = 'fail' if entry['failures'] else 'pass'
            except Exception:
                entry['status'] = 'error'
                entry['error'] = 'navigation-or-action-failed'
            if entry['status'] != 'pass': break
    return {'schema': 1, 'status': 'pass' if all(p['status'] == 'pass' for p in results) else 'fail',
            'phases': results, 'scope': 'Browser network emulation and explicit DOM contracts. Backend delivery is not inferred.'}
