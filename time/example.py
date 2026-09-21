"""English to calendar: run the public program, or pass --local."""
import argparse
import json
from datetime import date

import programasweights as paw

PROGRAM_ID = "94cae81a182723b85cdf"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default="Every weekend from 2pm to 4pm")
    parser.add_argument("--program", default=PROGRAM_ID)
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--today", default=date.today().isoformat(), help="Reference date, YYYY-MM-DD")
    args = parser.parse_args()
    with paw.function(args.program, remote=not args.local) as function:
        output = function(json.dumps({"text": args.text, "today": date.fromisoformat(args.today).isoformat()}))
    print(json.dumps(json.loads(output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
