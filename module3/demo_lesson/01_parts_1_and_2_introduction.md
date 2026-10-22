# Agentic AI Frameworks — Parts 1 & 2: Introduction and Comparison

**Class Lecture 01**  
**Topic:** Pydantic, LangChain, LangGraph, Hermes Agent, CrewAI, and Langfuse

## Part 1 — The Big Picture

Before students start installing Python libraries and building autonomous agents, they need to understand something fundamental:

> **These six technologies do not all perform the same job.** They address different problems in the development, execution, coordination, and monitoring of AI applications.

Some overlap, some compete, and some complement each other.

Consider a traditional application built with Python, FastAPI, PostgreSQL, and AWS ECS. Each component has a distinct responsibility:

- **FastAPI** exposes application endpoints.
- **PostgreSQL** manages persistent data.
- **Amazon ECS** runs containers.

Agentic AI applications follow a similar architectural principle, except that we introduce components capable of interpreting information, selecting tools, making decisions, and collaborating with other agents.

An LLM such as GPT, Claude, or Llama supplies model capabilities. Frameworks provide the software architecture around the model.

## Part 2 — The Six Technologies at a Glance

| Technology | Primary responsibility | Simple explanation |
| --- | --- | --- |
| **Pydantic** | Data validation | Makes sure data is structured and valid. |
| **LangChain** | LLM application development | Connects models, prompts, tools, and external data. |
| **LangGraph** | Workflow orchestration | Controls stateful execution, branching, and recovery. |
| **Hermes Agent** | Autonomous agent runtime | Provides a working agent that can use tools and accumulate reusable skills. |
| **CrewAI** | Multi-agent collaboration | Organizes specialized AI agents into cooperating teams. |
| **Langfuse** | Observability and evaluation | Tracks what agents did, how well they performed, and what they cost. |

The first five can participate directly in building or running intelligent functionality. Langfuse primarily helps engineers observe, debug, and improve that functionality.

> **Terminology:** **Pydantic** is not **PydanticAI**. Pydantic is a Python data-validation library; PydanticAI is a separate framework for constructing AI agents using typed interfaces.

### Learning objectives

After this introduction, students should be able to:

1. Describe the principal purpose of each technology.
2. Explain why these technologies are not interchangeable.
3. Identify which responsibilities belong to the model, the agent runtime, the application, and the infrastructure.

### Discussion prompt

**Question:** If an LLM can generate Python code and call an API, why do we need an application framework at all?

**Instructor direction:** Ask students to consider repeatability, access control, typed data, state management, execution recovery, and observability.
