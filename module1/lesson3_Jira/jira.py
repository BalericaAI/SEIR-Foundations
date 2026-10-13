#!/usr/bin/env python3
"""Balerica AI - Jira Cloud incident reporting (SEIR Foundations).

Install: python -m pip install requests python-dotenv
Configure .env with JIRA_SITE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY.
Test: python jira.py --test
"""

import argparse
import json
import logging
import os
import sys
from typing import Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

# ================================================================
# YO STUDENT! INSERT YOUR JIRA SITE URL HERE OR CHEWBACCA BITES YOU!
# Example: https://chewbacca-seir.atlassian.net
# NOT your Slack workspace URL. YES, WE ARE LOOKING AT YOU.
# ================================================================
JIRA_SITE_URL = os.getenv("JIRA_SITE_URL", "https://YOUR-SITE.atlassian.net").rstrip("/")

# Keep secrets in .env. NEVER paste an API token into this file or GitHub.
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "BAI")
JIRA_ISSUE_TYPE = os.getenv("JIRA_ISSUE_TYPE", "Task")
JIRA_ENABLED = os.getenv("JIRA_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
JIRA_TIMEOUT_SECONDS = 15

logger = logging.getLogger(__name__)


class JiraError(RuntimeError):
    """An actionable Jira configuration or API error."""


def _validate_configuration() -> None:
    if not JIRA_ENABLED:
        raise JiraError("Jira reporting is disabled (JIRA_ENABLED=false).")
    parsed = urlparse(JIRA_SITE_URL)
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".atlassian.net") or parsed.path not in {"", "/"}:
        raise JiraError("Set JIRA_SITE_URL to your Jira Cloud site, e.g. https://your-site.atlassian.net")
    if parsed.hostname.startswith("your-site"):
        raise JiraError("YO STUDENT: replace the placeholder JIRA_SITE_URL. Chewbacca is watching.")
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise JiraError("Set JIRA_EMAIL and JIRA_API_TOKEN privately in your .env file.")
    if not JIRA_PROJECT_KEY.strip():
        raise JiraError("Set JIRA_PROJECT_KEY (for example, BAI).")


def _adf(text: str) -> dict:
    """Jira Cloud API v3 expects Atlassian Document Format for description."""
    lines = str(text).splitlines() or [""]
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": ([{"type": "text", "text": line}] if line else [])}
            for line in lines
        ],
    }


def _request(method: str, path: str, *, payload: Optional[dict] = None) -> dict:
    _validate_configuration()
    try:
        response = requests.request(
            method,
            f"{JIRA_SITE_URL}/rest/api/3/{path}",
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=payload,
            timeout=JIRA_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise JiraError(f"Cannot reach Jira: {exc}") from exc

    if not response.ok:
        guidance = {
            400: "Check project key, issue type, required fields, and issue description.",
            401: "Check JIRA_EMAIL and JIRA_API_TOKEN.",
            403: "Account/token lacks permission to create issues in this project.",
            404: "Check JIRA_SITE_URL and JIRA_PROJECT_KEY.",
            429: "Jira rate limit reached; retry later.",
        }.get(response.status_code, "Inspect the Jira project settings and API response.")
        # Jira error bodies can contain private data: do not dump them to logs.
        raise JiraError(f"Jira HTTP {response.status_code}. {guidance}")
    try:
        return response.json()
    except ValueError as exc:
        raise JiraError("Jira returned a non-JSON response.") from exc


def verify_connection() -> dict:
    """Check that the credentials can access the student's project."""
    project = _request("GET", f"project/{JIRA_PROJECT_KEY}")
    return {"project_key": project.get("key"), "project_name": project.get("name")}


def create_incident(
    agent: str,
    severity: str,
    message: str,
    *,
    incident_id: Optional[str] = None,
    evidence: Optional[str] = None,
    recommendation: Optional[str] = None,
) -> dict:
    """Create a Jira issue and return its key and URL.

    This method creates a NEW ticket on each call. Callers should deduplicate
    recurring alerts before invoking it (e.g. by incident_id).
    """
    if not agent.strip() or not message.strip():
        raise ValueError("agent and message are required")
    severity = severity.upper().strip()
    if severity not in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("severity must be INFO, WARNING, ERROR, or CRITICAL")

    summary = f"[Balerica AI][{severity}] {agent}: {message.splitlines()[0]}"[:255]
    description = "\n".join(
        part for part in [
            "Balerica AI - Incident Report",
            f"Source agent: {agent}",
            f"Severity: {severity}",
            f"Incident ID: {incident_id}" if incident_id else None,
            f"Problem: {message}",
            f"Evidence: {evidence}" if evidence else None,
            f"Recommended investigation: {recommendation}" if recommendation else None,
            "Engineer must verify the findings before remediation.",
        ] if part
    )
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": _adf(description),
            "issuetype": {"name": JIRA_ISSUE_TYPE},
        }
    }
    result = _request("POST", "issue", payload=payload)
    key = result.get("key")
    if not key:
        raise JiraError("Jira did not return an issue key.")
    return {"key": key, "url": f"{JIRA_SITE_URL}/browse/{key}", "id": result.get("id")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Balerica AI Jira integration")
    parser.add_argument("--test", action="store_true", help="Verify connection and CREATE a test issue")
    parser.add_argument("--verify", action="store_true", help="Verify project access without creating an issue")
    args = parser.parse_args()
    if not (args.test or args.verify):
        parser.print_help()
        return 0
    try:
        project = verify_connection()
        print(f"Connected to Jira project: {project['project_key']} ({project['project_name']})")
        if args.test:
            result = create_incident(
                agent="jira.py",
                severity="INFO",
                message="SEIR Foundations Jira integration test - no real incident",
                incident_id="SEIR-JIRA-TEST",
                recommendation="Confirm this issue appears in your Jira project.",
            )
            print("Test issue created:", result["url"])
        return 0
    except JiraError as exc:
        print(f"JIRA ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
