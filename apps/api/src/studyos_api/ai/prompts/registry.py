"""Named prompts — swap templates via DB or files without changing provider code."""

from __future__ import annotations

from studyos_api.ai.prompts import builtins

_default_registry: PromptRegistry | None = None


class PromptRegistry:
    def __init__(self, templates: dict[str, str]) -> None:
        self._templates = dict(templates)

    @classmethod
    def default(cls) -> PromptRegistry:
        """Process-wide singleton — avoids rebuilding default templates on every AI request."""
        global _default_registry
        if _default_registry is None:
            _default_registry = cls(dict(builtins.DEFAULT_PROMPTS))
        return _default_registry

    def register(self, prompt_id: str, template: str) -> None:
        self._templates[prompt_id] = template

    def render(self, prompt_id: str, **variables: str) -> str:
        tmpl = self._templates.get(prompt_id)
        if tmpl is None:
            msg = f"Unknown prompt_id: {prompt_id}"
            raise KeyError(msg)
        try:
            return tmpl.format(**variables)
        except KeyError as exc:
            msg = f"Missing template variable for {prompt_id}: {exc}"
            raise KeyError(msg) from exc
