"""
Communication Simulator Tests Package

This package contains individual test modules for the PAL MCP Communication Simulator.
Each test is in its own file for better organization and maintainability.
"""

from .base_test import BaseSimulatorTest
from .test_basic_conversation import BasicConversationTest
from .test_codereview_validation import CodeReviewValidationTest
from .test_consensus_conversation import TestConsensusConversation
from .test_consensus_workflow_accurate import TestConsensusWorkflowAccurate
from .test_content_validation import ContentValidationTest
from .test_conversation_chain_validation import ConversationChainValidationTest
from .test_cross_tool_continuation import CrossToolContinuationTest
from .test_openrouter_models import OpenRouterModelsTest
from .test_prompt_size_limit_bug import PromptSizeLimitBugTest
from .test_thinkdeep_validation import ThinkDeepWorkflowValidationTest
from .test_token_allocation_validation import TokenAllocationValidationTest

# Test registry for dynamic loading
TEST_REGISTRY = {
    "basic_conversation": BasicConversationTest,
    "codereview_validation": CodeReviewValidationTest,
    "content_validation": ContentValidationTest,
    "cross_tool_continuation": CrossToolContinuationTest,
    "token_allocation_validation": TokenAllocationValidationTest,
    "thinkdeep_validation": ThinkDeepWorkflowValidationTest,
    "conversation_chain_validation": ConversationChainValidationTest,
    "consensus_conversation": TestConsensusConversation,
    "consensus_workflow_accurate": TestConsensusWorkflowAccurate,
    "openrouter_models": OpenRouterModelsTest,
    "prompt_size_limit_bug": PromptSizeLimitBugTest,
}

__all__ = [
    "BaseSimulatorTest",
    "BasicConversationTest",
    "CodeReviewValidationTest",
    "ContentValidationTest",
    "CrossToolContinuationTest",
    "TokenAllocationValidationTest",
    "ThinkDeepWorkflowValidationTest",
    "ConversationChainValidationTest",
    "TestConsensusConversation",
    "TestConsensusWorkflowAccurate",
    "OpenRouterModelsTest",
    "PromptSizeLimitBugTest",
    "TEST_REGISTRY",
]
