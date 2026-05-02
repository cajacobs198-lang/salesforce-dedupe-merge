import re
import tldextract

_STOPWORDS = (" inc", " llc", " ltd", " gmbh", " sa", " co", " corp", " corporation", " the ")
_NON_ALNUM = re.compile(r"[^a-z0-9 ]")
_WHITESPACE = re.compile(r"\s+")


def norm_name(name: str) -> str:
    n = (name or "").lower()
    for s in _STOPWORDS:
        n = n.replace(s, " ")
    n = _NON_ALNUM.sub(" ", n)
    n = _WHITESPACE.sub(" ", n).strip()
    return n


def norm_domain(domain: str) -> str:
    if not domain:
        return ""
    ext = tldextract.extract(domain.strip().lower())
    if not ext.domain or not ext.suffix:
        return domain.strip().lower()
    return f"{ext.domain}.{ext.suffix}"
