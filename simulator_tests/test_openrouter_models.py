#!/usr/bin/env python3
"""
OpenRouter Models Test

Tests that OpenRouter model aliases (e.g. 'gemini') are reachable via the
chat tool and produce coherent responses.  Validates:
- Basic chat call with the 'gemini' alias routes through OpenRouter
- Conversation continuation works with OpenRouter models
- Response content is non-empty and meaningful
"""

from .base_test import BaseSimulatorTest


class OpenRouterModelsTest(BaseSimulatorTest):
    """Test OpenRouter model aliases via the chat tool"""

    @property
    def test_name(self) -> str:
        return "openrouter_models"

    @property
    def test_description(self) -> str:
        return "OpenRouter model aliases (gemini) via chat tool"

    def run_test(self) -> bool:
        """Test OpenRouter model routing with the gemini alias"""
        try:
            self.logger.info("Test: OpenRouter models — gemini alias")

            self.setup_test_files()

            # 2.1 — basic call with gemini alias
            self.logger.info("  2.1: Basic chat call using gemini alias")
            response1, continuation_id = self.call_mcp_tool(
                "chat",
                {
                    "prompt": "Please use low thinking mode. In one short paragraph, explain what a Fibonacci sequence is.",
                    "model": "gemini",
                },
            )

            if not response1:
                self.logger.error("Failed to get a response from OpenRouter (gemini alias)")
                return False

            if not continuation_id:
                self.logger.error("No continuation_id returned from OpenRouter call")
                return False

            self.logger.info(f"  ✅ Got response via gemini alias, continuation_id: {continuation_id}")

            # 2.2 — verify response contains meaningful content
            self.logger.info("  2.2: Validating response content")
            keywords = ["fibonacci", "sequence", "number"]
            response_lower = response1.lower()
            found = [kw for kw in keywords if kw in response_lower]
            if not found:
                self.logger.error(f"Response does not mention expected keywords {keywords}: {response1[:200]}")
                return False

            self.logger.info(f"  ✅ Response contains expected keywords: {found}")

            # 2.3 — conversation continuation with gemini
            self.logger.info("  2.3: Conversation continuation with gemini alias")
            response2, _ = self.call_mcp_tool(
                "chat",
                {
                    "prompt": "Please use low thinking mode. Give me the first 5 numbers in the sequence.",
                    "continuation_id": continuation_id,
                    "model": "gemini",
                },
            )

            if not response2:
                self.logger.error("Failed to continue conversation with gemini alias")
                return False

            # Expect digits 0/1 through 3 to appear
            digits_found = any(d in response2 for d in ["0", "1", "2", "3"])
            if not digits_found:
                self.logger.error(f"Continuation response missing expected Fibonacci digits: {response2[:200]}")
                return False

            self.logger.info("  ✅ Conversation continuation working with gemini alias")

            # 2.4 — file analysis with gemini
            self.logger.info("  2.4: File analysis with gemini alias")
            response3, _ = self.call_mcp_tool(
                "chat",
                {
                    "prompt": "Please use low thinking mode. In one sentence, describe what this Python file does.",
                    "absolute_file_paths": [self.test_files["python"]],
                    "model": "gemini",
                },
            )

            if not response3:
                self.logger.error("Failed to get file-analysis response from gemini alias")
                return False

            self.logger.info("  ✅ File analysis working with gemini alias")
            self.logger.info("OpenRouter models test passed")
            return True

        except Exception as e:
            self.logger.error(f"OpenRouter models test failed: {e}")
            return False
        finally:
            self.cleanup_test_files()
