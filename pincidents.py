#!/usr/bin/env python

import argparse, csv, os, sys
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse as dateparse

import pygerduty.v2
from dotenv import load_dotenv


ALL_URGENCIES=["low", "high"]


# --since
# The start of the date range over which you want to search. Maximum range is 6
# months and default is 1 month.
#
# --until
# The end of the date range over which you want to search. Maximum range is 6
# months and default is 1 month


def load_env(env_path=""):
    # Load the global environment file. but do not override environment
    # variables if they are already set
    if not env_path:
        env_path = Path.home() / '.pincidents'
    load_dotenv(dotenv_path=env_path)


# get_incident_duration: returns the duration for an incident; if the incident
# is not resolved the duration is from start until now
def get_incident_duration(incident)
    started = dateparse(incident.created_at)
    if incident.status == 'resolved':
        last_update = dateparse(incident.last_status_change_at)
    else:
        last_update = datetime.now()
    return last_update - started


def output_incident(incident, csv=False):
    if csv:
        writer = csv.writer(sys.stdout)

    print(incident.id, incident.urgency, incident.created_at,
            incident.last_status_change_at, incident.title, incident.status, duration,
            incident.html_url)
    # Join all notes with a newline
    notes = "".join(f"{note.content}\n" for note in incident.notes.list())
    print(notes)


def get_args()
    parser = argparse.ArgumentParser(description='Determine if a user is on call')
    parser.add_argument('--team', metavar='ID', type=str, dest="team_id",
            help='PagerDuty team ID')
    parser.add_argument('--outfile'. type=str, default='',
            help='Write output to the given file (instead of stdout)')
    parser.add_argument('--csv', type=bool, default=False,
            help='Output as CSV for importing into managementy spreadsheets')
    parser.add_argument('--urgency', type=str, choices=["low", "high"],
            help='Show only incidents of a particular urgency')
    # Default to either PAGERDUTY_API_TOKEN or PAGERDUTY_TOKEN
    parser.add_argument('--token', metavar='TOKEN', type=str, dest="api_token",
            default=os.environ.get('PAGERDUTY_API_TOKEN', os.environ.get('PAGERDUTY_TOKEN')),
            help='PagerDuty API (v2) token')
    return parser.parse_args()


def main():
    load_env()
    args = get_args()
    urgencies = [args.urgency] if args.urgency else ALL_URGENCIES
    outfile = open(sys.stdout if not args.outfile else args.outfile, 'w')

    incidents = []
    try:
        pager = pygerduty.v2.PagerDuty(args.api_token)
        for incident in pager.incidents.list(
                team_ids=[args.team_id],
                urgencies=urgencies):
            duration = get_incident_duration(incident)
            # Join all notes with a newline
            notes = "".join(f"{note.content}\n" for note in incident.notes.list())
            incidents += [
                    incident.id,
                    incident.urgency,
                    incident.created_at,
                    incident.last_status_change_at,
                    incident.title,
                    incident.status,
                    duration,
                    incident.html_url,
                    notes
            ]
        write_incidents(incidents, outfile=outfile, csv=args.csv)
        outfile.close()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
