#!/usr/bin/env python

"""
List all the teams to which the API user belongs. The API token can be
specified at the command line, in a ~/.pincidents environment file, or
in environment variables.
"""

import argparse
import os
import sys

import pygerduty.v2
import pygerduty.exceptions
from pincidents import load_env


def parse_args():
    """
    Parse command-line arguments. Defaults for the PagerDuty API can come from
    the environment which can be preloaded via load_env().
    """
    parser = argparse.ArgumentParser(description='Lists all the teams to which you belong')
    # Default to either PAGERDUTY_API_TOKEN or PAGERDUTY_TOKEN
    parser.add_argument('--token', metavar='TOKEN', type=str, dest="api_token",
            default=os.environ.get('PAGERDUTY_API_TOKEN', os.environ.get('PAGERDUTY_TOKEN')),
            help='PagerDuty API (v2) token')
    return parser.parse_args()


def main():
    load_env()
    args = parse_args()
    api_token = args.api_token

    try:
        pager = pygerduty.v2.PagerDuty(api_token)
        for team in pager.users.show("me").teams:
            print(f"{team.id} {team.summary}")
    except pygerduty.exceptions.Error as pygerduty_error:
        print(pygerduty_error)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
