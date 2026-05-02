from dataclasses import dataclass
from rapidfuzz import fuzz
from .normalize import norm_name, norm_domain


@dataclass
class PairScore:
    a_id: str
    b_id: str
    name_score: int
    domain_match: bool
    score: int  # composite 0-100


def score_pair(a: dict, b: dict) -> PairScore:
    name_s = fuzz.token_set_ratio(norm_name(a.get("name", "")), norm_name(b.get("name", "")))
    d_a, d_b = norm_domain(a.get("website", "")), norm_domain(b.get("website", ""))
    domain_match = bool(d_a and d_b and d_a == d_b)
    composite = name_s + (10 if domain_match else 0)
    composite = min(composite, 100)
    return PairScore(a_id=a["id"], b_id=b["id"], name_score=name_s,
                     domain_match=domain_match, score=composite)


def score_blocks(records: list[dict], blocks: dict[str, list[int]]) -> list[PairScore]:
    seen: set[tuple[str, str]] = set()
    out: list[PairScore] = []
    for _, idxs in blocks.items():
        if len(idxs) < 2:
            continue
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                a, b = records[idxs[i]], records[idxs[j]]
                if a["id"] == b["id"]:
                    continue
                key = tuple(sorted((a["id"], b["id"])))
                if key in seen:
                    continue
                seen.add(key)
                out.append(score_pair(a, b))
    return out
