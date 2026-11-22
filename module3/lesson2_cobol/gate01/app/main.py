"""Synthetic bank API: validation in Python, calculation in GnuCOBOL."""
import json
import logging
import os
import re
import socket
import subprocess
import time
import uuid
from decimal import Decimal, InvalidOperation
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="SEIR Module 3 Lab 02", version="1.0.0")
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("seir.lab02")
BINARY = os.getenv("COBOL_BIN", "/usr/local/bin/finance")
TIMEOUT_SECONDS = 2
MONEY_RE = re.compile(r"^(?:0|[1-9][0-9]{0,7})(?:\.[0-9]{1,2})?$")
RATE_RE = re.compile(r"^(?:0|[1-9][0-9]{0,2})(?:\.[0-9]{1,2})?$")


def validate_number(value: str, pattern: re.Pattern, field: str) -> str:
    if not pattern.fullmatch(value):
        raise ValueError(f"{field} must be a nonnegative decimal string with up to 2 decimal places")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not a valid decimal") from exc
    return format(number, ".2f")


class InterestRequest(BaseModel):
    principal: str
    annual_rate_percent: str
    years: Annotated[int, Field(ge=1, le=50)]

    @field_validator("principal")
    @classmethod
    def principal_valid(cls, value):
        return validate_number(value, MONEY_RE, "principal")

    @field_validator("annual_rate_percent")
    @classmethod
    def rate_valid(cls, value):
        return validate_number(value, RATE_RE, "annual_rate_percent")


class LoanRequest(BaseModel):
    principal: str
    annual_rate_percent: str
    months: Annotated[int, Field(ge=1, le=600)]

    @field_validator("principal")
    @classmethod
    def principal_valid(cls, value):
        result = validate_number(value, MONEY_RE, "principal")
        if Decimal(result) == 0:
            raise ValueError("principal must be positive")
        return result

    @field_validator("annual_rate_percent")
    @classmethod
    def rate_valid(cls, value):
        return validate_number(value, RATE_RE, "annual_rate_percent")


class TransferRequest(BaseModel):
    amount: str
    available_balance: str

    @field_validator("amount")
    @classmethod
    def amount_valid(cls, value):
        result = validate_number(value, MONEY_RE, "amount")
        if Decimal(result) == 0:
            raise ValueError("amount must be positive")
        return result

    @field_validator("available_balance")
    @classmethod
    def balance_valid(cls, value):
        return validate_number(value, MONEY_RE, "available_balance")


def run_cobol(operation: str, arg_a="0.00", arg_b="0.00", arg_n="0") -> list[str]:
    try:
        result = subprocess.run(
            [BINARY, operation, str(arg_a), str(arg_b), str(arg_n)],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.error(json.dumps({"event":"cobol_execution_failure", "operation": operation,
                                 "error_type":type(exc).__name__}))
        raise HTTPException(status_code=503, detail="COBOL backend unavailable") from exc
    output = result.stdout.strip().splitlines()
    if result.returncode != 0 or len(output) != 1 or not output[0].startswith("OK|"):
        logger.error(json.dumps({"event":"cobol_invalid_response", "operation":operation,
                                 "return_code":result.returncode}))
        raise HTTPException(status_code=503, detail="COBOL backend unavailable")
    return output[0].split("|")[1:]


@app.middleware("http")
async def access_log(request: Request, call_next):
    start = time.monotonic()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({"event":"http_request", "request_id":request_id,
                            "path":request.url.path, "method":request.method,
                            "status":response.status_code,
                            "duration_ms":round((time.monotonic()-start)*1000, 2)}))
    return response


@app.get("/health")
def health():
    return {"status":"healthy"}


@app.get("/ready")
def ready():
    values = run_cobol("PING")
    if values != ["READY"]:
        raise HTTPException(status_code=503, detail="COBOL readiness check failed")
    return {"status":"ready"}


@app.get("/v1/info")
def info():
    return {"hostname":socket.gethostname(), "version":"gate01"}


@app.post("/v1/interest")
def interest(body: InterestRequest):
    values = run_cobol("INTEREST", body.principal, body.annual_rate_percent, body.years)
    if len(values) != 2:
        raise HTTPException(status_code=503, detail="COBOL invalid result")
    return {"interest":values[0], "total":values[1], "currency":"USD", "method":"simple"}


@app.post("/v1/loan-payment")
def loan(body: LoanRequest):
    values = run_cobol("LOAN", body.principal, body.annual_rate_percent, body.months)
    if len(values) != 1:
        raise HTTPException(status_code=503, detail="COBOL invalid result")
    return {"monthly_payment":values[0], "currency":"USD"}


@app.post("/v1/transfer/validate")
def transfer(body: TransferRequest):
    values = run_cobol("TRANSFER", body.amount, body.available_balance)
    if values not in (["APPROVED"], ["DECLINED"]):
        raise HTTPException(status_code=503, detail="COBOL invalid result")
    return {"decision":values[0], "posted":False}
