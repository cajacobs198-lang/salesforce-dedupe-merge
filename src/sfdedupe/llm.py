import os
import json
from typing import Optional

_PROMPT = """You are reviewing two Salesforce account records to decide if they
represent the same company. Answer with JSON only:
{{"same_company": true|false, "confidence": 0-1, "reason": "one sentence"}}

RECORD A:
{a}

RECORD B:
{b}
"""


def tiebreak(a: dict, b: dict, classify_fn=None) -> Optional[dict]:
    fn = classify_fn or _real_classify
    return fn(a, b)


def _real_classify(a: dict, b: dict) -> Optional[dict]:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    from anthropic import Anthropic  # noqa: WPS433
    client = Anthropic()
    msg = client.messages.create(
        model=os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=200,
        messages=[{"role": "user", "content": _PROMPT.format(a=json.dumps(a), b=json.dumps(b))}],
    )
    text = msg.content[0].text.strip()
    s, e = text.find("{"), text.rfind("}")
    try:
        return json.loads(text[s:e + 1])
    except Exception:
        return None
