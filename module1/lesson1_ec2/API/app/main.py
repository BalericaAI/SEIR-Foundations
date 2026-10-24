# ============================================================
#                       BALERICA AI
#                    SEIR FOUNDATIONS
# ============================================================
#
#                 BALERICA LEGACY BANK API
#
# Chewbacca says:
#
#     "RRRRAAAWWWRRR!"
#
# Translation:
#
#     You survived SSH.
#     You survived vi.
#     You survived Python.
#     You survived FastAPI.
#
#     Now meet the systems that were already running
#     before any of those existed.
#
#     This API is the modern face of a COBOL core.
#
#     That sentence describes most banks on Earth.
#
# ============================================================
#
#     ARCHITECTURE
#
#         SWIFT Traffic Generator
#                  |
#                  v
#               FastAPI          <- this file
#                  |
#                  v
#            cobol_bridge.py
#                  |
#                  v
#         account_lookup / payment_post   (GnuCOBOL)
#                  |
#                  v
#         accounts.dat / payments.dat     (fixed width)
#                  |
#                  v
#               SQLite                    (system of record)
#
#     And on the side, when humans get confused:
#
#               POST /ask
#                  |
#                  v
#            Balerica AI helper agent
#                  |
#                  v
#            Amazon Bedrock
#
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# uvicorn is started from BANK_HOME as "app.main:app".
# Make app/ (for cobol_bridge) and agents/ (for balerica)
# importable regardless of how the server is launched.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "agents"))

import cobol_bridge
import balerica


app = FastAPI(
    title="Balerica Legacy Bank",
    description="SEIR Foundations - FastAPI with a COBOL core",
    version="1.0",
)


# ------------------------------------------------------------
# REQUEST MODELS
#
# Chewbacca says: "RRRAAAWR?"
#
# Translation:
#
#     The SWIFT MT103 message carries many fields.
#
#     Our API accepts the ones the bank core needs.
#
#     Pydantic rejects garbage before it reaches COBOL.
# ------------------------------------------------------------

class SwiftPayment(BaseModel):
    reference: str = Field(..., max_length=16)
    account_id: str = Field(..., min_length=6, max_length=6)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    ordering_customer: str = ""
    beneficiary: str = ""


class Question(BaseModel):
    question: str


# ------------------------------------------------------------
# HOMEPAGE
# ------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Balerica Legacy Bank</title></head>
        <body>
            <h1>Balerica Legacy Bank</h1>
            <h2>SEIR Foundations</h2>
            <p>FastAPI front office. COBOL back office.</p>
            <hr>
            <h3>Platform</h3>
            <p>Amazon EC2 + GnuCOBOL + SQLite</p>
            <h3>Status</h3>
            <p>FastAPI: ONLINE</p>
            <hr>
            <p><a href="/docs">Open Balerica Bank API Console</a></p>
        </body>
    </html>
    """


@app.get("/status")
def status():
    return {
        "platform": "Balerica Legacy Bank",
        "environment": "Amazon EC2",
        "api": "online",
        "core_banking": "GnuCOBOL",
    }


# ------------------------------------------------------------
# ACCOUNT LOOKUP
#
#     GET /accounts/100001
#
# The web layer never touches the ledger directly.
# COBOL answers. FastAPI translates.
# ------------------------------------------------------------

@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    result = cobol_bridge.account_lookup(account_id)

    if result["return_code"] == 4:
        raise HTTPException(status_code=404, detail="Account not found")

    if result["return_code"] != 0:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Core banking error"),
        )

    return {
        "account": result["account"],
        "name": result["name"],
        "status": result["status"],
        "balance": float(result["balance"]),
        "currency": result["currency"],
        "source": "account_lookup.cob",
    }


# ------------------------------------------------------------
# PAYMENT POSTING
#
#     POST /payments
#
# Chewbacca says:
#
#     "RRRRRAAAAAAAAAAWWWWWRRRR!"
#
# Translation:
#
#     The traffic generator sends an MT103-style payment.
#
#     FastAPI validates the envelope.
#
#     COBOL renders the verdict.
#
#     Return code 0 = POSTED.
#     Anything else = the auditors want a word.
# ------------------------------------------------------------

@app.post("/payments")
def post_payment(payment: SwiftPayment):
    verdict = cobol_bridge.post_payment(
        account_id=payment.account_id,
        amount=payment.amount,
        currency=payment.currency.upper(),
        reference=payment.reference,
    )

    http_status = 200 if verdict.get("status") == "POSTED" else 422

    response = {
        "transaction_id": verdict.get("txn"),
        "account_id": payment.account_id,
        "amount": payment.amount,
        "currency": payment.currency.upper(),
        "status": verdict.get("status", "UNKNOWN"),
        "reason": verdict.get("reason", ""),
        "cobol_return_code": verdict["return_code"],
        "source": "payment_post.cob",
    }

    if http_status != 200:
        raise HTTPException(status_code=http_status, detail=response)

    return response


# ------------------------------------------------------------
# TRANSACTION JOURNAL
# ------------------------------------------------------------

@app.get("/transactions")
def transactions(limit: int = 50):
    records = cobol_bridge.list_transactions(limit=limit)
    return {"count": len(records), "transactions": records}


# ------------------------------------------------------------
# ASK BALERICA AI
#
#     POST /ask
#
# The helper agent. Students hit COBOL return codes,
# file-status errors, and SWIFT jargon for the first time.
# Balerica AI explains instead of judging.
# ------------------------------------------------------------

@app.post("/ask")
def ask_balerica(request: Question):
    try:
        answer = balerica.ask(request.question)
        return {
            "question": request.question,
            "response": answer["response"],
            "source": answer["source"],
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ------------------------------------------------------------
# CHEWBACCA PLATFORM DIAGNOSTIC
#
# Still absolutely essential enterprise functionality.
# ------------------------------------------------------------

@app.get("/chewbacca")
def chewbacca():
    return {
        "status": "operational",
        "message": "RRRRAAAWWWRRR!",
        "translation": "Balerica Legacy Bank is online. "
                       "The COBOL is older than your parents' mortgage.",
    }
