import argparse

'''
A command line argument parser utility using decorators that is built on Python's standard argparse library.
'''

cli = argparse.ArgumentParser(prog="cli")
subparsers = cli.add_subparsers(dest="subcommand")


def get_subparser_action(parser: argparse.ArgumentParser):
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            return a


def get_parsers(
    parser: argparse.ArgumentParser,
    maxdepth: int = 0,
    depth: int = 0,
):
    if maxdepth and depth >= maxdepth:
        return

    yield parser

    if parser._subparsers is None:
        return

    sp = get_subparser_action(parser)

    if sp is None:
        return

    for k, v in sp.choices.items():
        if isinstance(v, argparse.ArgumentParser):
            for p in get_parsers(v, maxdepth, depth + 1):
                yield p


def matching(parsers, parent):
    for parser in parsers:
        if parser.prog == parent:
            return parser


def argument(*names_or_flags, **kwargs):
    return names_or_flags, kwargs


def subcommand(*arguments, parser=cli, parent="cli", parents=[]):
    def decorator(func):
        parsers = get_parsers(parser)
        argparser = matching(parsers, parent)
        subparser = get_subparser_action(argparser)
        if subparser is None:
            subparsers = argparser.add_subparsers()
        else:
            subparsers = subparser
        subcommand = subparsers.add_parser(
            func.__name__, help=func.__name__, parents=parents
        )
        for args, kwargs in arguments:
            subcommand.add_argument(*args, **kwargs)
        subcommand.set_defaults(func=func)

    return decorator
