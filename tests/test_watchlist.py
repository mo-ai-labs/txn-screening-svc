from tests.conftest import make_txn


def test_list_watchlist_has_seed_entries(client):
    names = {entry["name"] for entry in client.get("/watchlist").json()}
    assert "Globex Front LLC" in names


def test_added_entry_is_used_in_screening(client):
    response = client.post("/watchlist", json={"name": "Wile E. Sample"})
    assert response.status_code == 201
    assert response.json()["list_name"] == "SYNTH-SANCTIONS"

    screened = client.post("/transactions/screen", json=make_txn(originator_name="Wile E Sample")).json()
    assert screened["decision"] == "review"


def test_removed_entry_no_longer_matches(client):
    entry_id = next(e["id"] for e in client.get("/watchlist").json() if e["name"] == "Globex Front LLC")
    assert client.delete(f"/watchlist/{entry_id}").status_code == 204

    screened = client.post("/transactions/screen", json=make_txn(beneficiary_name="Globex Front LLC")).json()
    assert screened["decision"] == "clear"


def test_remove_unknown_entry_returns_404(client):
    assert client.delete("/watchlist/wl_missing").status_code == 404
