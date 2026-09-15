import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

source = Path(args.source).read_text()
if source.count('computes "int.add:1"') != 1:
    raise SystemExit("runtime candidate mutation did not find exactly one bounded operation")
candidate = source.replace('computes "int.add:1"', 'computes "int.add:2"', 1)
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(candidate)
print("prepared bounded runtime candidate: int.add:1 -> int.add:2")
