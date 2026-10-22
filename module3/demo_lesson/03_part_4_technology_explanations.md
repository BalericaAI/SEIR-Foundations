# Agentic AI Frameworks — Part 4: What Each Technology Does

**Class Lecture 01**  
**Topic:** The responsibilities and limits of six agentic AI technologies

## Part 4 — What Each Technology Actually Does

### 4.1 Pydantic — Data Integrity

Pydantic validates and structures Python data. It checks types, required fields, ranges, and other constraints.

**Classroom example:** An AI security agent recommends blocking an IP address. Pydantic verifies that the returned object has a valid IP address, an accepted severity level, and a properly structured recommendation.

**Important limitation:** Pydantic does not determine whether the recommendation is *correct*. It determines whether the data meets the defined rules.

### 4.2 LangChain — LLM Integration

LangChain provides components for building applications that connect LLMs with tools, databases, retrieval systems, and external services. It also offers higher-level agent capabilities.

**Classroom example:** An agent receives a CloudWatch alarm, retrieves application logs, searches internal troubleshooting documentation, and asks a model to explain the likely cause.

**Key idea:** LangChain makes those integrations easier without requiring students to write every connection from scratch.

### 4.3 LangGraph — State and Control

LangGraph is designed for stateful workflows where execution can branch, pause, resume, loop, or involve human approval.

**Classroom example:** A security agent identifies a potential vulnerability, passes its findings to a verification agent, requests human authorization when necessary, and only then proceeds to remediation.

**Key idea:** LangGraph manages transitions and preserves relevant workflow state. It underpins LangChain's higher-level agent implementation but can also be used directly.

### 4.4 Hermes Agent — Autonomous Execution

Hermes Agent, developed by Nous Research, is a deployable AI agent with tool use, persistent knowledge, reusable skill creation, and delegation capabilities.

**Classroom example:** A student installs Hermes Agent on a Linux VM, connects an LLM, and gives it a task to examine a repository, run tests, produce findings, and preserve a reusable troubleshooting skill.

**Key distinction:** Unlike LangGraph, which is used to create custom execution workflows, Hermes Agent already provides a substantial working agent runtime.

**Important limitation:** Learning or reusing skills does not mean the system has automatically retrained the underlying LLM weights.

### 4.5 CrewAI — Collaborative Agents

CrewAI emphasizes multiple specialized agents working together. Developers assign roles, tasks, tools, and objectives.

**Classroom example:** A Security Analyst Agent examines vulnerabilities, an Infrastructure Agent checks Terraform configurations, and an Auditor Agent prepares compliance findings.

**Key idea:** CrewAI also provides **Flows** for structured execution. As a result, its capabilities overlap with LangGraph; it is not limited to simple agent teams.

### 4.6 Langfuse — Observability and Evaluation

Langfuse instruments LLM and agent applications so engineers can trace model requests, tool calls, execution paths, latency, cost, and output quality.

**Classroom example:** An agent generates an incorrect remediation proposal. Langfuse helps students investigate which model was called, what context was supplied, which tools executed, and where the workflow may have gone wrong.

**Key idea:** Langfuse also supports prompt management, datasets, experiments, and evaluation. It helps engineers **observe and improve** applications rather than acting as their main workflow engine.

## Summary: What Question Does Each Answer?

| Technology | Question it helps answer |
| --- | --- |
| Pydantic | Is the data valid? |
| LangChain | How do I connect a model to tools and data? |
| LangGraph | How do I control a stateful, multi-step process? |
| Hermes Agent | How do I run an existing autonomous agent with tools and skills? |
| CrewAI | How do I organize cooperating specialized agents? |
| Langfuse | How do I understand and evaluate what happened? |

### Classroom discussion

**Question:** If five agents agree on an incorrect action, does agreement make that action safe?

**Instructor direction:** No. Agreement among agents is not a substitute for evidence, authorization, independent verification, or policy enforcement.
