from sfdedupe.score import score_pair, score_blocks
from sfdedupe.block import build_blocks


def test_score_pair_high_for_obvious_duplicate():
    a = {"id": "1", "name": "Acme Inc", "website": "acme.com"}
    b = {"id": "2", "name": "Acme, Inc.", "website": "www.acme.com"}
    p = score_pair(a, b)
    assert p.domain_match is True
    assert p.score >= 95


def test_score_pair_low_for_unrelated():
    a = {"id": "1", "name": "Acme Inc", "website": "acme.com"}
    b = {"id": "2", "name": "Wayne Industries", "website": "wayne.com"}
    p = score_pair(a, b)
    assert p.score < 50


def test_blocks_reduce_pair_count():
    records = [
        {"id": "1", "name": "Acme Inc", "website": "acme.com"},
        {"id": "2", "name": "Acme Co", "website": "acme.com"},
        {"id": "3", "name": "Stripe", "website": "stripe.com"},
        {"id": "4", "name": "Stripe Inc", "website": "stripe.com"},
    ]
    blocks = build_blocks(records)
    pairs = score_blocks(records, blocks)
    pair_ids = {tuple(sorted((p.a_id, p.b_id))) for p in pairs}
    # cross-cluster pairs should be excluded by blocking
    assert ("1", "3") not in pair_ids
    assert ("1", "2") in pair_ids
    assert ("3", "4") in pair_ids
