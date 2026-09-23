"""Explainable, offline-first phishing triage heuristics.

This module deliberately does not fetch URLs or execute content. It extracts
signals from user-supplied text and produces a transparent risk score that a
human analyst can review.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from html import unescape
import ipaddress
import re
from typing import Iterable
from urllib.parse import parse_qs, urlparse


MAX_INPUT_LENGTH = 50_000
SUSPICIOUS_TLDS = {".zip", ".mov", ".top", ".click", ".work", ".gq", ".tk", ".xyz"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly", "rb.gy"}
URGENCY_TERMS = {"urgent", "immediately", "act now", "verify", "suspended", "expired", "within 24 hours"}
REQUEST_TERMS = {"password", "otp", "one-time code", "login", "credentials", "payment", "gift card", "wire transfer"}
URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>\"']+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


@dataclass(frozen=True)
class Finding:
    code: str
    title: str
    detail: str
    severity: str
    points: int


@dataclass(frozen=True)
class Analysis:
    score: int
    verdict: str
    confidence: str
    urls: list[str]
    findings: list[Finding]
    recommendations: list[str]

    def to_dict(self) -> dict:
        result = asdict(self)
        result["findings"] = [asdict(item) for item in self.findings]
        return result


def _clean(value: str) -> str:
    value = unescape(value or "")
    return value[:MAX_INPUT_LENGTH]


def extract_urls(text: str) -> list[str]:
    """Extract de-duplicated candidate URLs without making network requests."""
    found: list[str] = []
    for raw in URL_RE.findall(_clean(text)):
        candidate = raw.rstrip(".,;:!?)\"]")
        if candidate.lower().startswith("www."):
            candidate = "http://" + candidate
        if candidate not in found:
            found.append(candidate)
    return found


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False


def analyze(text: str) -> Analysis:
    """Return a bounded, explainable risk assessment for email or URL text."""
    content = _clean(text)
    lower = content.lower()
    findings: list[Finding] = []

    def add(code: str, title: str, detail: str, severity: str, points: int) -> None:
        findings.append(Finding(code, title, detail, severity, points))

    urls = extract_urls(content)
    if not urls:
        add("NO_URL", "No URL found", "No web link was available for URL-specific checks.", "info", 0)

    for url in urls:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme != "https":
            add("PLAIN_HTTP", "Unencrypted link", f"{host or url} uses HTTP instead of HTTPS.", "medium", 12)
        if _is_ip(host):
            add("IP_HOST", "IP-address host", f"The link points directly to {host}, which is uncommon for trusted sign-in pages.", "high", 25)
        if "@" in parsed.netloc:
            add("AT_SYMBOL", "Username in URL", "An @ symbol can hide the true destination after the host delimiter.", "high", 25)
        if len(url) > 120:
            add("LONG_URL", "Unusually long URL", "Long links can conceal tracking or redirect parameters.", "low", 6)
        if host in SHORTENERS:
            add("SHORTENER", "URL shortener", f"{host} hides the final destination and should be expanded safely before visiting.", "medium", 15)
        if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
            add("SUSPICIOUS_TLD", "Higher-risk top-level domain", f"{host} uses a top-level domain frequently seen in abuse reports.", "medium", 10)
        labels = host.split(".") if host else []
        if len(labels) >= 4:
            add("MANY_SUBDOMAINS", "Many subdomains", "Several subdomain levels can make a brand impersonation harder to notice.", "low", 7)
        if any(term in host for term in ("login", "verify", "secure", "account", "update", "microsoft", "paypal", "google")):
            add("BRAND_WORD", "Brand or login wording in host", "The hostname contains account or brand wording that deserves independent verification.", "low", 6)
        query_keys = {key.lower() for key in parse_qs(parsed.query).keys()}
        if query_keys & {"token", "session", "auth", "password", "redirect", "url", "next"}:
            add("SENSITIVE_QUERY", "Sensitive or redirect parameter", "The URL carries a token, authentication, or redirect-like parameter.", "medium", 12)

    urgency_hits = sorted(term for term in URGENCY_TERMS if term in lower)
    if urgency_hits:
        add("URGENCY", "Urgency or threat language", f"Detected pressure terms: {', '.join(urgency_hits)}.", "medium", 12)
    request_hits = sorted(term for term in REQUEST_TERMS if term in lower)
    if request_hits:
        add("SENSITIVE_REQUEST", "Sensitive action requested", f"Detected requests involving: {', '.join(request_hits)}.", "high", 18)
    if len(EMAIL_RE.findall(content)) >= 2 and any(word in lower for word in ("from", "reply", "sender")):
        add("MULTIPLE_EMAILS", "Multiple sender addresses", "Several addresses appear in the message; compare the display name with the real domain.", "low", 5)
    if re.search(r"(?i)\b(attachment|invoice|receipt)\b", content) and re.search(r"(?i)\.(?:exe|scr|js|vbs|iso|zip)\b", content):
        add("RISKY_ATTACHMENT", "Potentially risky attachment", "The text mentions an attachment type that can execute or hide content.", "high", 20)

    score = min(100, sum(item.points for item in findings))
    if score >= 60:
        verdict, confidence = "High risk", "High"
    elif score >= 30:
        verdict, confidence = "Needs review", "Medium"
    else:
        verdict, confidence = "Low risk", "Low"

    recommendations = _recommendations(findings, urls)
    return Analysis(score, verdict, confidence, urls, findings, recommendations)


def _recommendations(findings: Iterable[Finding], urls: list[str]) -> list[str]:
    codes = {item.code for item in findings}
    result = ["Do not click or submit credentials until the sender and destination are verified through a separate channel."]
    if urls:
        result.append("Open the organization’s known website manually instead of following the supplied link.")
    if {"SENSITIVE_REQUEST", "URGENCY"} <= codes:
        result.append("Treat urgency plus a request for secrets or money as a social-engineering pattern.")
    if "RISKY_ATTACHMENT" in codes:
        result.append("Do not open the attachment; submit it to your security team or a sandbox for analysis.")
    if "PLAIN_HTTP" in codes or "IP_HOST" in codes:
        result.append("Escalate the link for investigation and preserve the original message headers if available.")
    result.append("Record the evidence and analyst decision so future detections can be improved.")
    return result


__all__ = ["Analysis", "Finding", "MAX_INPUT_LENGTH", "analyze", "extract_urls"]
