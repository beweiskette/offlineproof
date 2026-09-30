import argparse
import json
from .runner import run
from .safeio import read_json, report

def main(argv=None):
    parser = argparse.ArgumentParser(description='Verify explicit contracts through offline, reload and reconnect phases')
    parser.add_argument('command', choices=['run']); parser.add_argument('scenario')
    parser.add_argument('--out', required=True); parser.add_argument('--browser'); parser.add_argument('--allow-remote', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = run(read_json(args.scenario), args.browser, args.allow_remote)
        report(result, args.out)
        print(json.dumps({'status': result['status']}))
        return int(result['status'] != 'pass')
    except Exception as exc:
        parser.exit(2, f'Cannot run scenario ({type(exc).__name__}). Check the scenario, server and installed browser.\n')
