# Balerica AI — FastAPI `app.py`

## SEIR Foundations — AI Platform Engineering

---

## Why Are We Building `app.py`?

Until this point, Balerica AI has primarily been a command-line application.

You connect to the EC2 instance:

```bash
ssh ...
```

Move into the python directory:

```bash
cd module1/lesson1_ec2/python
```

And execute Balerica AI:

```bash
python ask.py
```

This works.

However, other applications cannot easily interact with Balerica AI this way.

Modern engineering platforms commonly expose functionality through **APIs**.

`app.py` begins that transformation.

```text
Command Line Application
        |
        v
      FastAPI
        |
        v
       API
        |
        v
Engineering Platform
```

We are not replacing Balerica AI.

We are creating another way to communicate with it.

---

# What Is FastAPI?

FastAPI is a Python framework for building APIs.

An API allows one software system to communicate with another software system through a defined interface.

For Balerica AI, FastAPI becomes the doorway between external clients and our existing Python agents.

```text
Browser
   |
   v
FastAPI
   |
   v
Balerica AI
```

Later, many different systems could use the same API.

```text
                  Balerica AI API
                        |
        +---------------+---------------+
        |               |               |
     Browser           CLI          Automation
```

The important concept is that Balerica AI no longer needs to know **who is asking**.

It simply receives a properly structured request.

---

# What Does `app.py` Do?

`app.py` is the **web and API layer** of Balerica AI.

It should remain relatively small.

Its responsibilities include:

* Starting the FastAPI application
* Receiving HTTP requests
* Validating incoming data
* Exposing Balerica AI agents
* Sending requests to `ask.py`
* Returning responses to the client

It should **not** contain all of Balerica AI's engineering logic.

---

# Separation of Responsibilities

Balerica AI is intentionally divided into components.

```text
                    USER
                     |
                     v
                  app.py
                     |
                     v
                  ask.py
                     |
                     v
                auditor.py
                     |
                     v
              Agent Framework
                     |
        +------------+------------+
        |            |            |
        v            v            v
    health.py    cost.py    analyze_logs.py
        |            |            |
        +------------+------------+
                     |
                     v
                 bedrock.py
                     |
                     v
               Amazon Bedrock
```

Each component has a different responsibility.

### `app.py`

Handles HTTP and the API.

### `ask.py`

Coordinates Balerica AI and determines which capabilities should be used.

### `auditor.py`

Examines incoming requests before they are processed.

### Agents

Perform specific engineering tasks.

Examples include:

```text
health.py
telemetry.py
analyze_logs.py
cost.py
suggestion.py
```

### `bedrock.py`

Handles communication with Amazon Bedrock foundation models.

This separation makes Balerica AI easier to understand, test, modify, and eventually deploy to different platforms.

---

# What Is an API Endpoint?

An endpoint is a location exposed by an API.

For example:

```text
/status
```

could return information about Balerica AI.

```text
/agents
```

could return the agents currently installed.

```text
/agent/health
```

could execute the Health agent.

```text
/ask
```

could send a question into the Balerica AI workflow.

Instead of running:

```bash
python health.py
```

an application could request:

```text
/agent/health
```

The capability is the same.

The interface has changed.

---

# GET and POST

You will encounter two important HTTP methods in this lab.

## GET

`GET` normally requests information.

Examples:

```text
GET /status

GET /agents

GET /agent/health
```

The client is asking Balerica AI to return something.

---

## POST

`POST` sends information to the application for processing.

For example:

```text
POST /ask
```

might send:

```json
{
    "question": "Why is my EC2 CPU utilization high?"
}
```

Balerica AI receives the question, processes it, and returns a response.

---

# What Is JSON?

APIs frequently exchange information using JSON.

JSON represents information using structured key/value pairs.

Example:

```json
{
    "platform": "Balerica AI",
    "environment": "Amazon EC2",
    "status": "online"
}
```

Humans can read JSON.

Applications can also easily process JSON.

This makes it useful for communication between systems.

---

# Why Are We Using Pydantic?

You will see this inside `app.py`:

```python
from pydantic import BaseModel
```

and later:

```python
class QuestionRequest(BaseModel):
    question: str
```

This is our first introduction to **Pydantic**.

Pydantic allows Python applications to define the structure of the data they expect.

Balerica AI expects something like:

```json
{
    "question": "Analyze my EC2 instance."
}
```

The value of `question` should be text.

Pydantic helps validate that incoming request before our application processes it.

Conceptually:

```text
Human Input
     |
     v
  Pydantic
     |
     | Valid
     v
  FastAPI
     |
     v
 Balerica AI
```

Invalid or malformed data can be rejected before it reaches deeper parts of the application.

