# Lab 02: Build the Security Analyst Agent (CrewAI + Pydantic)

**Prerequisite:** [Architecture introduction](01_ARCHITECTURE.md).  
**Goal:** Build one read-only AI Security Analyst that analyzes a local snapshot, produces a structured report, and validates it against a Pydantic schema.

> Safety boundary: This lab uses fabricated AWS security-group data. No live AWS credentials, scanning, remediation, or `terraform apply` are required.

## Source files

```text
crewai_pydantic_classroom/
├── 01_ARCHITECTURE.md
├── 02_SECURITY_ANALYST_LAB.md
├── requirements.txt
├── security_analyst.py
└── fixtures/
    └── security_snapshot.json
```

## Before we code: the mental model

- `Agent(...)`, `Task(...)`, and `Crew(...)` are **Python objects** created by the `crewai` library.
- `BaseModel` and `Field` are **Python classes/functions** from the `pydantic` package.
- `output_pydantic=SecurityReport` passes a **class reference** to CrewAI. It is **not** an HTTP URL.
- `crew.kickoff()` runs the CrewAI workflow and may trigger a real **LLM model API call**.
- The JSON fixture is **local file input**, not a real-time AWS scan.

## Step 1 — Set up a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

> Your Python version must be compatible with your selected CrewAI release. Pin and test dependency versions in a classroom lockfile before a scheduled lab.

## Step 2 — Inspect the evidence

Open [`fixtures/security_snapshot.json`](fixtures/security_snapshot.json). It contains a mock AWS security group allowing TCP/22 from `0.0.0.0/0`, plus a more restricted TCP/443 rule. The `source_file` and `line` fields provide provenance hints for this invented Terraform example; they are **not proof the Terraform file was parsed**.

Ask students: *Which rule deserves review, and what additional operational context would change the risk assessment?*

## Step 3 — Read the Pydantic schemas

The script defines:

```python
class SecurityFinding(BaseModel):
    resource_id: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    title: str = Field(min_length=5)
    explanation: str = Field(min_length=15)
    evidence: list[str] = Field(min_length=1)
    recommendation: str = Field(min_length=10)
```

This contract can reject a value like `severity="EXTREME"` or an empty `evidence` list. It **cannot** prove that a vulnerability is real. Validation is structural, not factual.

## Step 4 — Run the validation-only exercise FIRST

```bash
python security_analyst.py --validate-only
```

This mode does **not import CrewAI**, does **not need an API key**, and performs **no network calls**. It reads the JSON and constructs Pydantic objects. Students can deliberately change the example's severity to an invalid value and observe a validation error.

## Step 5 — Create the CrewAI Agent

The complete, commented source is [`security_analyst.py`](security_analyst.py). Focus on:

```python
analyst = Agent(
    role="AWS Security Analyst",
    goal="Find supported AWS network risks in the supplied evidence",
    backstory="You are a cautious cloud security reviewer.",
    llm=model_name,
    allow_delegation=False,
)
```

This constructs an object. It does not launch a VM or connect to an agent server.

## Step 6 — Define a Task with Pydantic output

```python
task = Task(
    description="Analyze the supplied security snapshot ...",
    expected_output="A structured security report",
    agent=analyst,
    output_pydantic=SecurityReport,
)
```

The ellipsis above is explanatory shorthand. **The runnable script uses the full task description and embeds the validated snapshot.**

`output_pydantic=SecurityReport` is the key integration: CrewAI structures the output according to a Pydantic model inside the application's Python environment.

## Step 7 — Assemble the Crew and call the LLM

```python
crew = Crew(
    agents=[analyst],
    tasks=[task],
    process=Process.sequential,
)
result = crew.kickoff()
```

Here `crew.kickoff()` can communicate with the configured LLM provider. **That model API is the network boundary**, not Pydantic.

For an OpenAI-backed example:

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
export MODEL_NAME="openai/gpt-4.1-mini"
python security_analyst.py --run-agent
```

Never commit credentials to a Git repository. Other providers, including Bedrock, may require different CrewAI/LiteLLM configuration, credentials, and dependency support.

## Step 8 — Inspect the result

The script checks whether `result.pydantic` exists, validates it again at the application boundary, and checks that the reported assessment and resource IDs match the input. It prints the JSON only after these checks.

**Important:** A valid report can still contain an incorrect risk conclusion or misquoted evidence. Later labs should add deterministic checks that each evidence string maps to an actual source record, and require human review before making changes.

## Instructor discussion prompts

1. Locate the first line where the LLM could be contacted. *(Answer: `crew.kickoff()` triggers model execution.)*
2. Which lines instantiate local Python objects? *(Answer: `SecurityFinding(...)`, `Agent(...)`, `Task(...)`, and `Crew(...)`.)*
3. Would three agents necessarily require three AWS ECS services? *(Answer: no.)*
4. Can Pydantic detect a fabricated CVE number if it is a valid string? *(Answer: not by itself.)*
5. Why is this agent not permitted to run `terraform apply`? *(Answer: analysis is not authorization to modify infrastructure.)*

## Next extension

Implement the Infrastructure Agent with read-only Terraform parsing, a `TerraformAssessment` output model, and a separate verification step. Then add a Compliance Auditor whose report must distinguish `PASS`, `FAIL`, and `REVIEW` based on explicitly provided evidence and controls.

## Documentation

- [CrewAI](https://docs.crewai.com/)
- [CrewAI task outputs](https://docs.crewai.com/concepts/tasks)
- [Pydantic](https://docs.pydantic.dev/latest/)
