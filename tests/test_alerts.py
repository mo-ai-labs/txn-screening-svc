CLOSE_BODY = {"disposition": "false_positive", "reason": "Name-only match, different entity"}


def test_list_alerts(client, alert_id):
    response = client.get("/alerts")
    assert response.status_code == 200
    assert [alert["id"] for alert in response.json()] == [alert_id]


def test_list_alerts_filters_by_status(client, alert_id):
    client.post(f"/alerts/{alert_id}/close", json=CLOSE_BODY)
    assert client.get("/alerts", params={"alert_status": "open"}).json() == []
    assert len(client.get("/alerts", params={"alert_status": "closed"}).json()) == 1


def test_list_alerts_filters_by_assignee(client, alert_id):
    client.post(f"/alerts/{alert_id}/assign", json={"assignee": "analyst-1"})
    assert len(client.get("/alerts", params={"assignee": "analyst-1"}).json()) == 1
    assert client.get("/alerts", params={"assignee": "analyst-2"}).json() == []


def test_get_alert(client, alert_id):
    response = client.get(f"/alerts/{alert_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == alert_id
    assert body["status"] == "open"
    assert {hit["rule_id"] for hit in body["hits"]} == {"WATCHLIST_NAME", "HIGH_RISK_COUNTRY"}


def test_get_unknown_alert_returns_404(client):
    assert client.get("/alerts/alt_missing").status_code == 404


def test_assign_alert(client, alert_id):
    response = client.post(f"/alerts/{alert_id}/assign", json={"assignee": "analyst-1"})
    assert response.status_code == 200
    assert response.json()["assignee"] == "analyst-1"


def test_add_note(client, alert_id):
    response = client.post(f"/alerts/{alert_id}/notes", json={"author": "analyst-1", "text": "Looking into it"})
    assert response.status_code == 201
    assert response.json()["text"] == "Looking into it"

    notes = client.get(f"/alerts/{alert_id}").json()["notes"]
    assert [note["text"] for note in notes] == ["Looking into it"]


def test_close_alert(client, alert_id):
    response = client.post(f"/alerts/{alert_id}/close", json=CLOSE_BODY)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "closed"
    assert body["disposition"] == "false_positive"
    assert body["close_reason"] == CLOSE_BODY["reason"]
    assert body["closed_at"] is not None


def test_closed_alert_cannot_be_closed_or_assigned(client, alert_id):
    client.post(f"/alerts/{alert_id}/close", json=CLOSE_BODY)
    assert client.post(f"/alerts/{alert_id}/close", json=CLOSE_BODY).status_code == 409
    assert client.post(f"/alerts/{alert_id}/assign", json={"assignee": "analyst-1"}).status_code == 409


def test_close_rejects_unknown_disposition(client, alert_id):
    response = client.post(f"/alerts/{alert_id}/close", json={"disposition": "maybe", "reason": "x"})
    assert response.status_code == 422