---

# Why Does Validation Matter?

Humans are unpredictable.

Software should not assume that incoming data is correct.

An application may expect:

```json
{
    "question": "Analyze my logs."
}
```

But someone could send malformed, missing, or unexpected data.

Validation creates a boundary between external input and internal application logic.

This becomes increasingly important when applications interact with:

* Databases
* Cloud APIs
* Automation systems
* AI models
* Security tools
* Production infrastructure

Later in SEIR, validation will become part of a much larger discussion about secure application design.

For now, remember:

> **Never assume incoming data is correct simply because someone sent it to your API.**

---

# Agent Discovery

Balerica AI is designed to grow.

Today the agents directory might contain:

```text
agents/

health.py
telemetry.py
analyze_logs.py
cost.py
suggestion.py
```

Later it could contain:

```text
network.py
security.py
database.py
```

And someday, when morale becomes dangerously high:

```text
cobol.py
```

`app.py` should not require major modifications every time a new agent is created.

Instead:

```text
app.py
   |
   v
ask.py
   |
   v
Discover Agents
   |
   +-- health.py
   +-- telemetry.py
   +-- cost.py
   +-- network.py
   +-- future_agent.py
```

This is an introduction to **extensible software architecture**.

New capabilities can be added without redesigning the entire application.

---

# FastAPI Gives Us Something for Free

FastAPI automatically generates interactive API documentation.

After starting Balerica AI, you can open:

```text
http://EC2-IP:8000/docs
```

A recorded walkthrough of the homepage and this console is [balerica-api-console-walkthrough.mp4](../API/balerica-api-console-walkthrough.mp4).

FastAPI will display the available endpoints.

For example:

```text
BALERICA AI

GET     /
GET     /status
GET     /agents
GET     /agent/{agent_name}
POST    /ask
GET     /chewbacca
```

You can execute API requests directly from the browser.

This gives us a graphical interface before we build our own graphical Balerica AI console.

---

# The `/chewbacca` Endpoint

Every enterprise platform requires sophisticated diagnostic capabilities.

Balerica AI therefore includes:

```text
GET /chewbacca
```

A successful response may look like:

```json
{
    "status": "operational",
    "message": "RRRRAAAWWWRRR!",
    "translation": "Balerica AI is online."
}
```

This endpoint provides absolutely essential enterprise functionality.

Obviously.

---

# The Engineering Concept

The most important lesson in this lab is not FastAPI syntax.

It is this:

> **Separate capabilities from interfaces.**

Originally:

```text
Human
  |
  v
Command Line
  |
  v
Balerica AI
```

Now:

```text
Human
  |
  v
Browser
  |
  v
FastAPI
  |
  v
Balerica AI
```

The interface changed.

The underlying capabilities did not.

---

# Why This Matters for Amazon ECS

Today Balerica AI runs directly on EC2.

```text
EC2
 |
 +-- FastAPI
 |
 +-- Balerica AI
 |
 +-- Agents
```

Later we can place the application inside a container.

```text
Docker Container
       |
       +-- FastAPI
       |
       +-- Balerica AI
       |
       +-- Agents
```

Amazon ECS can then run that container.

```text
Amazon ECS
     |
     v
Docker Container
     |
     v
FastAPI
     |
     v
Balerica AI
```

Notice what happened.

We changed the deployment platform.

We did **not** redesign the application.

---

# And Later: Amazon EKS

The progression continues.

```text
EC2
 |
 v
FastAPI
 |
 v
Balerica AI
```

becomes:

```text
ECS
 |
 v
Container
 |
 v
FastAPI
 |
 v
Balerica AI
```

and eventually:

```text
EKS
 |
 v
Pod
 |
 v
Container
 |
 v
FastAPI
 |
 v
Balerica AI
```

The infrastructure changes.

The application architecture survives.

---

# Engineering Systems Thinking

SEIR Foundations is not simply teaching you how to configure individual AWS services.

You are learning how engineering systems evolve.

Balerica AI begins as:

```text
Python Scripts
```

Then becomes:

```text
Command-Line Application
```

Then:

```text
API
```

Then:

```text
Web Application
```

Then:

```text
Containerized Application
```

Then:

```text
Distributed Platform
```

At every stage, we reuse what we previously built.

That is intentional.

---

# Chewbacca's Engineering Principle

```text
              RRRRAAAWWWRRR!

                  ||

                  \/

Do not rebuild a working system
simply because you learned a new technology.

Extend it.

Understand it.

Improve it.

Then deploy it somewhere new.
```

That is the purpose of `app.py`.

You are not simply learning FastAPI.

You are turning Balerica AI into a platform.
