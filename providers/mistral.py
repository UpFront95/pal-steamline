"""Mistral model provider implementation."""

import logging
from typing import TYPE_CHECKING, ClassVar, Optional

if TYPE_CHECKING:
    pass

from .openai_compatible import OpenAICompatibleProvider
from .registries.mistral import MistralModelRegistry
from .registry_provider_mixin import RegistryBackedProviderMixin
from .shared import ModelCapabilities, ProviderType

logger = logging.getLogger(__name__)


class MistralModelProvider(RegistryBackedProviderMixin, OpenAICompatibleProvider):
    """Integration for Mistral models exposed over an OpenAI-compatible API.

    Publishes capability metadata for the officially supported deployments and
    maps tool-category preferences to the appropriate Mistral model.
    """

    FRIENDLY_NAME = "Mistral"

    REGISTRY_CLASS = MistralModelRegistry
    MODEL_CAPABILITIES: ClassVar[dict[str, ModelCapabilities]] = {}

    PRIMARY_MODEL = "mistral-large-latest"
    FALLBACK_MODEL = "mistral-large-latest"

    def __init__(self, api_key: str, **kwargs):
        """Initialize Mistral provider with API key."""
        kwargs.setdefault("base_url", "https://api.mistral.ai/v1")
        self._ensure_registry()
        super().__init__(api_key, **kwargs)
        self._invalidate_capability_cache()

    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.MISTRAL


# Load registry data at import time
MistralModelProvider._ensure_registry()
