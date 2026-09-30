from .validate import actions, assertions, integer

PHASES = ('online', 'offline', 'offline_reload', 'reconnect')

def validate(spec):
    if not isinstance(spec, dict) or not isinstance(spec.get('url'), str):
        raise ValueError('A scenario URL is required')
    phases = spec.get('phases')
    integer(spec.get('stability_ms', 250), 0, 10000)
    if not isinstance(phases, dict) or set(phases) != set(PHASES):
        raise ValueError('All four phases are required')
    for name in PHASES:
        actions(phases[name].get('actions', []))
        assertions(phases[name].get('assertions'))
    return spec
