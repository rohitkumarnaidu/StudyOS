"""Tests for AI provider factory."""

from unittest.mock import MagicMock

import pytest

from studyos_api.ai.provider_factory import build_llm_chain


class TestBuildLLMChain:
    @pytest.fixture
    def mock_http_client(self):
        return MagicMock()

    def test_build_chain_ollama_only(self, mock_http_client):
        settings = MagicMock()
        settings.ai_ollama_base_url = "http://localhost:11434"
        settings.ai_default_model_ollama = "llama3"
        settings.ai_openai_api_key = None
        settings.ai_anthropic_api_key = None
        settings.ai_primary_provider = "ollama"
        settings.ai_fallback_provider_ids = []

        chain = build_llm_chain(settings, mock_http_client)
        assert len(chain) == 1
        assert chain[0].__class__.__name__ == "OllamaProvider"

    def test_build_chain_with_openai(self, mock_http_client):
        settings = MagicMock()
        settings.ai_ollama_base_url = "http://localhost:11434"
        settings.ai_default_model_ollama = "llama3"
        settings.ai_openai_api_key = "sk-test"
        settings.ai_openai_base_url = "https://api.openai.com/v1"
        settings.ai_default_model_openai = "gpt-4"
        settings.ai_anthropic_api_key = None
        settings.ai_primary_provider = "openai"
        settings.ai_fallback_provider_ids = ["ollama"]

        chain = build_llm_chain(settings, mock_http_client)
        assert len(chain) == 2
        assert chain[0].__class__.__name__ == "OpenAIProvider"
        assert chain[1].__class__.__name__ == "OllamaProvider"

    def test_build_chain_with_anthropic(self, mock_http_client):
        settings = MagicMock()
        settings.ai_ollama_base_url = "http://localhost:11434"
        settings.ai_default_model_ollama = "llama3"
        settings.ai_openai_api_key = None
        settings.ai_anthropic_api_key = "sk-ant-test"
        settings.ai_anthropic_base_url = "https://api.anthropic.com"
        settings.ai_default_model_anthropic = "claude-3"
        settings.ai_primary_provider = "anthropic"
        settings.ai_fallback_provider_ids = ["ollama"]

        chain = build_llm_chain(settings, mock_http_client)
        assert len(chain) == 2
        assert chain[0].__class__.__name__ == "AnthropicProvider"

    def test_build_chain_all_providers(self, mock_http_client):
        settings = MagicMock()
        settings.ai_ollama_base_url = "http://localhost:11434"
        settings.ai_default_model_ollama = "llama3"
        settings.ai_openai_api_key = "sk-test"
        settings.ai_openai_base_url = "https://api.openai.com/v1"
        settings.ai_default_model_openai = "gpt-4"
        settings.ai_anthropic_api_key = "sk-ant-test"
        settings.ai_anthropic_base_url = "https://api.anthropic.com"
        settings.ai_default_model_anthropic = "claude-3"
        settings.ai_primary_provider = "ollama"
        settings.ai_fallback_provider_ids = ["openai", "anthropic"]

        chain = build_llm_chain(settings, mock_http_client)
        assert len(chain) == 3

    def test_build_chain_invalid_primary(self, mock_http_client):
        settings = MagicMock()
        settings.ai_ollama_base_url = "http://localhost:11434"
        settings.ai_default_model_ollama = "llama3"
        settings.ai_openai_api_key = None
        settings.ai_anthropic_api_key = None
        settings.ai_primary_provider = "invalid"
        settings.ai_fallback_provider_ids = []

        chain = build_llm_chain(settings, mock_http_client)
        assert len(chain) == 1
        assert chain[0].__class__.__name__ == "OllamaProvider"

    def test_build_chain_empty_fallback(self, mock_http_client):
        settings = MagicMock()
        settings.ai_ollama_base_url = "http://localhost:11434"
        settings.ai_default_model_ollama = "llama3"
        settings.ai_openai_api_key = "sk-test"
        settings.ai_openai_base_url = "https://api.openai.com/v1"
        settings.ai_default_model_openai = "gpt-4"
        settings.ai_anthropic_api_key = None
        settings.ai_primary_provider = "openai"
        settings.ai_fallback_provider_ids = ["nonexistent"]

        chain = build_llm_chain(settings, mock_http_client)
        assert len(chain) == 1
