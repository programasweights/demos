"""Arabic morphology: run the public program, or pass --local."""
import argparse
import json

import programasweights as paw

PROGRAM_ID = "4185aac0cf28915ce61e"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default="وبكتابهم")
    parser.add_argument("--program", default=PROGRAM_ID)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    with paw.function(args.program, remote=not args.local) as function:
        output = function(args.text)
    print(json.dumps(json.loads(output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
