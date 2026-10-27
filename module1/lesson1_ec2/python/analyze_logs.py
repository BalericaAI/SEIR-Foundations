#!/usr/bin/env python3
"""
=========================================================
                 BALERICA AI
             Log Analysis Agent v1.0
=========================================================

SEIR Foundations

Purpose:

Collect Linux logs and use Amazon Bedrock to
generate an easy-to-understand operational report.

=========================================================
"""

import json

from telemetry import (
    get_recent_journal,
    get_recent_auth,
    get_recent_kernel,
    get_failed_services
)

from bedrock import invoke_bedrock


# ---------------------------------------------------------
# Agent contract
#
# ask.py's discover_agents() only registers a module as an
# agent if AGENT is True. Without this, analyze_logs.py is a
# working standalone script that ask.py and app.py can
# never find or route to.
# ---------------------------------------------------------

AGENT = True
NAME = "Log Analysis Agent"
DESCRIPTION = "Collect Linux logs and generate a Bedrock operational report."
VERSION = "1.0"


# ---------------------------------------------------------
# Chewbacca says:
#
# "Rrrrrrrraaaagh..."
#
# Translation:
#
# Logs tell stories.
#
# Before fixing anything...
#
# Read the story.
# ---------------------------------------------------------


def build_prompt(logs):

    return f"""
You are a Senior Linux Systems Engineer.

Review the supplied Linux logs.

Your report should contain the following sections.

====================================================

Executive Summary

Critical Errors

Warnings

Authentication Findings

Failed Services

Kernel Findings

Recommendations

Overall Risk

Engineering Lesson

====================================================

Rules

Use ONLY the supplied logs.

Do NOT invent information.

If something cannot be determined,
say so clearly.

Linux Logs

{json.dumps(logs, indent=4)}

"""


# ---------------------------------------------------------
# Main Program
# ---------------------------------------------------------


def main():

    print()

    print("=" * 60)
    print("             BALERICA AI")
    print("          Log Analysis Agent")
    print("=" * 60)

    print()

    print("Collecting Linux logs...\n")

    logs = {}

    print("[✓] System Journal")
    logs["System Journal"] = get_recent_journal()

    print("[✓] Authentication Log")
    logs["Authentication"] = get_recent_auth()

    print("[✓] Kernel Messages")
    logs["Kernel"] = get_recent_kernel()

    print("[✓] Failed Services")
    logs["Failed Services"] = get_failed_services()

    print()

    print("Preparing analysis...")

    prompt = build_prompt(logs)

    print("Connecting to Amazon Bedrock...")

    print("Generating report...\n")

    try:

        response = invoke_bedrock(prompt)

        print("=" * 60)

        print(response)

        print("=" * 60)

        print()

        print("Analysis Complete.\n")

        print("----------------------------------------------")
        print("Remember")
        print("----------------------------------------------")
        print("AI provides recommendations.")
        print("Engineers verify evidence.")
        print("----------------------------------------------")

    except Exception as ex:

        print()

        print("Unable to analyze logs.\n")

        print("Things to check:\n")

        print("✓ IAM Role")

        print("✓ Bedrock Model Access")

        print("✓ AWS Region")

        print("✓ Foundation Model Identifier")

        print()

        print("Technical Details\n")

        print(ex)


# ---------------------------------------------------------
# Program Entry
# ---------------------------------------------------------

def run(question=None):
    """Agent entry point used by ask.py."""

    return main()


if __name__ == "__main__":

    main()
