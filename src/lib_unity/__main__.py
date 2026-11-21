"""Read-only Unity CLI discovery of running Editor and tools."""
import argparse
import json
from .client import UnityCLI


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "list", "commands"))
    parser.add_argument("--executable", default="unity")
    args = parser.parse_args(argv)
    print(json.dumps(UnityCLI(executable=args.executable).query(args.command),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
