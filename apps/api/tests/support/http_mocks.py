"""Outbound HTTP mocks (Ollama, OpenAI, …) using `respx`.

See https://lundberg.github.io/respx/ — prefer `@respx.mock` on tests that patch
provider base URLs from `get_settings()`.
"""
