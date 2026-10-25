"""EDUCATIONAL REFERENCE TEMPLATE — OPTIONS, NOT REQUIREMENTS.

START WITH YOUR OWN REQUIREMENTS. Do not select, install, or combine frameworks
merely because they appear in this file. This is a menu of small examples,
NOT a prescribed architecture, deployment plan, production security design,
or an instruction to use all six technologies.

Suggested student workflow:
  1. Write functional requirements and security / operational constraints.
  2. Identify data inputs, outputs, trust boundaries, and approval decisions.
  3. Choose the smallest set of tools that meets those requirements.
  4. Prototype one option at a time and test assumptions.
  5. Compare alternatives; retain, modify, or discard this template.

Run: python sample.py                       # Pydantic-only demo, no network
Optional: python sample.py --demo langgraph  # local state workflow, no LLM
Other demos: --demo crewai | langchain | langfuse | hermes-info

Optional demos may require extra packages, credentials, configured LLMs, or a
running backend. No cloud resources are modified by these examples.
"""

import argparse
import json
import os
from typing import Literal, TypedDict

from pydantic import BaseModel, Field, ValidationError


# -----------------------------------------------------------------------------
# OPTION A: PYDANTIC — Data contracts, not an agent and not a network service.
# Keep a schema only if it helps YOUR application's requirements.
# -----------------------------------------------------------------------------
class SecurityFinding(BaseModel):
    resource_id: str = Field(min_length=1)
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    evidence: list[str] = Field(min_length=1)


SAMPLE_EVIDENCE = {
    "resource_id": "i-0123456789abcdef0",
    "severity": "HIGH",
    "description": "Example: SSH ingress from 0.0.0.0/0",
    "recommendation": "Review exposure and restrict SSH to approved sources",
    "evidence": ["Simulated security-group rule: tcp/22 0.0.0.0/0"],
}


def demo_pydantic() -> None:
    """Validate local, SIMULATED evidence. No AI and no network calls."""
    finding = SecurityFinding.model_validate(SAMPLE_EVIDENCE)
    print(finding.model_dump_json(indent=2))
    try:
        SecurityFinding.model_validate({**SAMPLE_EVIDENCE, "severity": "URGENT"})
    except ValidationError:
        print("Expected failure: 'URGENT' does not match the severity contract.")
    # IMPORTANT: Schema-valid data is not necessarily a factually correct finding.


# -----------------------------------------------------------------------------
# OPTION B: CREWAI — A POSSIBLE agent-execution layer, not mandatory.
# In particular, creating Agent/Task objects is not itself a network connection.
# CrewAI invokes an LLM only when the crew actually executes.
# -----------------------------------------------------------------------------
def demo_crewai() -> None:
    from crewai import Agent, Crew, Process, Task  # Optional dependency

    security_agent = Agent(
        role="Security Analyst",
        goal="Assess supplied, simulated AWS security evidence",
        backstory="Cloud security engineer who distinguishes facts from assumptions",
        llm=os.environ.get("DEMO_MODEL", "openai/gpt-4.1-mini"),
        allow_delegation=False,
        verbose=False,
    )
    security_task = Task(
        description=(
            "Using ONLY this simulated evidence, produce one security finding. "
            "Do not claim to have connected to AWS or scanned any system. "
            f"Evidence: {json.dumps(SAMPLE_EVIDENCE)}"
        ),
        expected_output="One structured, evidence-grounded security finding",
        agent=security_agent,
        output_pydantic=SecurityFinding,  # Local Pydantic schema, NOT a server.
    )
    crew = Crew(agents=[security_agent], tasks=[security_task], process=Process.sequential)
    # This line may send a request to the configured model provider.
    result = crew.kickoff()
    if result.pydantic is None:
        raise ValueError("CrewAI did not produce structured output")
    validated = SecurityFinding.model_validate(result.pydantic.model_dump())
    print(validated.model_dump_json(indent=2))


