#!/usr/bin/env python
#
# Fetches incidents from PagerDuty and extracts the "most important" fields in
# CSV formatted output.


import argparse, csv, os, sys
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse as dateparse

import pygerduty.v2
from dotenv import load_dotenv


ALL_URGENCIES=["low", "high"]


def load_env(env_path=""):
    # Load the global environment file. but do not override environment
    # variables if they are already set
    if not env_path:
        env_path = Path.home() / '.pincidents'
    load_dotenv(dotenv_path=env_path)


# get_incident_duration: returns the duration for an incident; if the incident
# is not resolved the duration is from start until now
def get_incident_duration(incident):
    started = dateparse(incident.created_at)
    if incident.status == 'resolved':
        last_update = dateparse(incident.last_status_change_at)
    else:
        last_update = datetime.now()
    # Convert duration to a nice string representation
    return str(last_update - started)


# get_args:
#
# --since <date>
# The start of the date range over which you want to search. Maximum range is 6
# months and default is 1 month.
#
# --until <date>
# The end of the date range over which you want to search. Maximum range is 6
# months and default is 1 month
def get_args():
    parser = argparse.ArgumentParser(description='Extract CSV incident history')
    parser.add_argument('--outfile', type=str, default='',
            help='Write output to the given file (instead of stdout)')
    parser.add_argument('--since', metavar='DATE', type=str, default='',
            help='Start of date range (default 1 month, max 6 months) over which you want to search')
    parser.add_argument('--status', metavar='STATUS', type=str, dest='statuses',
            action='append', nargs='*', default=[],
            help='Optionally specify the subset of statuses')
    parser.add_argument('--team', metavar='ID', type=str, dest='team_ids',
            action='append', nargs='*', default=[],
            help='PagerDuty team ID')
    parser.add_argument('--timezone', '--tz', type=str, default='UTC',
            help='Timezone to use for the result fields')
    # Default to either PAGERDUTY_API_TOKEN or PAGERDUTY_TOKEN
    parser.add_argument('--token', metavar='TOKEN', type=str, dest="api_token",
            default=os.environ.get('PAGERDUTY_API_TOKEN', os.environ.get('PAGERDUTY_TOKEN')),
            help='PagerDuty API (v2) token')
    parser.add_argument('--until', metavar='DATE', type=str, default='',
            help='End of date range (default 1 month, max 6 months) over which you want to search')
    parser.add_argument('--urgency', type=str, choices=["low", "high"],
            help='Show only incidents of a particular urgency')
    args = parser.parse_args()

    # If an urgency has been chosen, convert it to a list expected by the API,
    # otherwise default to all urgencies
    args.urgencies = [args.urgency] if args.urgency else ALL_URGENCIES

    # Statuses can be a list of lists, so we flatten them to a single list
    args.statuses = [status for statuses in args.statuses for status in statuses]

    # Team IDs can be a list of lists, so we flatten them to a single list
    args.team_ids = [team for teams in args.team_ids for team in teams]

    # Since and until must be a valid ISO8601 datetime or left as empty strings
    if args.since:
        args.since = str(dateparse(args.since))
    if args.until:
        args.until = str(dateparse(args.until))

    return args


def main():
    load_env()
    args = get_args()
    try:
        # If specified, open the output file with newline='', otherwise use sys.stdout
        outfile = open(args.outfile, 'w', newline='') if args.outfile else sys.stdout
        writer = csv.writer(outfile)
        pager = pygerduty.v2.PagerDuty(args.api_token)
        for incident in pager.incidents.list(
                since=args.since,
                statuses=args.statuses,
                team_ids=args.team_ids,
                time_zone=args.timezone,
                until=args.until,
                urgencies=args.urgencies):
            duration = get_incident_duration(incident)
            # Join all notes with a newline
            notes = "".join(f"{note.content}\n" for note in incident.notes.list())
            writer.writerow([
                    incident.id,
                    incident.urgency,
                    incident.created_at,
                    incident.last_status_change_at,
                    incident.title,
                    incident.status,
                    duration,
                    incident.html_url,
                    notes
            ])
        outfile.close()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
