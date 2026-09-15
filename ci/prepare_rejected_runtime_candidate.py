import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

source = Path(args.source).read_text()
if source.count('computes "int.add:1"') != 1:
    raise SystemExit("overflow candidate mutation did not find exactly one bounded operation")
candidate = source.replace('computes "int.add:1"', 'computes "int.add:9223372036854775807"', 1)
output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(candidate)
print("prepared bounded rejected candidate: int.add:1 -> int.add:9223372036854775807")
