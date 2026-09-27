from decimal import Decimal

from app.models import Decision, TransactionIn
from app.screening import screen
from app.store import Store
from tests.conftest import make_txn


def run(**overrides):
    return screen(TransactionIn(**make_txn(**overrides)), list(Store().watchlist.values()))


def rule_ids(hits):
    return sorted(hit.rule_id for hit in hits)


def test_clean_transaction_is_cleared():
    decision, score, hits = run()
    assert decision is Decision.CLEAR
    assert score == 0
    assert hits == []


def test_watchlist_name_fuzzy_match_triggers_review():
    decision, score, hits = run(originator_name="ivan  PLACEHOLDR")
    assert decision is Decision.REVIEW
    assert score == 70
    assert rule_ids(hits) == ["WATCHLIST_NAME"]


def test_dissimilar_name_does_not_match():
    _, _, hits = run(beneficiary_name="Ivy Holder")
    assert hits == []


def test_high_risk_country_alone_is_below_threshold():
    decision, score, hits = run(beneficiary_country="zz")
    assert decision is Decision.CLEAR
    assert score == 40
    assert rule_ids(hits) == ["HIGH_RISK_COUNTRY"]


def test_same_high_risk_country_on_both_sides_counts_once():
    _, score, _ = run(originator_country="XQ", beneficiary_country="XQ")
    assert score == 40


def test_large_amount_plus_high_risk_country_triggers_review():
    decision, score, hits = run(amount=Decimal("7600.10"), beneficiary_country="XR")
    assert decision is Decision.REVIEW
    assert score == 60
    assert rule_ids(hits) == ["HIGH_RISK_COUNTRY", "LARGE_AMOUNT"]


def test_round_large_amount_stays_clear():
    decision, score, hits = run(amount=Decimal("8000"))
    assert decision is Decision.CLEAR
    assert score == 30
    assert rule_ids(hits) == ["LARGE_AMOUNT", "ROUND_AMOUNT"]


def test_score_is_capped_at_100():
    _, score, _ = run(
        amount=Decimal("9000"),
        beneficiary_name="Globex Front LLC",
        beneficiary_country="XQ",
    )
    assert score == 100
