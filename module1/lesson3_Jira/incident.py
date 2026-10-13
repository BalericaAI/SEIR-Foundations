#!/usr/bin/env python3
"""Balerica AI incident coordinator: Jira ticket first, Slack alert second.

Run: python incident.py --dry-run | --test
Uses existing jira.py and slack.py. Never send secrets or customer data.
"""
import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
from jira import create_incident, JiraError  # noqa: E402
from slack import send_alert  # noqa: E402

# YO STUDENT: CONFIGURE JIRA AND SLACK FIRST, OR CHEWBACCA BITES YOU!
# Your .env holds the secrets. Do NOT paste webhooks or API tokens here.
STATE_DB = Path(os.getenv('INCIDENT_STATE_DB', 'data/incident_state.db'))
SEVERITIES = {'INFO', 'WARNING', 'ERROR', 'CRITICAL'}


def _db():
    STATE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(STATE_DB, timeout=15)
    conn.execute('''CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        jira_key TEXT NOT NULL,
        jira_url TEXT NOT NULL,
        slack_sent INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )''')
    conn.commit()
    return conn


def report_incident(*, agent, severity, message, incident_id,
                    evidence='', recommendation=''):
    """Create at most one Jira issue per incident_id in sequential use.

    If Slack fails, a later call with the same ID retries Slack only.
    This is a teaching implementation, not a distributed lock/queue.
    """
    if not all(isinstance(x, str) and x.strip() for x in (agent, message, incident_id)):
        raise ValueError('agent, message, and stable incident_id are required')
    severity = severity.upper().strip()
    if severity not in SEVERITIES:
        raise ValueError('Invalid severity')
    with _db() as conn:
        row = conn.execute('SELECT jira_key, jira_url, slack_sent FROM incidents WHERE incident_id=?',
                           (incident_id,)).fetchone()
        created = False
        if row is None:
            jira_result = create_incident(agent=agent, severity=severity, message=message,
                                          incident_id=incident_id, evidence=evidence,
                                          recommendation=recommendation)
            conn.execute('INSERT INTO incidents VALUES (?, ?, ?, ?, ?)',
                         (incident_id, jira_result['key'], jira_result['url'], 0,
                          datetime.now(timezone.utc).isoformat()))
            conn.commit()
            jira_key, jira_url, slack_sent = jira_result['key'], jira_result['url'], 0
            created = True
        else:
            jira_key, jira_url, slack_sent = row

        slack_status = 'already_sent' if slack_sent else 'pending'
        if not slack_sent:
            # Slack only gets a brief sanitized incident summary and a Jira link.
            # Never include raw logs, secrets, account numbers, or customer records.
            alert = f'{message[:400]}\nJira: {jira_url}\nReview ticket for details.'
            try:
                sent = send_alert(agent=agent, severity=severity, message=alert,
                                  incident_id=incident_id)
                if sent:
                    conn.execute('UPDATE incidents SET slack_sent=1 WHERE incident_id=?',
                                 (incident_id,))
                    conn.commit()
                    slack_status = 'sent'
                else:
                    slack_status = 'filtered_or_disabled'
            except Exception as exc:
                # Avoid logging exception details: upstream HTTP errors may expose URLs.
                slack_status = f'failed_{type(exc).__name__}'
        return {'incident_id': incident_id, 'jira_key': jira_key, 'jira_url': jira_url,
                'jira_created': created, 'slack_status': slack_status}


def main():
    parser = argparse.ArgumentParser(description='Balerica AI: Jira + Slack incident workflow')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', help='Show workflow; no API calls')
    group.add_argument('--test', action='store_true', help='Create a Jira issue and send Slack alert')
    args = parser.parse_args()
    if args.dry_run:
        print('EC2 agent -> incident.py -> Jira ticket -> Slack alert (includes Jira link)')
        print('No API calls made. Run --test when .env is configured.')
        return 0
    # A new ID per explicit test allows students to repeat the test intentionally.
    test_id = 'SEIR-TEST-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    try:
        result = report_incident(agent='incident.py', severity='ERROR',
                                 message='SEIR Foundations integration test: simulated application failure',
                                 incident_id=test_id,
                                 evidence='Synthetic test only; no customer data',
                                 recommendation='Confirm the Jira issue and Slack message.')
        print(json.dumps(result, indent=2))
        return 0 if result['slack_status'] == 'sent' else 1
    except (JiraError, ValueError, OSError, sqlite3.Error) as exc:
        print(f'Incident test failed: {type(exc).__name__}. Check Jira configuration and local state.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
