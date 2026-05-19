"""
Integration test demonstrating that all tools get line numbers by default.
"""

from tools.chat import ChatTool
from tools.codereview import CodeReviewTool
from tools.codereview import CodeReviewTool


class TestLineNumbersIntegration:
    """Test that all tools inherit line number behavior correctly."""

    def test_all_tools_want_line_numbers(self):
        """Verify that all tools want line numbers by default."""
        tools = [
            ChatTool(),
            CodeReviewTool(),
            CodeReviewTool(),
        ]

        for tool in tools:
            assert tool.wants_line_numbers_by_default(), f"{tool.get_name()} should want line numbers by default"

    def test_no_tools_override_line_numbers(self):
        """Verify that no tools override the base class line number behavior."""
        tools_classes = [
            ChatTool,
            CodeReviewTool,
            CodeReviewTool,
        ]

        for tool_class in tools_classes:
            has_override = "wants_line_numbers_by_default" in tool_class.__dict__
            assert not has_override, f"{tool_class.__name__} should not override wants_line_numbers_by_default"
