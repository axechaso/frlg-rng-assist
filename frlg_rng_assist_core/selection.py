"""Normalize the categorized public form, preserving the older --target CLI."""

import argparse

from .encounters import CATEGORIES, UNOWN_CHAMBERS, WILD_LOCATIONS


def target_flag(category):
    return "--target-" + category


def method_flag(category):
    return "--method-" + category


def selection_arguments(parser):
    parser.add_argument("--category", choices=CATEGORIES)
    for category, (_, targets) in CATEGORIES.items():
        parser.add_argument(target_flag(category), choices=targets, default=targets[0], help=argparse.SUPPRESS)
        parser.add_argument(method_flag(category), dest="method", type=int,
                            choices=(1, 2, 4) if category in ("wild", "unown") else (1, 4),
                            default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--location", choices=dict(WILD_LOCATIONS), default="other")
    parser.add_argument("--chamber", choices=UNOWN_CHAMBERS, default="monean")


def normalize_selection(args):
    if args.category:
        args.target = getattr(args, "target_" + args.category.replace("-", "_"))
    if args.target == "unown":
        args.location = "other"
    return args
