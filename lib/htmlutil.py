"""Gemeinsame HTML-Helfer für die Specialists."""
from __future__ import annotations

import re
from bs4 import BeautifulSoup


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def meta_content(s: BeautifulSoup, name: str) -> str | None:
    tag = s.find("meta", attrs={"name": name}) or s.find("meta", attrs={"property": name})
    return (tag.get("content") or "").strip() if tag else None


def title_text(s: BeautifulSoup) -> str:
    tag = s.find("title")
    return (tag.get_text() or "").strip() if tag else ""


def h1s(s: BeautifulSoup) -> list:
    return [h.get_text(strip=True) for h in s.find_all("h1")]


def heading_counts(s: BeautifulSoup) -> dict:
    return {f"h{i}": len(s.find_all(f"h{i}")) for i in range(1, 7)}


def link_attr(tag, attr: str) -> str:
    return (tag.get(attr) or "").strip()


_WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß\-']{2,}")


def words(text: str) -> list:
    return _WORD_RE.findall(text or "")


STOPWORDS = set(
    """der die das und oder aber nicht ein eine ist sind für mit auf im zu den dem des
    von bei nach über unter auch als wie sich ich wir sie es er so nur noch wenn dann
    the and or but not for with that this from are was have has had you your we our
    their they them will would can could should about into over under more most than
    zur zum im am um bei beim seit sowie bzw""".split()
)


def top_terms(text: str, top_n: int = 15) -> list:
    from collections import Counter

    toks = [w.lower() for w in words(text) if w.lower() not in STOPWORDS and len(w) > 2]
    return [w for w, _ in Counter(toks).most_common(top_n)]


def phone_numbers(text: str) -> list:
    patterns = [
        r"\+?\d{1,4}[\s\-./]?(?:\(\d{1,5}\)[\s\-./]?)?\d{2,5}[\s\-./]?\d{2,5}[\s\-./]?\d{0,5}",
    ]
    out = set()
    for pat in patterns:
        for m in re.findall(pat, text):
            if len(re.sub(r"\D", "", m)) >= 8:
                out.add(m.strip())
    return sorted(out)[:10]


def email_addresses(text: str) -> list:
    return sorted(set(re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)))[:10]


def postal_address(text: str) -> list:
    pat = r"\b\d{4,5}\s+[A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß\-]+)*"
    return sorted(set(re.findall(pat, text)))[:10]
