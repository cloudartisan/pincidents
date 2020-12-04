#!/usr/bin/env python

"""
Determine if the given user is currently on-call. If a user ID is not supplied,
defaults to checking for user who owns the API token.
"""

import argparse
import os
import sys

import pygerduty.v2
import pygerduty.exceptions
from pincidents import load_env


def parse_args():
    """
    Parse command-line arguments. Defaults for the PagerDuty API token can come
    from the environment which can be preloaded via load_env().
    """
    parser = argparse.ArgumentParser(description='Determine if a user is on call')
    # Default to either PAGERDUTY_API_TOKEN or PAGERDUTY_TOKEN
    parser.add_argument('--token', metavar='TOKEN', type=str, dest="api_token",
            default=os.environ.get('PAGERDUTY_API_TOKEN', os.environ.get('PAGERDUTY_TOKEN')),
            help='PagerDuty API (v2) token')
    parser.add_argument('user_id', metavar='ID', type=str, nargs='?',
            default="me",
            help='User ID')
    return parser.parse_args()


def main():
    load_env()
    args = parse_args()
    user_id = args.user_id
    api_token = args.api_token

    try:
        pager = pygerduty.v2.PagerDuty(api_token)
        if user_id == "me":
            user_id = pager.users.show("me").id
        oncalls = pager.oncalls.list(user_ids=[user_id])
        num_oncalls = (len(list(oncalls)))
    except pygerduty.exceptions.Error as pygerduty_error:
        print(pygerduty_error)
        sys.exit(2)

    # If we are on call (num_oncalls > 0) is True
    # If we are NOT on call (num_oncalls > 0) is False
    is_oncall = (num_oncalls > 0)
    print(f"User {user_id} on call: {is_oncall}")

    # Exit code 0 if we are on call, otherwise exit code 1 if we are
    # NOT on call
    sys.exit(0 if is_oncall else 1)

if __name__ == "__main__":
    main()
