from collections import defaultdict
from .normalize import norm_name, norm_domain


def block_keys(record: dict) -> list[str]:
    """Return all block keys this record belongs to. A record can be in multiple blocks."""
    keys: list[str] = []
    n = norm_name(record.get("name", ""))
    if n:
        keys.append(f"name:{n[:4]}")  # first 4 chars of normalized name
    d = norm_domain(record.get("website", "") or record.get("domain", ""))
    if d:
        keys.append(f"dom:{d.split('.')[0]}")
    return keys


def build_blocks(records: list[dict]) -> dict[str, list[int]]:
    blocks: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(records):
        for k in block_keys(r):
            blocks[k].append(i)
    return blocks
