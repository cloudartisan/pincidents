#!/usr/bin/env python

import argparse, os, sys
from pathlib import Path

import pygerduty.v2
from pincidents import load_env


def main():
    load_env()
    parser = argparse.ArgumentParser(description='Lists all the teams to which you belong')
    # Default to either PAGERDUTY_API_TOKEN or PAGERDUTY_TOKEN
    parser.add_argument('--token', metavar='TOKEN', type=str, dest="api_token",
            default=os.environ.get('PAGERDUTY_API_TOKEN', os.environ.get('PAGERDUTY_TOKEN')),
            help='PagerDuty API (v2) token')
    args = parser.parse_args()
    api_token = args.api_token

    try:
        pager = pygerduty.v2.PagerDuty(api_token)
        for team in pager.users.show("me").teams:
            print(f"{team.id} {team.summary}")
    except Exception as e:
        print(e)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
