"""Prompt injection guards — detects and blocks prompt injection attempts (safety, not monetization)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class InjectionRisk(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InjectionCheck:
    """Result of a prompt injection check."""

    risk: InjectionRisk
    blocked: bool
    reasons: list[str]
    sanitized_text: str


_INJECTION_PATTERNS = [
    (re.compile(r"(?i)ignore\s+(all\s+)?previous\s+instructions"), "ignore_previous"),
    (re.compile(r"(?i)system\s*:\s*"), "system_prefix"),
    (re.compile(r"(?i)you\s+are\s+(now\s+)?(no\s+longer\s+)?(a|an)\s+"), "role_override"),
    (re.compile(r"(?i)(dan|jailbreak|bypass|override)\s*(mode|rules|filter)?"), "jailbreak"),
    (re.compile(r"(?i)(act\s+as|pretend\s+to\s+be|roleplay\s+as)\s+"), "role_play"),
    (re.compile(r"(?i)reveal\s+(your\s+)?(system\s+)?(prompt|instructions|rules)"), "prompt_leak"),
    (re.compile(r"(?i)output\s+(your\s+)?(initial|system|original)\s+(prompt|instructions)"), "prompt_leak"),
    (re.compile(r"<\|.*?\|>"), "delimiter_abuse"),
    (re.compile(r"(?i)do\s+not\s+(follow|obey|adhere\s+to)\s+(the\s+)?(rules|guidelines|policy)"), "rule_override"),
    (re.compile(r"(?i)(new\s+)?instructions?\s*[:：]"), "instruction_injection"),
]

_PII_PATTERNS = [
    (re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"), "credit_card"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "email"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "ssn"),
]


def check_prompt_injection(text: str) -> InjectionCheck:
    """Check if a prompt contains injection attempts."""
    reasons = []
    risk_score = 0

    for pattern, reason in _INJECTION_PATTERNS:
        if pattern.search(text):
            reasons.append(reason)
            risk_score += 2

    if risk_score >= 4:
        risk = InjectionRisk.CRITICAL
    elif risk_score >= 2:
        risk = InjectionRisk.HIGH
    elif risk_score >= 1:
        risk = InjectionRisk.MEDIUM
    else:
        risk = InjectionRisk.SAFE

    blocked = risk in (InjectionRisk.MEDIUM, InjectionRisk.HIGH, InjectionRisk.CRITICAL)

    if blocked:
        logger.warning(
            "prompt_injection.blocked",
            risk=risk.value,
            reasons=reasons,
        )
    elif reasons:
        logger.info(
            "prompt_injection.flagged",
            risk=risk.value,
            reasons=reasons,
        )

    return InjectionCheck(
        risk=risk,
        blocked=blocked,
        reasons=reasons,
        sanitized_text=text if not blocked else "[Prompt blocked by safety filter]",
    )


def sanitize_pii(text: str) -> tuple[str, list[str]]:
    """Detect and mask PII in text. Returns sanitized text and list of detected types."""
    detected = []
    sanitized = text

    for pattern, pii_type in _PII_PATTERNS:
        if pattern.search(sanitized):
            detected.append(pii_type)
            sanitized = pattern.sub(f"[{pii_type}_REDACTED]", sanitized)

    return sanitized, detected


def is_safe_prompt(text: str) -> bool:
    """Quick check if a prompt is safe to process."""
    result = check_prompt_injection(text)
    return not result.blocked
