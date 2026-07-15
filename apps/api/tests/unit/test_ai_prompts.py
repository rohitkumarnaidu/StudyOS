"""Tests for AI prompt registry and built-in templates."""

import pytest

from studyos_api.ai.prompts.builtins import DEFAULT_PROMPTS
from studyos_api.ai.prompts.registry import PromptRegistry


class TestPromptRegistry:
    def test_default_has_builtin_prompts(self) -> None:
        registry = PromptRegistry.default()
        assert "tutor.system.v1" in registry._templates
        assert "router.system.v1" in registry._templates

    def test_default_is_singleton(self) -> None:
        r1 = PromptRegistry.default()
        r2 = PromptRegistry.default()
        assert r1 is r2

    def test_render_simple_prompt(self) -> None:
        registry = PromptRegistry({"greet.v1": "Hello, {name}!"})
        result = registry.render("greet.v1", name="Student")
        assert result == "Hello, Student!"

    def test_render_prompt_with_multiple_variables(self) -> None:
        registry = PromptRegistry({"explain.v1": "Explain {topic} to a {level} student."})
        result = registry.render("explain.v1", topic="Physics", level="beginner")
        assert result == "Explain Physics to a beginner student."

    def test_render_unknown_prompt_raises(self) -> None:
        registry = PromptRegistry({})
        with pytest.raises(KeyError, match="Unknown prompt_id"):
            registry.render("nonexistent")

    def test_render_missing_variable_raises(self) -> None:
        registry = PromptRegistry({"test.v1": "Hello {name} from {city}"})
        with pytest.raises(KeyError, match="Missing template variable"):
            registry.render("test.v1", name="Student")

    def test_register_new_prompt(self) -> None:
        registry = PromptRegistry({})
        registry.register("custom.v1", "Custom prompt: {value}")
        result = registry.render("custom.v1", value="test")
        assert result == "Custom prompt: test"

    def test_register_overwrites_existing(self) -> None:
        registry = PromptRegistry({"greet.v1": "Hello"})
        registry.register("greet.v1", "Hi there")
        assert registry.render("greet.v1") == "Hi there"

    def test_default_prompts_content(self) -> None:
        assert "StudyOS" in DEFAULT_PROMPTS["tutor.system.v1"]
        assert "NEET" in DEFAULT_PROMPTS["tutor.system.v1"]
        assert "JSON" in DEFAULT_PROMPTS["router.system.v1"]

    def test_render_tutor_prompt(self) -> None:
        registry = PromptRegistry.default()
        result = registry.render("tutor.system.v1", context="Chapter on optics")
        assert "Chapter on optics" in result
        assert "StudyOS" in result

    def test_render_router_prompt(self) -> None:
        registry = PromptRegistry.default()
        result = registry.render("router.system.v1", topic="Chemistry")
        assert "Chemistry" in result
        assert "JSON" in result
