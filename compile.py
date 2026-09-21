"""Compile an example's English spec into a public neural program."""
import argparse
from pathlib import Path

import programasweights as paw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", choices=["time", "syntax", "arabic", "filters", "cron"])
    parser.add_argument("--spec", type=Path, help="Use a different spec file")
    parser.add_argument("--compiler", default="paw-ft-bs48")
    args = parser.parse_args()
    path = args.spec or Path(__file__).parent / args.demo / "spec.txt"
    program = paw.compile(path.read_text(encoding="utf-8").strip(), compiler=args.compiler, public=True)
    if program.status != "ready":
        raise RuntimeError(f"Compilation did not finish: {program.status}; {program.error}")
    print(f"Program ID: {program.id}")
    print(f"python {args.demo}/example.py --program {program.id}")


if __name__ == "__main__":
    main()
