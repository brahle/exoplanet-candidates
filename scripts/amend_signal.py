"""Apply one locally staged assessment amendment; never push or publish."""
import argparse
import json
from pathlib import Path

from export_batch import amend

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--batch', required=True)
    parser.add_argument('--signal-id', required=True)
    args = parser.parse_args()
    print(json.dumps(amend(args.root, args.batch, args.signal_id)))
