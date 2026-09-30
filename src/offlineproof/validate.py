def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Integer outside accepted range')

def selector(item):
    if not isinstance(item.get('selector'), str) or not 1 <= len(item['selector']) <= 500:
        raise ValueError('A bounded selector is required')

def assertions(items):
    if not isinstance(items, list) or not 1 <= len(items) <= 30:
        raise ValueError('Specify 1 to 30 explicit assertions')
    for item in items:
        selector(item)
        if item.get('kind') not in ('hidden', 'visible', 'focused', 'count', 'text'):
            raise ValueError('Unknown assertion')
        integer(item.get('timeout_ms', 1000), 1, 5000)
        if item['kind'] == 'count': integer(item.get('value'), 0, 10000)
        if item['kind'] == 'text' and not isinstance(item.get('value'), str):
            raise ValueError('Expected text must be a string')

def actions(items):
    if not isinstance(items, list) or len(items) > 30:
        raise ValueError('At most 30 actions are supported per phase')
    for item in items:
        if item.get('kind') not in ('click', 'fill', 'wait'):
            raise ValueError('Unknown action')
        if item['kind'] == 'wait': integer(item.get('ms'), 0, 10000)
        else: selector(item)
        if item['kind'] == 'fill' and (not isinstance(item.get('value'), str) or len(item['value']) > 10000):
            raise ValueError('Fill value must be a bounded string')
