import pytest

from tests.conftest import make_txn


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_screen_clean_transaction_creates_no_alert(client, store):
    response = client.post("/transactions/screen", json=make_txn())
    assert response.status_code == 201
    body = response.json()
    assert body["decision"] == "clear"
    assert body["alert_id"] is None
    assert store.alerts == {}


def test_screen_suspicious_transaction_opens_alert(client):
    response = client.post(
        "/transactions/screen",
        json=make_txn(beneficiary_name="Acme Shell Holdings"),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["decision"] == "review"
    assert body["risk_score"] == 70

    alert = client.get(f"/alerts/{body['alert_id']}").json()
    assert alert["status"] == "open"
    assert alert["transaction_id"] == body["transaction_id"]


def test_get_screening_result(client):
    screened = client.post("/transactions/screen", json=make_txn()).json()
    response = client.get(f"/transactions/{screened['transaction_id']}")
    assert response.status_code == 200
    assert response.json() == screened


def test_get_unknown_transaction_returns_404(client):
    assert client.get("/transactions/txn_missing").status_code == 404


def test_screen_rejects_invalid_payload(client):
    response = client.post("/transactions/screen", json=make_txn(amount=-5))
    assert response.status_code == 422


@pytest.mark.parametrize("currency", ["eur", "123"])
def test_screen_rejects_invalid_currency(client, currency):
    response = client.post("/transactions/screen", json=make_txn(currency=currency))
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "country"),
    [
        ("originator_country", "de"),
        ("originator_country", "12"),
        ("beneficiary_country", "de"),
        ("beneficiary_country", "12"),
    ],
)
def test_screen_rejects_invalid_country_code(client, field, country):
    response = client.post("/transactions/screen", json=make_txn(**{field: country}))
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["originator_name", "beneficiary_name", "reference"])
def test_screen_rejects_whitespace_only_text(client, field):
    response = client.post("/transactions/screen", json=make_txn(**{field: "   "}))
    assert response.status_code == 422


def test_screen_rejects_amount_with_more_than_two_decimal_places(client):
    response = client.post("/transactions/screen", json=make_txn(amount=10.123))
    assert response.status_code == 422


def test_rules_are_listed(client):
    ids = {rule["id"] for rule in client.get("/rules").json()}
    assert ids == {"WATCHLIST_NAME", "HIGH_RISK_COUNTRY", "LARGE_AMOUNT", "ROUND_AMOUNT"}
