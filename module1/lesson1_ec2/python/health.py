#!/usr/bin/env python3
"""
=========================================================
                BALERICA AI
           EC2 Health Analyzer v1.0
=========================================================

SEIR Foundations

Purpose:
Collect basic Linux telemetry and send it to Amazon Bedrock
for a health assessment.

=========================================================
"""

import boto3
import json
import subprocess
import platform
from datetime import datetime

# ---------------------------------------------------------
# Student Challenge
#
# Replace 4.X with the version you enabled in Amazon Bedrock.
#
# Hint:
# AWS Console
# -> Amazon Bedrock
# -> Model Access
#
# Chewbacca says:
#
# "Rrrrrrrghhh!"
#
# Translation:
# Engineers always verify their dependencies.
# ---------------------------------------------------------

MODEL_ID = "anthropic.claude-sonnet-4.X"

REGION = "us-east-1"

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION
)


# ---------------------------------------------------------
# Agent contract
#
# ask.py's discover_agents() only registers a module as an
# agent if AGENT is True. Without this, health.py is a
# working standalone script that ask.py and app.py can
# never find or route to.
# ---------------------------------------------------------

AGENT = True
NAME = "EC2 Health Analyzer"
DESCRIPTION = "Collect Linux telemetry and generate a Bedrock health assessment."
VERSION = "1.0"


# ---------------------------------------------------------
# Chewbacca says:
#
# "RRRRAAAAAAAGH!"
#
# Translation:
# Never trust assumptions.
# Gather evidence first.
# ---------------------------------------------------------

def run_command(command):

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        return result.stdout.strip()

    except Exception as ex:

        return str(ex)


# ---------------------------------------------------------
# Collect telemetry
# ---------------------------------------------------------

def collect_telemetry():

    telemetry = {

        "Hostname": run_command("hostname"),

        "Current User": run_command("whoami"),

        "Operating System": platform.platform(),

        "Kernel": run_command("uname -r"),

        "Current Time": str(datetime.now()),

        "Uptime": run_command("uptime"),

        "CPU": run_command("top -bn1 | head -5"),

        "Memory": run_command("free -h"),

        "Disk": run_command("df -h"),

        "Failed Services":
            run_command("systemctl --failed --no-pager")

    }

    return telemetry


# ---------------------------------------------------------
# Create Prompt
# ---------------------------------------------------------

def build_prompt(telemetry):

    return f"""
You are a Senior Linux Systems Engineer.

Analyze the telemetry below.

Provide:

1. Overall Health Score (0-100)

2. Executive Summary

3. Problems Found

4. Recommendations

5. Risk Level

Only use the information provided.

Do not invent facts.

Telemetry:

{json.dumps(telemetry, indent=2)}

"""


# ---------------------------------------------------------
# Ask Bedrock
# ---------------------------------------------------------

def ask_bedrock(prompt):

    body = {

        "anthropic_version": "bedrock-2023-05-31",

        "max_tokens": 1000,

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ]

    }

    response = bedrock.invoke_model(

        modelId=MODEL_ID,

        body=json.dumps(body)

    )

    response_body = json.loads(

        response["body"].read()

    )

    return response_body["content"][0]["text"]


# ---------------------------------------------------------
# Main Program
# ---------------------------------------------------------

def main():

    print("\n")

    print("=" * 60)
    print("             BALERICA AI")
    print("        EC2 Health Analyzer")
    print("=" * 60)

    print("\nCollecting telemetry...\n")

    telemetry = collect_telemetry()

    for item in telemetry:

        print(f"[✓] {item}")

    print("\nConnecting to Amazon Bedrock...")

    prompt = build_prompt(telemetry)

    print("Generating Health Report...\n")

    try:

        response = ask_bedrock(prompt)

        print("=" * 60)

        print(response)

        print("=" * 60)

        print("\nAnalysis Complete.\n")

        print(
            "Remember:\n"
            "AI provides recommendations.\n"
            "Engineers verify evidence."
        )

    except Exception as ex:

        print("\nUnable to invoke Amazon Bedrock.\n")

        print("Things to check:")

        print("  ✓ IAM Role")

        print("  ✓ Bedrock Model Access")

        print("  ✓ AWS Region")

        print("  ✓ Model Identifier")

        print("\nTechnical Details:\n")

        print(ex)


def run(question=None):
    """Agent entry point used by ask.py."""

    return main()


if __name__ == "__main__":

    main()
