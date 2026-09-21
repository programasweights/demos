"""Predict a flex row's [left, width] boxes in pixels."""
import argparse
import json
from pathlib import Path

import programasweights as paw
from codec import decode, encode

PROGRAM_ID = "3c09d7b6e31063797825"
DEFAULT = {"width": 640, "gap": 16, "justify": "space-between", "items": [
    {"basis": 120, "grow": 1, "shrink": 1},
    {"basis": 160, "grow": 0, "shrink": 1},
    {"basis": 200, "grow": 2, "shrink": 1},
]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="Read layout properties from JSON")
    parser.add_argument("--width", type=int, help="Override container width")
    parser.add_argument("--program", default=PROGRAM_ID)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    layout = json.loads(args.file.read_text()) if args.file else dict(DEFAULT)
    if args.width is not None:
        layout["width"] = args.width
    with paw.function(args.program, remote=not args.local) as function:
        raw = function(encode(layout), max_tokens=128)
    print(json.dumps(decode(raw, layout), indent=2))


if __name__ == "__main__":
    main()
