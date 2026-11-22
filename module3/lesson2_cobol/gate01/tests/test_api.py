from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def stub(operation, *args):
    return {
        "PING": ["READY"],
        "INTEREST": ["100.00", "1100.00"],
        "LOAN": ["100.00"],
        "TRANSFER": ["APPROVED"],
    }[operation]


def test_health_does_not_depend_on_cobol():
    assert client.get("/health").status_code == 200


def test_ready_calls_cobol():
    with patch("app.main.run_cobol", side_effect=stub) as backend:
        assert client.get("/ready").json() == {"status":"ready"}
        backend.assert_called_once_with("PING")


def test_interest_contract():
    with patch("app.main.run_cobol", side_effect=stub):
        response = client.post("/v1/interest", json={"principal":"1000.00", "annual_rate_percent":"5.00", "years":2})
        assert response.status_code == 200
        assert response.json()["interest"] == "100.00"


def test_loan_contract():
    with patch("app.main.run_cobol", side_effect=stub):
        response = client.post("/v1/loan-payment", json={"principal":"1200.00", "annual_rate_percent":"0.00", "months":12})
        assert response.json()["monthly_payment"] == "100.00"


def test_transfer_never_posts_money():
    with patch("app.main.run_cobol", side_effect=stub):
        response = client.post("/v1/transfer/validate", json={"amount":"250.00", "available_balance":"500.00"})
        assert response.json() == {"decision":"APPROVED", "posted":False}


def test_bad_amount_rejected_before_cobol():
    with patch("app.main.run_cobol") as backend:
        response = client.post("/v1/interest", json={"principal":"1.234", "annual_rate_percent":"5", "years":2})
        assert response.status_code == 422
        backend.assert_not_called()


def test_negative_amount_rejected():
    response = client.post("/v1/transfer/validate", json={"amount":"-20", "available_balance":"50"})
    assert response.status_code == 422


def test_readiness_degrades_when_binary_missing():
    with patch("app.main.BINARY", "/does/not/exist/finance"):
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503


def test_info_has_hostname():
    assert client.get("/v1/info").json()["hostname"]
