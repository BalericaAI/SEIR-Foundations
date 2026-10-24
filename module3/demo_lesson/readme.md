Sample Code


Sample CrewAI Import


    # 04_crewai_example.py
    
    from crewai import Agent, Task, Crew, Process
    
    # Define a security analyst.
    analyst = Agent(
        role="AWS Security Analyst",
        goal="Identify potential AWS security risks",
        backstory="Experienced cloud security engineer",
        llm="openai/gpt-4.1-mini",
        verbose=True
    )
    
    # Define an auditor.
    auditor = Agent(
        role="Security Auditor",
        goal="Review security findings for completeness",
        backstory="Independent cybersecurity reviewer",
        llm="openai/gpt-4.1-mini",
        verbose=True
    )
    
    # Assign work to the analyst.
    analysis_task = Task(
        description=(
            "Evaluate the security risk of an EC2 "
            "security group exposing SSH to 0.0.0.0/0."
        ),
        expected_output="A concise security risk assessment",
        agent=analyst
    )
    
    # Assign work to the auditor.
    audit_task = Task(
        description="Review the analyst's assessment.",
        expected_output="A final reviewed security report",
        agent=auditor,
        context=[analysis_task]
    )
    
    # Coordinate the agents.
    crew = Crew(
        agents=[analyst, auditor],
        tasks=[analysis_task, audit_task],
        process=Process.sequential
    )
    
    result = crew.kickoff()
    print(result)


Sample Import


    from pydantic import BaseModel
    from typing import Literal
    
    class SecurityFinding(BaseModel):
        resource_id: str
        vulnerability: str
        severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    class TerraformAssessment(BaseModel):
        file_path: str
        misconfiguration: str
        recommendation: str
    
    class ComplianceReport(BaseModel):
        framework: str
        status: Literal["PASS", "FAIL", "REVIEW"]
        findings: list[str]
        remediation_required: bool

Sample Import 2 Frameworks


    from typing import Literal
    from pydantic import BaseModel, Field
    from crewai import Agent, Task
    
    # Pydantic: Define the data contract.
    class SecurityFinding(BaseModel):
        resource_id: str
        severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        description: str
        recommendation: str
        evidence: list[str] = Field(min_length=1)
    
    # CrewAI: Define the worker.
    security_agent = Agent(
        role="Security Analyst",
        goal="Identify AWS security vulnerabilities",
        backstory="Experienced cloud security engineer",
    )
    
    # CrewAI: Assign work and specify its output schema.
    security_task = Task(
        description="Analyze the supplied AWS security findings.",
        expected_output="A validated security finding",
        agent=security_agent,
        output_pydantic=SecurityFinding,
    )




How three Agentic AI Framework technologies integrate in Python

The essential integration looks like this:

    # Pydantic defines the structure of a finding.
    class SecurityFinding(BaseModel):
        resource_id: str
        severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        vulnerability: str
        evidence: list[str]
    
    # CrewAI defines the specialist and its expected output.
    task = Task(
        description="Review supplied AWS security evidence",
        expected_output="A structured security finding",
        agent=security_agent,
        output_pydantic=SecurityFinding,
    )
    
    # LangGraph registers the Python function that
    # invokes the CrewAI specialist.
    workflow = StateGraph(AssessmentState)
    
    workflow.add_node("security", security_node)
    workflow.add_node("infrastructure", infrastructure_node)
    workflow.add_node("audit", audit_node)
    
    workflow.add_edge(START, "security")
    # Conditional routing and remaining edges are
    # defined in the complete application.

