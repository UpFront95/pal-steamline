"""
System prompts for Gemini tools
"""

from .chat_prompt import CHAT_PROMPT
from .codereview_prompt import CODEREVIEW_PROMPT
from .consensus_prompt import CONSENSUS_PROMPT
from .debug_prompt import DEBUG_ISSUE_PROMPT
from .generate_code_prompt import GENERATE_CODE_PROMPT
from .refactor_prompt import REFACTOR_PROMPT
from .thinkdeep_prompt import THINKDEEP_PROMPT

__all__ = [
    "THINKDEEP_PROMPT",
    "CODEREVIEW_PROMPT",
    "DEBUG_ISSUE_PROMPT",
    "GENERATE_CODE_PROMPT",
    "CHAT_PROMPT",
    "CONSENSUS_PROMPT",
    "REFACTOR_PROMPT",
]
