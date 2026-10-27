# ============================================================
#                       BALERICA AI
#                    SEIR FOUNDATIONS
# ============================================================
#
#                         _____
#                      .-'     '-.
#                     /  _     _  \
#                    |  / \   / \  |
#                    |  \_/   \_/  |
#                    |      ^      |
#                    |   .-----.   |
#                     \ /|||||||\ /
#                      \|||||||||/
#                       \_|||||_/
#                       / ||||| \
#                      /  |||||  \
#
#                      CHEWBACCA
#                PLATFORM ENGINEERING
#
#                 "RRRRAAAWWWRRR!"
#
# Translation:
#
#     Welcome to FastAPI.
#
#     You survived SSH.
#     You survived vi.
#     You survived Python.
#
#     Now we are putting your work on the web.
#
# ============================================================


# ============================================================
# CODE BLOCK 1
# FASTAPI FOUNDATION
# ============================================================
#
# Chewbacca says:
#
#     "WRRROOOAAARRR!"
#
# Translation:
#
#     This section creates the web application.
#
#     FastAPI is NOT replacing Balerica AI.
#
#     It is providing another way to reach Balerica AI.
#
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import ask


# ------------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RAAWWWR!"
#
# Translation:
#
#     This creates our FastAPI application.
#
#     FastAPI automatically gives us:
#
#         /docs
#
#         /redoc
#
#     Those interfaces are generated for us.
#
#     Accept free labor when the framework offers it.
#
# ------------------------------------------------------------

app = FastAPI(
    title="Balerica AI",
    description="AI Platform Engineering - SEIR Foundations",
    version="1.0"
)


# ------------------------------------------------------------
# DEFINE THE QUESTION FORMAT
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RRRAAAWR?"
#
# Translation:
#
#     Humans send unpredictable things.
#
#     APIs prefer structure.
#
#     Balerica AI expects a question containing text.
#
# ------------------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# ------------------------------------------------------------
# BALERICA AI HOMEPAGE
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RRRRAAAWWWRRR!"
#
# Translation:
#
#     Until now you reached Balerica AI through SSH.
#
#     Now Balerica AI has a web interface.
#
#     Same EC2.
#     Same Python.
#     Same agents.
#
#     Different interface.
#
# ------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>

        <head>
            <title>Balerica AI</title>
        </head>

        <body>

            <h1>Balerica AI</h1>

            <h2>SEIR Foundations</h2>

            <p>AI Platform Engineering Console</p>

            <hr>

            <h3>Platform</h3>

            <p>Amazon EC2</p>

            <h3>Status</h3>

            <p>FastAPI: ONLINE</p>

            <hr>

            <p>
                <a href="/docs">
                    Open Balerica AI API Console
                </a>
            </p>

        </body>

    </html>
    """


# ------------------------------------------------------------
# PLATFORM STATUS
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "WRRROOO!"
#
# Translation:
#
#     Humans like web pages.
#
#     Computers frequently prefer structured data.
#
#     This endpoint returns JSON.
#
# ------------------------------------------------------------

@app.get("/status")
def status():

    return {
        "platform": "Balerica AI",
        "environment": "Amazon EC2",
        "api": "online"
    }


# ------------------------------------------------------------
# DISCOVER INSTALLED AGENTS
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RRRRAAAAWWWRRR!"
#
# Translation:
#
#     app.py should not know every agent by name.
#
#     ask.py discovers them.
#
#     Today:
#
#         health.py
#         telemetry.py
#         analyze_logs.py
#         cost.py
#         suggestion.py
#
#     Tomorrow:
#
#         network.py
#         security.py
#         database.py
#
#     And someday...
#
#         cobol.py
#
#     Yes.
#
#     The COBOL book is still on the shelf.
#
# ------------------------------------------------------------

@app.get("/agents")
def agents():

    discovered = ask.discover_agents()

    catalog = []

    for agent in discovered:

        catalog.append({
            "name": agent.NAME,
            "description": getattr(agent, "DESCRIPTION", ""),
        })

    return {
        "count": len(catalog),
        "agents": catalog
    }

# ============================================================
# CODE BLOCK 2
# BALERICA AI EXECUTION
# ============================================================
#
# Chewbacca says:
#
#     "RRRRRAAAAAAAAAAWWWWWRRRR!"
#
# Translation:
#
#     Your web server works.
#
#     Your API works.
#
#     Balerica AI can see its agents.
#
#     Now we make those agents DO something.
#
# ============================================================


# ------------------------------------------------------------
# RUN AN INDIVIDUAL AGENT
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RAAAAWR!"
#
# Translation:
#
#     FastAPI can read information directly from the URL.
#
#     Therefore:
#
#         /agent/health
#
#     can execute:
#
#         health.py
#
#     and:
#
#         /agent/cost
#
#     can execute:
#
#         cost.py
#
#     One API route can support many agents.
#
#     Do not write 47 routes when one will work.
#
# ------------------------------------------------------------

@app.get("/agent/{agent_name}")
def run_agent(agent_name: str):

    try:

        result = ask.run_agent(agent_name)

        return {
            "agent": agent_name,
            "result": result
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ------------------------------------------------------------
# ASK BALERICA AI
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RRRRRAAAAAAAAAAWWWWWRRRR!"
#
# Translation:
#
#     This is the complete workflow.
#
#
#              HUMAN
#                |
#                v
#             FastAPI
#                |
#                v
#             ask.py
#                |
#                v
#           auditor.py
#                |
#                v
#          Agent Selection
#                |
#                v
#          Balerica Agent
#                |
#                v
#           bedrock.py
#                |
#                v
#         Amazon Bedrock
#
#
#     FastAPI does not perform the analysis.
#
#     FastAPI provides access to the workflow.
#
# ------------------------------------------------------------

@app.post("/ask")
def ask_balerica(request: QuestionRequest):

    try:

        response = ask.run(request.question)

        return {
            "question": request.question,
            "response": response
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ------------------------------------------------------------
# CHEWBACCA PLATFORM DIAGNOSTIC
# ------------------------------------------------------------
#
# Chewbacca says:
#
#     "RRRRAAAWWWRRR!"
#
# Translation:
#
#     This endpoint performs an extremely sophisticated
#     enterprise-grade diagnostic procedure.
#
#     If you receive a Wookiee response:
#
#         FastAPI is running.
#
#     If you do not:
#
#         Check your code.
#
#         Check Uvicorn.
#
#         Check the port.
#
#         Check the Security Group.
#
#         Check the process.
#
#     Only after checking those things
#     are you permitted to blame AWS.
#
# ------------------------------------------------------------

@app.get("/chewbacca")
def chewbacca():

    return {
        "status": "operational",
        "message": "RRRRAAAWWWRRR!",
        "translation": "Balerica AI is online."
    }
