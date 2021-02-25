import argparse
from argparse import Namespace


def arguementHandling() -> Namespace:
    """The method responsible for collecting and parsing command line inputs from the user.

    Important:
        Only meant to be used to initalize the Member Collection porition of PoliPy at the current time.

    Note:
        It does not take any arguements.

    Returns:
        Namespace: Contains the user's selected Congress Session, and the Congress Chamber that is to be scraped for information.
    """
    parser = argparse.ArgumentParser(
        prog="PolyPi Member Collection Module",
        usage="To download and store information about Members of Congress from a given Congress Session and Chamber.",
        description="This module was written by Nicholas M. Synovic in order to facilitate the collection and storage of data derived from the Congress.gov website.",
        epilog="While this module can be ran on its own, it is best ran as part of the larger PoliPy project.",
    )

    parser.add_argument(
        "-s",
        "--session",
        nargs=1,
        default=100,
        type=int,
        required=True,
        help="The Congress Session to scrape data from.",
    )

    parser.add_argument(
        "-c",
        "--chamber",
        nargs=1,
        default="House",
        type=str,
        required=True,
        help='The Congress Chamber to scrape data from. Can only be "House" or "Senate".',
    )

    return parser.parse_args()
