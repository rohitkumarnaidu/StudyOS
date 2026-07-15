"""Tests for content filter middleware."""

import pytest

from studyos_api.middleware.content_filter import (
    ContentFilterResult,
    ContentFlag,
    filter_content,
    is_safe_content,
)


class TestContentFilter:
    def test_safe_content(self) -> None:
        result = filter_content("Photosynthesis is the process by which plants convert sunlight into energy.")
        assert result.flag == ContentFlag.SAFE
        assert result.blocked is False
        assert result.flags == []

    def test_harmful_content_blocked(self) -> None:
        result = filter_content("You should hate speech and go die")
        assert result.blocked is True
        assert "harmful" in result.flags

    def test_self_harm_blocked(self) -> None:
        result = filter_content("Here are self-harm methods")
        assert result.blocked is True
        assert "self_harm" in result.flags

    def test_illegal_content_blocked(self) -> None:
        result = filter_content("How to make bomb and illegal drug")
        assert result.blocked is True

    def test_explicit_content_blocked(self) -> None:
        result = filter_content("This is explicit content nsfw")
        assert result.blocked is True

    def test_harassment_blocked(self) -> None:
        result = filter_content("Let's doxx this person and reveal their address")
        assert result.blocked is True

    def test_refusal_flagged_not_blocked(self) -> None:
        result = filter_content("I'm sorry, I cannot help with that")
        assert result.blocked is False
        assert "refusal" in result.flags

    def test_no_knowledge_flagged_not_blocked(self) -> None:
        result = filter_content("I don't have information about that topic")
        assert result.blocked is False
        assert "no_knowledge" in result.flags

    def test_repetitive_flagged(self) -> None:
        result = filter_content("aaaaabbbbbccccc")
        assert result.blocked is False
        assert "repetitive" in result.flags

    def test_filtered_text_replacement(self) -> None:
        result = filter_content("This is hate speech content")
        assert result.filtered_text == "[Content filtered for safety]"

    def test_safe_content_passes(self) -> None:
        assert is_safe_content("The mitochondria is the powerhouse of the cell") is True

    def test_unsafe_content_fails(self) -> None:
        assert is_safe_content("go die and kill yourself") is False
