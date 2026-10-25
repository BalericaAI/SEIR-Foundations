# Agent Framework Options — Requirements First

> **CLASSROOM REFERENCE, NOT LAW.** This package is a collection of independent examples, not a mandated stack. Do not install or combine every framework automatically. Define your requirements first, select the smallest suitable architecture, and justify your choices.

## Before writing agent code

Write a brief decision record: business problem; inputs and outputs; trust boundaries; required LLM behavior; tool permissions; approval gates; acceptable latency and cost; observability; evaluation tests; deployment environment; and conditions for success or failure. Determine whether an LLM or multi-agent design is needed at all.

## What the options mean

| Option | Potential purpose | When it may be unnecessary |
| --- | --- | --- |
| Pydantic | Validated schemas and output contracts | No structured inputs or outputs |
| CrewAI | Role-oriented specialist agent execution | Simple deterministic logic or one tool call |
| LangChain | LLM, tool, and retrieval integration | No LLM/tool integration needed, or another library already suffices |
| LangGraph | Stateful workflow, routing, and human gates | Straight-line execution with no state management needs |
| Langfuse | Tracing, evaluation, prompt and cost observability | Existing monitoring fully meets documented needs |
| Hermes Agent | Ready-made autonomous agent runtime and skills | Custom restrictive workflow provides better governance |

CrewAI and LangChain are often **alternatives** for a particular agent implementation. CrewAI and LangGraph can coexist, but students must decide *which component owns orchestration* to prevent conflicting execution control. LangChain's higher-level agents already use LangGraph internally; adding another graph is not automatically useful. Hermes is not merely another Python class that must be added to the same process.

## Run the independent examples

```bash
python -m pip install 'pydantic>=2,<3'
python sample.py                    # local, no LLM or network
python sample.py --demo hermes-info # information only

# Install only the dependency for the chosen experiment:
python -m pip install langgraph
python sample.py --demo langgraph   # local, no LLM

# Optional provider-backed experiments; configure model credentials first:
python -m pip install crewai
python sample.py --demo crewai

python -m pip install langchain langchain-openai
python sample.py --demo langchain

# Langfuse needs LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
python -m pip install langfuse
python sample.py --demo langfuse
```

Tested: syntax and local Pydantic demonstration (where dependencies are available). Optional provider-backed examples are **reference snippets** and have not been run against live services. Review dependency/version changes, pricing and approval requirements before use.

## Example questions for students

1. What requirements justify using a model rather than ordinary Python?
2. Does the security finding require a Pydantic contract? What can the contract *not* prove?
3. Would one agent suffice? What concrete benefit is gained by using several?
4. Who controls state, retries, failures, approvals, and termination?
5. Which calls cross a network boundary? What secrets and IAM permissions do they need?
6. Which frameworks can be removed while preserving the required behavior?

### Official documentation

- [Pydantic](https://docs.pydantic.dev/latest/)
- [CrewAI](https://docs.crewai.com/)
- [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)
- [Langfuse](https://langfuse.com/docs)
- [Hermes Agent](https://hermes-agent.nousresearch.com/docs/)
