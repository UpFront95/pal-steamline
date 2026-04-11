"""
Tests that reproduce and prevent provider routing bugs.

These tests specifically cover bugs that were found in production:
1. Fallback provider registration bypassing API key validation
2. OpenRouter alias-based restrictions not working
3. Double restriction filtering
4. Missing provider_used metadata
"""

import os
from unittest.mock import Mock

import pytest

from providers.registry import ModelProviderRegistry
from providers.shared import ProviderType
from tools.chat import ChatTool
from tools.shared.base_models import ToolRequest


class MockRequest(ToolRequest):
    """Mock request for testing."""

    pass


class TestProviderRoutingBugs:
    """Test cases that reproduce provider routing bugs."""

    def setup_method(self):
        """Set up clean state before each test."""
        # Clear restriction service cache
        import utils.model_restrictions

        utils.model_restrictions._restriction_service = None

        # Clear provider registry
        registry = ModelProviderRegistry()
        registry._providers.clear()
        registry._initialized_providers.clear()

    def teardown_method(self):
        """Clean up after each test."""
        # Clear restriction service cache
        import utils.model_restrictions

        utils.model_restrictions._restriction_service = None

    @pytest.mark.no_mock_provider
    def test_fallback_should_not_register_without_api_key(self):
        """
        Test that fallback logic correctly validates API keys before registering providers.

        This test ensures the fix in tools/base.py:2067-2081 works correctly.
        """
        # Save original environment
        original_env = {}
        for key in [
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "XAI_API_KEY",
            "OPENROUTER_API_KEY",
            "OPENROUTER_ALLOWED_MODELS",
        ]:
            original_env[key] = os.environ.get(key)

        try:
            # Set up scenario: NO API keys at all
            for key in [
                "GEMINI_API_KEY",
                "OPENAI_API_KEY",
                "XAI_API_KEY",
                "OPENROUTER_API_KEY",
                "OPENROUTER_ALLOWED_MODELS",
            ]:
                os.environ.pop(key, None)

            # Create tool to test fallback logic
            tool = ChatTool()

            # Test: Request 'flash' model with no API keys - should fail gracefully
            with pytest.raises(ValueError, match="Model 'flash' is not available"):
                tool.get_model_provider("flash")

            # Test: Request 'o3' model with no API keys - should fail gracefully
            with pytest.raises(ValueError, match="Model 'o3' is not available"):
                tool.get_model_provider("o3")

            # Verify no providers were auto-registered
            registry = ModelProviderRegistry()
            assert len(registry._providers) == 0, "No providers should be registered without API keys"

        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    @pytest.mark.no_mock_provider
    def test_mixed_api_keys_correct_routing(self):
        """
        Test that when multiple API keys are available, provider routing works correctly.
        """
        # Save original environment
        original_env = {}
        for key in [
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "XAI_API_KEY",
            "OPENROUTER_API_KEY",
            "OPENROUTER_ALLOWED_MODELS",
        ]:
            original_env[key] = os.environ.get(key)

        try:
            # Set up scenario: Multiple API keys available
            os.environ["GEMINI_API_KEY"] = "test-gemini-key"
            os.environ["OPENAI_API_KEY"] = "test-openai-key"
            os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
            os.environ.pop("XAI_API_KEY", None)
            os.environ.pop("OPENROUTER_ALLOWED_MODELS", None)  # Clear any restrictions

            # Register providers in priority order (like server.py)
            from providers.gemini import GeminiModelProvider
            from providers.openai import OpenAIModelProvider
            from providers.openrouter import OpenRouterProvider

            ModelProviderRegistry.register_provider(ProviderType.GOOGLE, GeminiModelProvider)
            ModelProviderRegistry.register_provider(ProviderType.OPENAI, OpenAIModelProvider)
            ModelProviderRegistry.register_provider(ProviderType.OPENROUTER, OpenRouterProvider)

            tool = ChatTool()

            # Test priority order: Native APIs should be preferred over OpenRouter
            # Google models should use Google provider
            flash_provider = tool.get_model_provider("flash")
            assert (
                flash_provider.get_provider_type() == ProviderType.GOOGLE
            ), "When both Google and OpenRouter API keys are available, 'flash' should prefer Google provider"

            # OpenAI models should use OpenAI provider
            o3_provider = tool.get_model_provider("o3")
            assert (
                o3_provider.get_provider_type() == ProviderType.OPENAI
            ), "When both OpenAI and OpenRouter API keys are available, 'o3' should prefer OpenAI provider"

        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class TestProviderMetadataBug:
    """Test for missing provider_used metadata bug."""

    def test_provider_used_metadata_included(self):
        """
        Test that provider_used metadata is included in tool responses.

        Bug: Only model_used was included, provider_used was missing.
        Fix: Added provider_used field in tools/base.py
        """
        # Test the actual _parse_response method with model_info
        tool = ChatTool()

        # Create mock provider
        mock_provider = Mock()
        mock_provider.get_provider_type.return_value = ProviderType.OPENROUTER

        # Create model_info like the execute method does
        model_info = {"provider": mock_provider, "model_name": "test-model", "model_response": Mock()}

        # Test _parse_response directly with a simple response
        request = MockRequest()
        result = tool._parse_response("Test response", request, model_info)

        # Verify metadata includes both model_used and provider_used
        assert hasattr(result, "metadata"), "ToolOutput should have metadata"
        assert result.metadata is not None, "Metadata should not be None"
        assert "model_used" in result.metadata, "Metadata should include model_used"
        assert result.metadata["model_used"] == "test-model", "model_used should be correct"
        assert "provider_used" in result.metadata, "Metadata should include provider_used (bug fix)"
        assert result.metadata["provider_used"] == "openrouter", "provider_used should be correct"
