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
    response = client.post("/transactions/screen", json=make_txn(amount=-5, currency="EURO"))
    assert response.status_code == 422


def test_screen_rejects_lowercase_currency(client):
    response = client.post("/transactions/screen", json=make_txn(currency="eur"))
    assert response.status_code == 422


def test_screen_rejects_numeric_currency(client):
    response = client.post("/transactions/screen", json=make_txn(currency="123"))
    assert response.status_code == 422


def test_screen_rejects_lowercase_originator_country(client):
    response = client.post("/transactions/screen", json=make_txn(originator_country="de"))
    assert response.status_code == 422


def test_screen_rejects_numeric_originator_country(client):
    response = client.post("/transactions/screen", json=make_txn(originator_country="12"))
    assert response.status_code == 422


def test_screen_rejects_lowercase_beneficiary_country(client):
    response = client.post("/transactions/screen", json=make_txn(beneficiary_country="de"))
    assert response.status_code == 422


def test_screen_rejects_numeric_beneficiary_country(client):
    response = client.post("/transactions/screen", json=make_txn(beneficiary_country="12"))
    assert response.status_code == 422


def test_screen_rejects_whitespace_reference(client):
    response = client.post("/transactions/screen", json=make_txn(reference="   "))
    assert response.status_code == 422


def test_screen_rejects_whitespace_originator_name(client):
    response = client.post("/transactions/screen", json=make_txn(originator_name="   "))
    assert response.status_code == 422


def test_screen_rejects_whitespace_beneficiary_name(client):
    response = client.post("/transactions/screen", json=make_txn(beneficiary_name="   "))
    assert response.status_code == 422


def test_screen_rejects_amount_with_more_than_two_decimal_places(client):
    response = client.post("/transactions/screen", json=make_txn(amount=10.123))
    assert response.status_code == 422


def test_rules_are_listed(client):
    ids = {rule["id"] for rule in client.get("/rules").json()}
    assert ids == {"WATCHLIST_NAME", "HIGH_RISK_COUNTRY", "LARGE_AMOUNT", "ROUND_AMOUNT"}
