#!/usr/bin/env python

import argparse, os, sys
from pathlib import Path

import pygerduty.v2
from pincidents import load_env


def main(argv):
    load_env()
    parser = argparse.ArgumentParser(description='Determine if a user is on call')
    # Default to either PAGERDUTY_API_TOKEN or PAGERDUTY_TOKEN
    parser.add_argument('--token', metavar='TOKEN', type=str, dest="api_token",
            default=os.environ.get('PAGERDUTY_API_TOKEN', os.environ.get('PAGERDUTY_TOKEN')),
            help='PagerDuty API (v2) token')
    parser.add_argument('user_id', metavar='ID', type=str, nargs='?',
            default="me",
            help='User ID')
    args = parser.parse_args()
    user_id = args.user_id
    api_token = args.api_token

    try:
        pager = pygerduty.v2.PagerDuty(api_token)
        if user_id == "me":
            user_id = pager.users.show("me").id
        oncalls = pager.oncalls.list(user_ids=[user_id])
        num_oncalls = (len(list(oncalls)))
    except Exception as e:
        print(e)
        sys.exit(2)

    # If we are on call (num_oncalls > 0) is True
    # If we are NOT on call (num_oncalls > 0) is False
    is_oncall = (num_oncalls > 0)
    print(f"User {user_id} on call: {is_oncall}")

    # Exit code 0 if we are on call, otherwise exit code 1 if we are
    # NOT on call
    sys.exit(0 if is_oncall else 1)

if __name__ == "__main__":
    main(sys.argv[1:])
