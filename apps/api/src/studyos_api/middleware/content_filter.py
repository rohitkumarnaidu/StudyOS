"""Content filter middleware — ensures AI output is safe and appropriate."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class ContentFlag(str, Enum):
    SAFE = "safe"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass
class ContentFilterResult:
    """Result of content filtering."""

    flag: ContentFlag
    blocked: bool
    flags: list[str]
    filtered_text: str


_PROHIBITED_PATTERNS = [
    (re.compile(r"(?i)\b(hate\s+speech|kill\s+yourself|go\s+die)\b"), "harmful"),
    (re.compile(r"(?i)\b(self.harm|suicide\s+method)\b"), "self_harm"),
    (re.compile(r"(?i)\b(illegal\s+drug|how\s+to\s+make\s+bomb)\b"), "illegal"),
    (re.compile(r"(?i)\b(explicit\s+content|nsfw|porn)\b"), "explicit"),
    (re.compile(r"(?i)\b(doxx|reveal\s+address|stalking)\b"), "harassment"),
]

_QUALITY_PATTERNS = [
    (re.compile(r"(?i)\b(i\s+cannot|as\s+an\s+ai|i'm\s+sorry|unfortunately)\b"), "refusal"),
    (re.compile(r"(?i)\b(i\s+don't\s+have|no\s+information|cannot\s+access)\b"), "no_knowledge"),
    (re.compile(r"\.{3,}"), "trailing_ellipsis"),
    (re.compile(r"(.)\1{4,}"), "repetitive"),
]


def filter_content(text: str) -> ContentFilterResult:
    """Filter AI output for harmful or low-quality content."""
    flags = []
    severity = 0
    has_prohibited = False

    for pattern, flag_type in _PROHIBITED_PATTERNS:
        if pattern.search(text):
            flags.append(flag_type)
            severity += 3
            has_prohibited = True

    for pattern, flag_type in _QUALITY_PATTERNS:
        if pattern.search(text):
            flags.append(flag_type)
            severity += 1

    if severity >= 6:
        flag = ContentFlag.SEVERE
    elif severity >= 3:
        flag = ContentFlag.MODERATE
    elif has_prohibited:
        flag = ContentFlag.MILD
    else:
        flag = ContentFlag.SAFE

    blocked = has_prohibited

    if blocked:
        logger.warning(
            "content_filter.blocked",
            flag=flag.value,
            flags=flags,
        )
        return ContentFilterResult(
            flag=flag,
            blocked=True,
            flags=flags,
            filtered_text="[Content filtered for safety]",
        )

    return ContentFilterResult(
        flag=flag,
        blocked=False,
        flags=flags,
        filtered_text=text,
    )


def is_safe_content(text: str) -> bool:
    """Quick check if content is safe to return to user."""
    return not filter_content(text).blocked