# -----------------------------------------------------------------------------
# OPTION C: LANGCHAIN — An ALTERNATIVE agent/model/tool integration approach.
# Students should compare this with CrewAI rather than automatically use both.
# The tool below is a LOCAL Python function. Model inference may be remote.
# -----------------------------------------------------------------------------
def demo_langchain() -> None:
    from langchain.agents import create_agent  # Optional dependency

    def read_sample_security_evidence() -> str:
        """Return demo evidence without AWS access."""
        return json.dumps(SAMPLE_EVIDENCE)

    agent = create_agent(
        model=os.environ.get("DEMO_LANGCHAIN_MODEL", "openai:gpt-4.1-mini"),
        tools=[read_sample_security_evidence],
        system_prompt=("You are a security analyst. Use the provided tool; "
                       "do not invent scans or claim to have contacted AWS."),
    )
    # May call an external LLM; LangChain itself runs in the Python application.
    result = agent.invoke({"messages": [{"role": "user", "content":
        "Summarize the example security risk using the evidence tool."}]})
    print(result["messages"][-1].content)


# -----------------------------------------------------------------------------
# OPTION D: LANGGRAPH — An OPTIONAL stateful workflow controller.
# Useful when requirements include branching, retries, approval or checkpoints.
# This example intentionally uses no LLM or CrewAI to make the distinction clear.
# -----------------------------------------------------------------------------
class AssessmentState(TypedDict):
    evidence: dict
    finding: dict | None
    review_required: bool


def demo_langgraph() -> None:
    from langgraph.graph import StateGraph, START, END  # Optional dependency

    def validate_node(state: AssessmentState) -> dict:
        finding = SecurityFinding.model_validate(state["evidence"])
        return {"finding": finding.model_dump()}

    def route_node(state: AssessmentState) -> dict:
        return {"review_required": state["finding"]["severity"] in {"HIGH", "CRITICAL"}}

    workflow = StateGraph(AssessmentState)
    workflow.add_node("validate", validate_node)
    workflow.add_node("flag_for_review", route_node)
    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "flag_for_review")
    workflow.add_edge("flag_for_review", END)
    graph = workflow.compile()
    print(graph.invoke({"evidence": SAMPLE_EVIDENCE, "finding": None,
                        "review_required": False}))
    # Extension exercise: use conditional edges and human approval when needed.


# -----------------------------------------------------------------------------
# OPTION E: LANGFUSE — OPTIONAL observability, not a reasoning agent.
# Requires an accessible Langfuse backend and configured credentials.
# It may transmit telemetry; do not send secrets, PII, or sensitive evidence.
# -----------------------------------------------------------------------------
def demo_langfuse() -> None:
    from langfuse import get_client  # Optional dependency

    needed = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
    missing = [name for name in needed if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Configure Langfuse before running: {', '.join(missing)}")
    langfuse = get_client()
    with langfuse.start_as_current_observation(
        as_type="span", name="simulated-security-validation"
    ) as span:
        finding = SecurityFinding.model_validate(SAMPLE_EVIDENCE)
        # Only minimal non-sensitive metadata in this classroom illustration.
        span.update(output={"severity": finding.severity, "validated": True})
    langfuse.flush()
    print("Sent a simple validation span to the configured Langfuse backend.")


# -----------------------------------------------------------------------------
# OPTION F: HERMES AGENT — A DIFFERENT option: a prebuilt agent runtime.
# It is not a drop-in replacement for `from crewai import Agent`.
# Students should FIRST decide whether they need a ready-made autonomous agent.
# Do not automatically install or launch it from this reference script.
# -----------------------------------------------------------------------------
def demo_hermes_info() -> None:
    print("Hermes Agent is an optional standalone agent runtime.")
    print("Review its installation, permissions, approval controls, skills,")
    print("tool execution and model configuration before running it.")
    print("Docs: https://hermes-agent.nousresearch.com/docs/")
    print("Potential exercise: compare Hermes capabilities to a custom CrewAI")
    print("or LangChain agent against YOUR written requirements.")
    # Deliberately no subprocess, install, network request, or autonomous action.


def main() -> None:
    parser = argparse.ArgumentParser(description="Requirements-first AI framework reference")
    parser.add_argument("--demo", choices=["pydantic", "crewai", "langchain",
                                           "langgraph", "langfuse", "hermes-info"],
                        default="pydantic")
    args = parser.parse_args()
    demos = {
        "pydantic": demo_pydantic,
        "crewai": demo_crewai,
        "langchain": demo_langchain,
        "langgraph": demo_langgraph,
        "langfuse": demo_langfuse,
        "hermes-info": demo_hermes_info,
    }
    demos[args.demo]()


if __name__ == "__main__":
    main()
