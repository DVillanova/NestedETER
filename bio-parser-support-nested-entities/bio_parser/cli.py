import argparse
import errno

from bio_parser.parse import add_validate_parser


def main():
    parser = argparse.ArgumentParser(
        prog="bio-parser",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    commands = parser.add_subparsers()
    add_validate_parser(commands)

    args = vars(parser.parse_args())
    if "func" in args:
        # Run the subcommand's function
        try:
            status = args.pop("func")(**args)
            parser.exit(status=status)
        except KeyboardInterrupt:
            # Just quit silently on ^C instead of displaying a long traceback
            parser.exit(status=errno.EOWNERDEAD)
    else:
        parser.print_help()
