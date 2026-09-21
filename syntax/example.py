"""Label a short code snippet with a neural program."""
import argparse
import json
from pathlib import Path

import programasweights as paw
from codec import decode, encode, highlight

PROGRAM_ID = "8cc17c494a1c1f81a50d"
DEFAULT = 'const message = "hello, world!";\nconsole.log(message);'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default=DEFAULT)
    parser.add_argument("--file", type=Path, help="Read a short source file")
    parser.add_argument("--program", default=PROGRAM_ID)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    code = args.file.read_text(encoding="utf-8") if args.file else args.text
    with paw.function(args.program, remote=not args.local) as function:
        pairs = decode(function(encode(code), max_tokens=1024), code)
    print(highlight(code, pairs))
    print(json.dumps(pairs, ensure_ascii=False))


if __name__ == "__main__":
    main()
