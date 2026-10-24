#!/usr/bin/env python3
"""
=========================================================
                    BALERICA AI
                AI Operations Console v1.0
=========================================================

SEIR Foundations

Purpose

Main entry point for Balerica AI.

Responsibilities

• Display banner
• Discover installed agents
• Audit user requests
• Route questions
• Display learning suggestions

=========================================================
"""

import contextlib
import importlib
import io
import os

from banner import show_banner, show_footer
from auditor import audit_request

# ---------------------------------------------------------
# Internal Libraries
# ---------------------------------------------------------

LIBRARIES = {

    "ask",
    "banner",
    "auditor",
    "bedrock",
    "telemetry",
    "suggestion",
    "config",
    "utils"

}


# ---------------------------------------------------------
# Chewbacca says:
#
# "Rrrrrrrgh..."
#
# Translation:
#
# Great systems discover capabilities.
#
# They don't require someone to hardcode
# every new feature.
# ---------------------------------------------------------

def discover_agents():

    agents = []

    for filename in os.listdir("."):

        if not filename.endswith(".py"):
            continue

        module_name = filename[:-3]

        if module_name.startswith("_"):
            continue

        if module_name in LIBRARIES:
            continue

        try:

            module = importlib.import_module(module_name)

            if getattr(module, "AGENT", False):

                agents.append(module)

        except Exception:

            continue

    return sorted(
        agents,
        key=lambda x: x.NAME
    )


# ---------------------------------------------------------

def show_agents(agents):

    print()

    print("=" * 60)

    print("Installed Agents")

    print("=" * 60)

    print()

    for index, agent in enumerate(agents, start=1):

        print(f"{index}. {agent.NAME}")

        print(f"   {agent.DESCRIPTION}")

        print()

    print("=" * 60)

    print()


# ---------------------------------------------------------

def select_agent(agents):

    while True:

        choice = input(
            "Agent Number (or ENTER for Auto): "
        ).strip()

        if choice == "":

            return None

        try:

            number = int(choice)

            if 1 <= number <= len(agents):

                return agents[number - 1]

        except ValueError:

            pass

        print("Invalid selection.\n")


# ---------------------------------------------------------
# Placeholder Router
#
# Later this becomes LangGraph,
# Semantic Routing,
# MCP,
# or another orchestration engine.
# ---------------------------------------------------------

def route_question(question, agents):

    lowered = question.lower()

    if "log" in lowered:

        for agent in agents:

            if "log" in agent.NAME.lower():

                return agent

    if "health" in lowered:

        for agent in agents:

            if "health" in agent.NAME.lower():

                return agent

    return None


# ---------------------------------------------------------
# API entry points
#
# app.py calls these instead of the interactive console.
#
# run() reuses the same audit and router as main().
# run_agent() executes one discovered agent by name.
# ---------------------------------------------------------

def _execute_agent(agent, question):

    buffer = io.StringIO()

    with contextlib.redirect_stdout(buffer):

        returned = agent.run(question)

    if returned is not None:

        return returned

    return buffer.getvalue().strip()


def _match_agent(agent_name, agents):

    needle = agent_name.strip().lower()

    for agent in agents:

        display = getattr(agent, "NAME", "")

        names = {
            getattr(agent, "__name__", "").lower(),
            display.lower(),
            display.lower().replace(" ", ""),
        }

        if needle in names or (needle and needle in display.lower()):

            return agent

    return None


def run_agent(agent_name):

    agents = discover_agents()

    selected = _match_agent(agent_name, agents)

    if selected is None:

        installed = ", ".join(
            agent.NAME for agent in agents
        ) or "none"

        raise ValueError(
            f"Agent not found: {agent_name}. Installed: {installed}"
        )

    return _execute_agent(selected, None)


def run(question):

    approved, message = audit_request(question)

    if not approved:

        return message

    agents = discover_agents()

    selected = route_question(question, agents)

    if selected is None:

        return (
            "No agent selected automatically. "
            "Choose an installed agent by name."
        )

    return _execute_agent(selected, question)


# ---------------------------------------------------------

def main():

    show_banner(

        agent_name="AI Operations Console",

        version="1.0"

    )

    print("Scanning installed agents...\n")

    agents = discover_agents()

    print(f"[✓] {len(agents)} agent(s) discovered.\n")

    show_agents(agents)

    print("Type 'exit' to quit.\n")

    while True:

        question = input("Question> ").strip()

        if question.lower() == "exit":

            break

        if len(question) == 0:

            continue

        approved, message = audit_request(question)

        if not approved:

            print(message)

            continue

        selected_agent = route_question(

            question,

            agents

        )

        if selected_agent is None:

            print()

            print("No agent selected automatically.")

            print("Please choose one manually.\n")

            selected_agent = select_agent(agents)

        if selected_agent is None:

            print()

            print("Request cancelled.\n")

            continue

        print()

        print(f"Launching {selected_agent.NAME}...\n")

        try:

            selected_agent.run(question)

        except Exception as ex:

            print()

            print("Agent execution failed.\n")

            print(ex)

        print()

    show_footer()


# ---------------------------------------------------------

if __name__ == "__main__":

    main()
