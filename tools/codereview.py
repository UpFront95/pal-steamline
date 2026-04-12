"""
Review / Cleanup Workflow tool - Systematic code review or cleanup analysis

This tool provides a structured workflow for two related activities:
- **review** mode: Comprehensive code review covering quality, security, performance, and architecture.
- **cleanup** mode: Systematic cleanup analysis identifying code smells, decomposition
  opportunities, modernization paths, and organisation improvements.

Both modes guide the CLI agent through systematic investigation steps with forced pauses between
each step to ensure thorough code examination and quality assessment before proceeding.

Key features:
- Step-by-step workflow with progress tracking
- Context-aware file embedding (references during investigation, full content for analysis)
- Automatic issue tracking with severity classification
- Expert analysis integration with external models
- Mode-specific confidence-based workflow optimisation
"""

import logging
from typing import TYPE_CHECKING, Any, Literal, Optional

from pydantic import Field, model_validator

if TYPE_CHECKING:
    pass

from config import TEMPERATURE_ANALYTICAL
from systemprompts import CODEREVIEW_PROMPT, REFACTOR_PROMPT
from tools.shared.base_models import WorkflowRequest

from .workflow.base import WorkflowTool

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Review-mode field descriptions
# ---------------------------------------------------------------------------
CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "Review narrative. Step 1: outline the review strategy. Later steps: report findings. MUST cover quality, security, "
        "performance, and architecture. Reference code via `relevant_files`; avoid dumping large snippets."
    ),
    "step_number": "Current review step (starts at 1) – each step should build on the last.",
    "total_steps": (
        "Number of review steps planned. External validation: two steps (analysis + summary). Internal validation: one step. "
        "Use the same limits when continuing an existing review via continuation_id."
    ),
    "next_step_required": (
        "True when another review step follows. External validation: step 1 → True, step 2 → False. Internal validation: set False immediately. "
        "Apply the same rule on continuation flows."
    ),
    "findings": "Capture findings (positive and negative) across quality, security, performance, and architecture; update each step.",
    "files_checked": "Absolute paths of every file reviewed, including those ruled out.",
    "relevant_files": "Step 1: list all files/dirs under review. Must be absolute full non-abbreviated paths. Final step: narrow to files tied to key findings.",
    "relevant_context": "Functions or methods central to findings (e.g. 'Class.method' or 'function_name').",
    "issues_found": "Issues with severity (critical/high/medium/low) and descriptions.",
    "review_validation_type": "Review mode: set 'external' (default) for expert follow-up or 'internal' for local-only review.",
    "images": "Optional diagram or screenshot paths that clarify review context.",
    "review_type": "Review mode: review focus (full/security/performance/quick). Defaults to 'full'.",
    "focus_on": "Review mode: areas to emphasise (e.g. 'threading', 'auth flow').",
    "standards": "Review mode: coding standards or style guides to enforce.",
    "severity_filter": "Review mode: lowest severity to include when reporting issues (critical/high/medium/low/all). Defaults to 'all'.",
}

# ---------------------------------------------------------------------------
# Refactor-mode field descriptions
# ---------------------------------------------------------------------------
REFACTOR_FIELD_DESCRIPTIONS = {
    "step": (
        "The refactoring plan. Step 1: state strategy. Later steps: report findings. "
        "CRITICAL: Examine code for smells, and opportunities for decomposition, modernisation, and organisation. "
        "Use 'relevant_files' for code. FORBIDDEN: Large code snippets."
    ),
    "findings": (
        "Summary of discoveries from this step, including code smells and opportunities for decomposition, modernisation, or organisation. "
        "Document both strengths and weaknesses. In later steps, confirm or update past findings."
    ),
    "issues_found": (
        "Refactoring opportunities as dicts with 'severity' (critical/high/medium/low), "
        "'type' (codesmells/decompose/modernize/organization), and 'description'. "
        "Include all improvement opportunities found."
    ),
    "confidence": (
        "Cleanup mode only. Your confidence in refactoring analysis: exploring (starting), incomplete (significant work remaining), "
        "partial (some opportunities found, more analysis needed), complete (comprehensive analysis finished, "
        "all major opportunities identified). "
        "WARNING: Use 'complete' ONLY when fully analysed and can provide recommendations without expert help. "
        "'complete' PREVENTS expert validation. Use 'partial' for large files or uncertain analysis."
    ),
    "refactor_type": "Cleanup mode: type of refactoring analysis (codesmells/decompose/modernize/organization). Defaults to 'codesmells'.",
    "focus_areas": "Cleanup mode: specific areas to focus on (e.g. 'performance', 'readability', 'maintainability', 'security').",
    "style_guide_examples": (
        "Cleanup mode: existing code files to use as style/pattern reference (must be FULL absolute paths to real files/folders – "
        "DO NOT SHORTEN). These files represent the target coding style and patterns for the project."
    ),
}


class CodeReviewRequest(WorkflowRequest):
    """Request model for code review / refactor workflow investigation steps."""

    # ------------------------------------------------------------------
    # Mode selector
    # ------------------------------------------------------------------
    mode: Literal["review", "cleanup"] = Field(
        "review",
        description=(
            "'review' for quality/security/performance/architecture audit; "
            "'cleanup' for code smell detection, decomposition, modernisation, and organisation improvements."
        ),
    )

    # ------------------------------------------------------------------
    # Required workflow fields (shared)
    # ------------------------------------------------------------------
    step: str = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])

    # ------------------------------------------------------------------
    # Investigation tracking fields (shared)
    # ------------------------------------------------------------------
    findings: str = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["files_checked"]
    )
    relevant_files: list[str] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"]
    )
    relevant_context: list[str] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["relevant_context"]
    )
    issues_found: list[dict] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["issues_found"]
    )

    # Optional images for visual context (shared)
    images: Optional[list[str]] = Field(default=None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["images"])

    # ------------------------------------------------------------------
    # Review-mode fields (only valid when mode="review")
    # ------------------------------------------------------------------
    review_validation_type: Optional[Literal["external", "internal"]] = Field(
        None,
        description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["review_validation_type"],
    )
    review_type: Optional[Literal["full", "security", "performance", "quick"]] = Field(
        None,
        description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["review_type"],
    )
    focus_on: Optional[str] = Field(None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["focus_on"])
    standards: Optional[str] = Field(None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["standards"])
    severity_filter: Optional[Literal["critical", "high", "medium", "low", "all"]] = Field(
        None,
        description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["severity_filter"],
    )

    # ------------------------------------------------------------------
    # Cleanup-mode fields (only valid when mode="cleanup")
    # ------------------------------------------------------------------
    confidence: Optional[Literal["exploring", "incomplete", "partial", "complete"]] = Field(
        None,
        description=REFACTOR_FIELD_DESCRIPTIONS["confidence"],
    )
    refactor_type: Optional[Literal["codesmells", "decompose", "modernize", "organization"]] = Field(
        None,
        description=REFACTOR_FIELD_DESCRIPTIONS["refactor_type"],
    )
    focus_areas: Optional[list[str]] = Field(None, description=REFACTOR_FIELD_DESCRIPTIONS["focus_areas"])
    style_guide_examples: Optional[list[str]] = Field(
        None, description=REFACTOR_FIELD_DESCRIPTIONS["style_guide_examples"]
    )

    # Exclude inherited fields that are not relevant to this tool's schema
    temperature: Optional[float] = Field(default=None, exclude=True)
    thinking_mode: Optional[str] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validate_mode_fields(self):
        """Enforce cross-mode field restrictions and supply mode-specific defaults."""
        if self.mode == "review":
            cross_mode_fields = {
                "confidence": self.confidence,
                "refactor_type": self.refactor_type,
                "focus_areas": self.focus_areas,
                "style_guide_examples": self.style_guide_examples,
            }
            bad = [name for name, val in cross_mode_fields.items() if val is not None]
            if bad:
                raise ValueError(
                    f"Fields {bad} are only valid when mode='cleanup'. "
                    "Remove them or switch to mode='cleanup'."
                )
        elif self.mode == "cleanup":
            cross_mode_fields = {
                "review_type": self.review_type,
                "focus_on": self.focus_on,
                "standards": self.standards,
                "severity_filter": self.severity_filter,
                "review_validation_type": self.review_validation_type,
            }
            bad = [name for name, val in cross_mode_fields.items() if val is not None]
            if bad:
                raise ValueError(
                    f"Fields {bad} are only valid when mode='review'. "
                    "Remove them or switch to mode='review'."
                )
            # Supply default confidence for cleanup mode
            if self.confidence is None:
                self.confidence = "incomplete"
        return self

    @model_validator(mode="after")
    def validate_step_one_requirements(self):
        """Ensure step 1 has required relevant_files field."""
        if self.step_number == 1 and not self.relevant_files:
            raise ValueError("Step 1 requires 'relevant_files' field to specify code files or directories to review")
        return self


class CodeReviewTool(WorkflowTool):
    """
    Code Review / Refactor workflow tool.

    Operates in two modes selected via the ``mode`` field:

    * **review** — Systematic, step-by-step code review with expert validation.
      Covers quality, security, performance, and architecture.

    * **refactor** — Structured refactoring analysis identifying code smells,
      decomposition opportunities, modernisation paths, and organisation improvements.
    """

    def __init__(self):
        super().__init__()
        self.initial_request = None
        self.review_config = {}
        self.refactor_config = {}
        # Tracks the mode of the currently executing workflow step.
        # Set in prepare_step_data / customize_workflow_response from the live request.
        self._current_mode = "review"

    def get_name(self) -> str:
        return "review"

    def get_description(self) -> str:
        return (
            "Checks code that works but might have issues — quality, security, performance, and architecture. "
            "Use mode='review' (default) to audit for bugs, security holes, and performance problems. "
            "Use mode='cleanup' to find code smells, decompose large functions, modernize patterns, and reorganize structure. "
            "Both modes run a structured investigation with expert validation."
        )

    def get_system_prompt(self) -> str:
        return REFACTOR_PROMPT if self._current_mode == "cleanup" else CODEREVIEW_PROMPT

    def get_default_temperature(self) -> float:
        return TEMPERATURE_ANALYTICAL

    def get_workflow_request_model(self):
        """Return the merged workflow request model."""
        return CodeReviewRequest

    def get_input_schema(self) -> dict[str, Any]:
        """Generate input schema using WorkflowSchemaBuilder with all mode-specific fields."""
        from .workflow.schema_builders import WorkflowSchemaBuilder

        field_overrides = {
            # Mode selector
            "mode": {
                "type": "string",
                "enum": ["review", "refactor"],
                "default": "review",
                "description": (
                    "'review' for quality/security/performance/architecture audit; "
                    "'refactor' for code smell detection, decomposition, modernisation, and organisation improvements."
                ),
            },
            # Shared required fields
            "step": {
                "type": "string",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["step"],
            },
            "step_number": {
                "type": "integer",
                "minimum": 1,
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["step_number"],
            },
            "total_steps": {
                "type": "integer",
                "minimum": 1,
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"],
            },
            "next_step_required": {
                "type": "boolean",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"],
            },
            "findings": {
                "type": "string",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["findings"],
            },
            "files_checked": {
                "type": "array",
                "items": {"type": "string"},
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["files_checked"],
            },
            "relevant_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"],
            },
            "issues_found": {
                "type": "array",
                "items": {"type": "object"},
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["issues_found"],
            },
            "images": {
                "type": "array",
                "items": {"type": "string"},
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["images"],
            },
            # Review-mode fields
            "review_validation_type": {
                "type": "string",
                "enum": ["external", "internal"],
                "default": "external",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["review_validation_type"],
            },
            "review_type": {
                "type": "string",
                "enum": ["full", "security", "performance", "quick"],
                "default": "full",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["review_type"],
            },
            "focus_on": {
                "type": "string",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["focus_on"],
            },
            "standards": {
                "type": "string",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["standards"],
            },
            "severity_filter": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low", "all"],
                "default": "all",
                "description": CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["severity_filter"],
            },
            # Refactor-mode fields
            "confidence": {
                "type": "string",
                "enum": ["exploring", "incomplete", "partial", "complete"],
                "default": "incomplete",
                "description": REFACTOR_FIELD_DESCRIPTIONS["confidence"],
            },
            "refactor_type": {
                "type": "string",
                "enum": ["codesmells", "decompose", "modernize", "organization"],
                "default": "codesmells",
                "description": REFACTOR_FIELD_DESCRIPTIONS["refactor_type"],
            },
            "focus_areas": {
                "type": "array",
                "items": {"type": "string"},
                "description": REFACTOR_FIELD_DESCRIPTIONS["focus_areas"],
            },
            "style_guide_examples": {
                "type": "array",
                "items": {"type": "string"},
                "description": REFACTOR_FIELD_DESCRIPTIONS["style_guide_examples"],
            },
        }

        return WorkflowSchemaBuilder.build_schema(
            tool_specific_fields=field_overrides,
            model_field_schema=self.get_model_field_schema(),
            auto_mode=False,
            tool_name=self.get_name(),
        )

    # ------------------------------------------------------------------
    # Mode-aware required actions
    # ------------------------------------------------------------------

    def get_required_actions(
        self, step_number: int, confidence: str, findings: str, total_steps: int, request=None
    ) -> list[str]:
        """Define required actions for each investigation phase."""
        if self._current_mode == "cleanup":
            return self._get_refactor_required_actions(step_number, confidence)
        return self._get_review_required_actions(step_number, request)

    def _get_review_required_actions(self, step_number: int, request=None) -> list[str]:
        """Required actions for review mode."""
        if request:
            continuation_id = self.get_request_continuation_id(request)
            validation_type = self.get_review_validation_type(request)
            if continuation_id and validation_type == "external":
                if step_number == 1:
                    return [
                        "Quickly review the code files to understand context",
                        "Identify any critical issues that need immediate attention",
                        "Note main architectural patterns and design decisions",
                        "Prepare summary of key findings for expert validation",
                    ]
                else:
                    return ["Complete review and proceed to expert analysis"]

        if step_number == 1:
            return [
                "Read and understand the code files specified for review",
                "Examine the overall structure, architecture, and design patterns used",
                "Identify the main components, classes, and functions in the codebase",
                "Understand the business logic and intended functionality",
                "Look for obvious issues: bugs, security concerns, performance problems",
                "Note any code smells, anti-patterns, or areas of concern",
            ]
        elif step_number == 2:
            return [
                "Examine specific code sections you've identified as concerning",
                "Analyse security implications: input validation, authentication, authorisation",
                "Check for performance issues: algorithmic complexity, resource usage, inefficiencies",
                "Look for architectural problems: tight coupling, missing abstractions, scalability issues",
                "Identify code quality issues: readability, maintainability, error handling",
                "Search for over-engineering, unnecessary complexity, or design patterns that could be simplified",
            ]
        elif step_number >= 3:
            return [
                "Verify all identified issues have been properly documented with severity levels",
                "Check for any missed critical security vulnerabilities or performance bottlenecks",
                "Confirm that architectural concerns and code quality issues are comprehensively captured",
                "Ensure positive aspects and well-implemented patterns are also noted",
                "Validate that your assessment aligns with the review type and focus areas specified",
                "Double-check that findings are actionable and provide clear guidance for improvements",
            ]
        else:
            return [
                "Continue examining the codebase for additional patterns and potential issues",
                "Gather more evidence using appropriate code analysis techniques",
                "Test your assumptions about code behaviour and design decisions",
                "Look for patterns that confirm or refute your current assessment",
                "Focus on areas that haven't been thoroughly examined yet",
            ]

    def _get_refactor_required_actions(self, step_number: int, confidence: str) -> list[str]:
        """Required actions for cleanup mode."""
        if step_number == 1:
            return [
                "Read and understand the code files specified for refactoring analysis",
                "Examine the overall structure, architecture, and design patterns used",
                "Identify potential code smells: long methods, large classes, duplicate code, complex conditionals",
                "Look for decomposition opportunities: oversized components that could be broken down",
                "Check for modernisation opportunities: outdated patterns, deprecated features, newer language constructs",
                "Assess organisation: logical grouping, file structure, naming conventions, module boundaries",
                "Document specific refactoring opportunities with file locations and line numbers",
            ]
        elif confidence in ["exploring", "incomplete"]:
            return [
                "Examine specific code sections you've identified as needing refactoring",
                "Analyse code smells in detail: complexity, coupling, cohesion issues",
                "Investigate decomposition opportunities: identify natural breaking points for large components",
                "Look for modernisation possibilities: language features, patterns, libraries that could improve the code",
                "Check organisation issues: related functionality that could be better grouped or structured",
                "Trace dependencies and relationships between components to understand refactoring impact",
                "Prioritise refactoring opportunities by impact and effort required",
            ]
        elif confidence == "partial":
            return [
                "Verify all identified refactoring opportunities have been properly documented with locations",
                "Check for any missed opportunities in areas not yet thoroughly examined",
                "Confirm that refactoring suggestions align with the specified refactor_type and focus_areas",
                "Ensure refactoring opportunities are prioritised by severity and impact",
                "Validate that proposed changes would genuinely improve code quality without breaking functionality",
                "Double-check that all relevant files and code elements are captured in your analysis",
            ]
        else:
            return [
                "Continue examining the codebase for additional refactoring opportunities",
                "Gather more evidence using appropriate code analysis techniques",
                "Test your assumptions about code quality and improvement possibilities",
                "Look for patterns that confirm or refute your current refactoring assessment",
                "Focus on areas that haven't been thoroughly examined for refactoring potential",
            ]

    # ------------------------------------------------------------------
    # Expert analysis hooks (mode-aware)
    # ------------------------------------------------------------------

    def should_call_expert_analysis(self, consolidated_findings, request=None) -> bool:
        """Decide when to call external model based on investigation completeness."""
        if request and not self.get_request_use_assistant_model(request):
            return False

        if self._current_mode == "cleanup":
            if request and request.confidence == "complete":
                return False
        else:
            # Review mode: external continuations always proceed
            continuation_id = self.get_request_continuation_id(request)
            validation_type = self.get_review_validation_type(request)
            if continuation_id and validation_type == "external":
                return True

        return (
            len(consolidated_findings.relevant_files) > 0
            or len(consolidated_findings.findings) >= 2
            or len(consolidated_findings.issues_found) > 0
        )

    def prepare_expert_analysis_context(self, consolidated_findings) -> str:
        """Prepare context for external model call."""
        if self._current_mode == "cleanup":
            return self._prepare_refactor_expert_context(consolidated_findings)
        return self._prepare_review_expert_context(consolidated_findings)

    def _prepare_review_expert_context(self, consolidated_findings) -> str:
        context_parts = [
            f"=== CODE REVIEW REQUEST ===\\n{self.initial_request or 'Code review workflow initiated'}\\n=== END REQUEST ==="
        ]
        investigation_summary = self._build_code_review_summary(consolidated_findings)
        context_parts.append(
            f"\\n=== AGENT'S CODE REVIEW INVESTIGATION ===\\n{investigation_summary}\\n=== END INVESTIGATION ==="
        )
        if self.review_config:
            config_text = "\\n".join(f"- {key}: {value}" for key, value in self.review_config.items() if value)
            context_parts.append(f"\\n=== REVIEW CONFIGURATION ===\\n{config_text}\\n=== END CONFIGURATION ===")
        if consolidated_findings.relevant_context:
            methods_text = "\\n".join(f"- {method}" for method in consolidated_findings.relevant_context)
            context_parts.append(f"\\n=== RELEVANT CODE ELEMENTS ===\\n{methods_text}\\n=== END CODE ELEMENTS ===")
        if consolidated_findings.issues_found:
            issues_text = "\\n".join(
                f"[{issue.get('severity', 'unknown').upper()}] {issue.get('description', 'No description')}"
                for issue in consolidated_findings.issues_found
            )
            context_parts.append(f"\\n=== ISSUES IDENTIFIED ===\\n{issues_text}\\n=== END ISSUES ===")
        if consolidated_findings.hypotheses:
            assessments_text = "\\n".join(
                f"Step {h['step']} ({h['confidence']} confidence): {h['hypothesis']}"
                for h in consolidated_findings.hypotheses
            )
            context_parts.append(f"\\n=== ASSESSMENT EVOLUTION ===\\n{assessments_text}\\n=== END ASSESSMENTS ===")
        if consolidated_findings.images:
            images_text = "\\n".join(f"- {img}" for img in consolidated_findings.images)
            context_parts.append(
                f"\\n=== VISUAL REVIEW INFORMATION ===\\n{images_text}\\n=== END VISUAL INFORMATION ==="
            )
        return "\\n".join(context_parts)

    def _prepare_refactor_expert_context(self, consolidated_findings) -> str:
        context_parts = [
            f"=== REFACTORING ANALYSIS REQUEST ===\\n{self.initial_request or 'Refactoring workflow initiated'}\\n=== END REQUEST ==="
        ]
        investigation_summary = self._build_refactoring_summary(consolidated_findings)
        context_parts.append(
            f"\\n=== AGENT'S REFACTORING INVESTIGATION ===\\n{investigation_summary}\\n=== END INVESTIGATION ==="
        )
        if self.refactor_config:
            config_text = "\\n".join(f"- {key}: {value}" for key, value in self.refactor_config.items() if value)
            context_parts.append(f"\\n=== REFACTOR CONFIGURATION ===\\n{config_text}\\n=== END CONFIGURATION ===")
        if consolidated_findings.relevant_context:
            methods_text = "\\n".join(f"- {method}" for method in consolidated_findings.relevant_context)
            context_parts.append(f"\\n=== RELEVANT CODE ELEMENTS ===\\n{methods_text}\\n=== END CODE ELEMENTS ===")
        if consolidated_findings.issues_found:
            opportunities_text = "\\n".join(
                f"[{issue.get('severity', 'unknown').upper()}] {issue.get('type', 'unknown').upper()}: {issue.get('description', 'No description')}"
                for issue in consolidated_findings.issues_found
            )
            context_parts.append(
                f"\\n=== REFACTORING OPPORTUNITIES ===\\n{opportunities_text}\\n=== END OPPORTUNITIES ==="
            )
        if consolidated_findings.hypotheses:
            assessments_text = "\\n".join(
                f"Step {h['step']} ({h['confidence']} confidence): {h['hypothesis']}"
                for h in consolidated_findings.hypotheses
            )
            context_parts.append(f"\\n=== ASSESSMENT EVOLUTION ===\\n{assessments_text}\\n=== END ASSESSMENTS ===")
        if consolidated_findings.images:
            images_text = "\\n".join(f"- {img}" for img in consolidated_findings.images)
            context_parts.append(
                f"\\n=== VISUAL REFACTORING INFORMATION ===\\n{images_text}\\n=== END VISUAL INFORMATION ==="
            )
        return "\\n".join(context_parts)

    def _build_code_review_summary(self, consolidated_findings) -> str:
        summary_parts = [
            "=== SYSTEMATIC CODE REVIEW INVESTIGATION SUMMARY ===",
            f"Total steps: {len(consolidated_findings.findings)}",
            f"Files examined: {len(consolidated_findings.files_checked)}",
            f"Relevant files identified: {len(consolidated_findings.relevant_files)}",
            f"Code elements analysed: {len(consolidated_findings.relevant_context)}",
            f"Issues identified: {len(consolidated_findings.issues_found)}",
            "",
            "=== INVESTIGATION PROGRESSION ===",
        ]
        for finding in consolidated_findings.findings:
            summary_parts.append(finding)
        return "\\n".join(summary_parts)

    def _build_refactoring_summary(self, consolidated_findings) -> str:
        summary_parts = [
            "=== SYSTEMATIC REFACTORING INVESTIGATION SUMMARY ===",
            f"Total steps: {len(consolidated_findings.findings)}",
            f"Files examined: {len(consolidated_findings.files_checked)}",
            f"Relevant files identified: {len(consolidated_findings.relevant_files)}",
            f"Code elements analysed: {len(consolidated_findings.relevant_context)}",
            f"Refactoring opportunities identified: {len(consolidated_findings.issues_found)}",
            "",
            "=== INVESTIGATION PROGRESSION ===",
        ]
        for finding in consolidated_findings.findings:
            summary_parts.append(finding)
        return "\\n".join(summary_parts)

    def should_include_files_in_expert_prompt(self) -> bool:
        return True

    def should_embed_system_prompt(self) -> bool:
        return True

    def get_expert_thinking_mode(self) -> str:
        return "high"

    def get_expert_analysis_instruction(self) -> str:
        if self._current_mode == "cleanup":
            return (
                "Please provide comprehensive refactoring analysis based on the investigation findings. "
                "Focus on validating the identified opportunities, ensuring completeness of the analysis, "
                "and providing final recommendations for refactoring implementation, following the structured "
                "format specified in the system prompt."
            )
        return (
            "Please provide comprehensive code review analysis based on the investigation findings. "
            "Focus on identifying any remaining issues, validating the completeness of the analysis, "
            "and providing final recommendations for code improvements, following the severity-based "
            "format specified in the system prompt."
        )

    # ------------------------------------------------------------------
    # Workflow hook overrides (mode-aware)
    # ------------------------------------------------------------------

    def prepare_step_data(self, request) -> dict:
        """Map request fields for internal processing and capture current mode."""
        # Capture mode before any prompt/system-prompt calls
        self._current_mode = request.mode

        step_data = {
            "step": request.step,
            "step_number": request.step_number,
            "findings": request.findings,
            "files_checked": request.files_checked,
            "relevant_files": request.relevant_files,
            "relevant_context": request.relevant_context,
            "issues_found": request.issues_found,
            "hypothesis": request.findings,  # workflow_mixin compatibility
            "images": request.images or [],
        }

        if request.mode == "review":
            step_data["review_validation_type"] = self.get_review_validation_type(request)
            step_data["confidence"] = "high"  # dummy value for workflow_mixin compatibility
        else:
            step_data["confidence"] = request.confidence or "incomplete"

        return step_data

    def should_skip_expert_analysis(self, request, consolidated_findings) -> bool:
        """Skip expert analysis based on mode-specific logic."""
        if request.mode == "cleanup":
            return (request.confidence or "incomplete") == "complete" and not request.next_step_required

        # Review mode
        continuation_id = self.get_request_continuation_id(request)
        validation_type = self.get_review_validation_type(request)
        if continuation_id and validation_type != "internal":
            return False
        return validation_type == "internal" and not request.next_step_required

    def store_initial_issue(self, step_description: str):
        """Store initial request for expert analysis."""
        self.initial_request = step_description

    def get_review_validation_type(self, request) -> str:
        """Return review_validation_type, defaulting to 'external'."""
        try:
            return request.review_validation_type or "external"
        except AttributeError:
            return "external"

    def get_completion_status(self) -> str:
        if self._current_mode == "cleanup":
            return "refactoring_analysis_complete_ready_for_implementation"
        return "code_review_complete_ready_for_implementation"

    def get_completion_data_key(self) -> str:
        if self._current_mode == "cleanup":
            return "complete_refactoring"
        return "complete_code_review"

    def get_final_analysis_from_request(self, request):
        return request.findings

    def get_confidence_level(self, request) -> str:
        if self._current_mode == "cleanup":
            return "complete"
        return "certain"

    def get_completion_message(self) -> str:
        if self._current_mode == "cleanup":
            return (
                "Refactoring analysis complete with COMPLETE confidence. You have identified all significant "
                "refactoring opportunities and provided comprehensive analysis. MANDATORY: Present the user with "
                "the complete refactoring results organised by type and severity, and IMMEDIATELY proceed with "
                "implementing the highest priority refactoring opportunities or provide specific guidance for "
                "improvements. Focus on actionable refactoring steps."
            )
        return (
            "Code review complete. You have identified all significant issues "
            "and provided comprehensive analysis. MANDATORY: Present the user with the complete review results "
            "categorised by severity, and IMMEDIATELY proceed with implementing the highest priority fixes "
            "or provide specific guidance for improvements. Focus on actionable recommendations."
        )

    def get_skip_reason(self) -> str:
        if self._current_mode == "cleanup":
            return "Completed comprehensive refactoring analysis with full confidence locally"
        return "Completed comprehensive code review with internal analysis only (no external model validation)"

    def get_skip_expert_analysis_status(self) -> str:
        if self._current_mode == "cleanup":
            return "skipped_due_to_complete_refactoring_confidence"
        return "skipped_due_to_internal_analysis_type"

    def prepare_work_summary(self) -> str:
        if self._current_mode == "cleanup":
            return self._build_refactoring_summary(self.consolidated_findings)
        return self._build_code_review_summary(self.consolidated_findings)

    def get_completion_next_steps_message(self, expert_analysis_used: bool = False) -> str:
        if self._current_mode == "cleanup":
            base_message = (
                "REFACTORING ANALYSIS IS COMPLETE. You MUST now summarise and present ALL refactoring opportunities "
                "organised by type (codesmells → decompose → modernize → organization) and severity (Critical → High → "
                "Medium → Low), specific code locations with line numbers, and exact recommendations for improvement. "
                "Clearly prioritise the top 3 refactoring opportunities that need immediate attention. Provide concrete, "
                "actionable guidance for each opportunity—make it easy for a developer to understand exactly what needs "
                "to be refactored and how to implement the improvements."
            )
        else:
            base_message = (
                "CODE REVIEW IS COMPLETE. You MUST now summarise and present ALL review findings organised by "
                "severity (Critical → High → Medium → Low), specific code locations with line numbers, and exact "
                "recommendations for improvement. Clearly prioritise the top 3 issues that need immediate attention. "
                "Provide concrete, actionable guidance for each issue—make it easy for a developer to understand "
                "exactly what needs to be fixed and how to implement the improvements."
            )

        if expert_analysis_used:
            expert_guidance = self.get_expert_analysis_guidance()
            if expert_guidance:
                return f"{base_message}\n\n{expert_guidance}"

        return base_message

    def get_expert_analysis_guidance(self) -> str:
        if self._current_mode == "cleanup":
            return (
                "IMPORTANT: Expert refactoring analysis has been provided above. You MUST review "
                "the expert's architectural insights and refactoring recommendations. Consider whether "
                "the expert's suggestions align with the codebase's evolution trajectory and current "
                "team priorities. Pay special attention to any breaking changes, migration complexity, "
                "or performance implications highlighted by the expert. Present a balanced view that "
                "considers both immediate benefits and long-term maintainability."
            )
        return (
            "IMPORTANT: Analysis from an assistant model has been provided above. You MUST critically evaluate and validate "
            "the expert findings rather than accepting them blindly. Cross-reference the expert analysis with "
            "your own investigation findings, verify that suggested improvements are appropriate for this "
            "codebase's context and patterns, and ensure recommendations align with the project's standards. "
            "Present a synthesis that combines your systematic review with validated expert insights, clearly "
            "distinguishing between findings you've independently confirmed and additional insights from expert analysis."
        )

    # ------------------------------------------------------------------
    # Step guidance (mode-aware dispatch)
    # ------------------------------------------------------------------

    def get_step_guidance_message(self, request) -> str:
        self._current_mode = request.mode
        if request.mode == "cleanup":
            guidance = self.get_refactor_step_guidance(
                request.step_number, request.confidence or "incomplete", request
            )
        else:
            guidance = self.get_code_review_step_guidance(request.step_number, request)
        return guidance["next_steps"]

    def get_code_review_step_guidance(self, step_number: int, request) -> dict[str, Any]:
        """Step-specific guidance for review mode."""
        required_actions = self.get_required_actions(
            step_number,
            "medium",
            request.findings or "",
            request.total_steps,
            request,
        )

        continuation_id = self.get_request_continuation_id(request)
        validation_type = self.get_review_validation_type(request)
        is_external_continuation = continuation_id and validation_type == "external"
        is_internal_continuation = continuation_id and validation_type == "internal"
        tool_name = self.get_name()

        if step_number == 1:
            if is_external_continuation:
                return {
                    "next_steps": (
                        "You are on step 1 of MAXIMUM 2 steps for continuation. CRITICAL: Quickly review the code NOW. "
                        "MANDATORY ACTIONS:\\n"
                        + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                        + "\\n\\nSet next_step_required=True and step_number=2 for the next call to trigger expert analysis."
                    )
                }
            elif is_internal_continuation:
                next_steps = (
                    "Continuing previous conversation with internal validation only. The analysis will build "
                    "upon the prior findings without external model validation. REQUIRED ACTIONS:\\n"
                    + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                )
            else:
                next_steps = (
                    f"MANDATORY: DO NOT call the {tool_name} tool again immediately. You MUST first examine "
                    f"the code files thoroughly using appropriate tools. CRITICAL AWARENESS: You need to:\\n"
                    + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                    + f"\\n\\nOnly call {tool_name} again AFTER completing your investigation. "
                    f"When you call {tool_name} next time, use step_number: {step_number + 1} "
                    f"and report specific files examined, issues found, and code quality assessments discovered."
                )

        elif step_number == 2:
            if (
                request.total_steps >= 3
                and request.step_number < request.total_steps
                and not request.next_step_required
            ):
                next_steps = (
                    f"ERROR: You set total_steps={request.total_steps} but next_step_required=False on step {request.step_number}. "
                    f"This violates the minimum step requirement. You MUST set next_step_required=True until you reach the final step. "
                    f"Call {tool_name} again with next_step_required=True and continue your investigation."
                )
            elif is_external_continuation or (not request.next_step_required and validation_type == "external"):
                next_steps = (
                    "Proceeding immediately to expert analysis. "
                    f"MANDATORY: call {tool_name} tool immediately again, and set next_step_required=False to "
                    f"trigger external validation NOW."
                )
            else:
                next_steps = (
                    f"STOP! Do NOT call {tool_name} again yet. You are on step 2 of {request.total_steps} minimum required steps. "
                    f"MANDATORY ACTIONS before calling {tool_name} step {step_number + 1}:\\n"
                    + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                    + f"\\n\\nRemember: You MUST set next_step_required=True until step {request.total_steps}. "
                    + f"Only call {tool_name} again with step_number: {step_number + 1} AFTER completing these code review tasks."
                )

        elif step_number >= 3:
            if not request.next_step_required and validation_type == "external":
                next_steps = (
                    "Completing review and proceeding to expert analysis. "
                    "Ensure all findings are documented with specific file references and line numbers."
                )
            else:
                next_steps = (
                    f"WAIT! Your code review needs final verification. DO NOT call {tool_name} immediately. REQUIRED ACTIONS:\\n"
                    + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                    + f"\\n\\nREMEMBER: Ensure you have identified all significant issues across all severity levels and "
                    f"verified the completeness of your review. Document findings with specific file references and "
                    f"line numbers where applicable, then call {tool_name} with step_number: {step_number + 1}."
                )
        else:
            if (
                request.total_steps >= 3
                and request.step_number < request.total_steps
                and not request.next_step_required
            ):
                next_steps = (
                    f"ERROR: You set total_steps={request.total_steps} but next_step_required=False on step {request.step_number}. "
                    f"This violates the minimum step requirement. You MUST set next_step_required=True until step {request.total_steps}."
                )
            elif not request.next_step_required and validation_type == "external":
                next_steps = (
                    "Completing review. "
                    "Ensure all findings are documented with specific file references and severity levels."
                )
            else:
                next_steps = (
                    f"PAUSE REVIEW. Before calling {tool_name} step {step_number + 1}, you MUST examine more code thoroughly. "
                    + "Required: "
                    + ", ".join(required_actions[:2])
                    + ". "
                    + f"Your next {tool_name} call (step_number: {step_number + 1}) must include "
                    f"NEW evidence from actual code analysis, not just theories. NO recursive {tool_name} calls "
                    f"without investigation work!"
                )

        return {"next_steps": next_steps}

    def get_refactor_step_guidance(self, step_number: int, confidence: str, request) -> dict[str, Any]:
        """Step-specific guidance for cleanup mode."""
        required_actions = self._get_refactor_required_actions(step_number, confidence)
        tool_name = self.get_name()

        if step_number == 1:
            next_steps = (
                f"MANDATORY: DO NOT call the {tool_name} tool again immediately. You MUST first examine "
                f"the code files thoroughly for refactoring opportunities using appropriate tools. CRITICAL AWARENESS: "
                f"You need to identify code smells, decomposition opportunities, modernisation possibilities, and "
                f"organisation improvements across the specified refactor_type. Look for complexity issues, outdated "
                f"patterns, oversized components, and structural problems. Use file reading tools, code analysis, and "
                f"systematic examination to gather comprehensive refactoring information. Only call {tool_name} "
                f"again AFTER completing your investigation. When you call {tool_name} next time, use "
                f"step_number: {step_number + 1} and report specific files examined, refactoring opportunities found, "
                f"and improvement assessments discovered."
            )
        elif confidence in ["exploring", "incomplete"]:
            next_steps = (
                f"STOP! Do NOT call {tool_name} again yet. Based on your findings, you've identified areas that need "
                f"deeper refactoring analysis. MANDATORY ACTIONS before calling {tool_name} step {step_number + 1}:\\n"
                + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                + f"\\n\\nOnly call {tool_name} again with step_number: {step_number + 1} AFTER "
                + "completing these refactoring analysis tasks."
            )
        elif confidence == "partial":
            next_steps = (
                f"WAIT! Your refactoring analysis needs final verification. DO NOT call {tool_name} immediately. REQUIRED ACTIONS:\\n"
                + "\\n".join(f"{i+1}. {action}" for i, action in enumerate(required_actions))
                + f"\\n\\nREMEMBER: Ensure you have identified all significant refactoring opportunities across all types and "
                f"verified the completeness of your analysis. Document opportunities with specific file references and "
                f"line numbers where applicable, then call {tool_name} with step_number: {step_number + 1}."
            )
        else:
            next_steps = (
                f"PAUSE REFACTORING ANALYSIS. Before calling {tool_name} step {step_number + 1}, you MUST examine more code thoroughly. "
                + "Required: "
                + ", ".join(required_actions[:2])
                + ". "
                + f"Your next {tool_name} call (step_number: {step_number + 1}) must include "
                f"NEW evidence from actual refactoring analysis, not just theories. NO recursive {tool_name} calls "
                f"without investigation work!"
            )

        return {"next_steps": next_steps}

    # ------------------------------------------------------------------
    # customize_workflow_response (mode-aware status remapping)
    # ------------------------------------------------------------------

    def customize_workflow_response(self, response_data: dict, request) -> dict:
        """Customise response to match the active mode's workflow format."""
        self._current_mode = request.mode
        tool_name = self.get_name()  # always "codereview"

        # Store initial request and mode-specific config on first step
        if request.step_number == 1:
            self.initial_request = request.step
            if request.mode == "review" and request.relevant_files:
                self.review_config = {
                    "relevant_files": request.relevant_files,
                    "review_type": request.review_type,
                    "focus_on": request.focus_on,
                    "standards": request.standards,
                    "severity_filter": request.severity_filter,
                }
            elif request.mode == "cleanup" and request.relevant_files:
                self.refactor_config = {
                    "relevant_files": request.relevant_files,
                    "refactor_type": request.refactor_type,
                    "focus_areas": request.focus_areas,
                    "style_guide_examples": request.style_guide_examples,
                }

        # Map generic status keys to mode-specific ones
        if request.mode == "cleanup":
            status_mapping = {
                f"{tool_name}_in_progress": "refactoring_analysis_in_progress",
                f"pause_for_{tool_name}": "pause_for_refactoring_analysis",
                f"{tool_name}_required": "refactoring_analysis_required",
                f"{tool_name}_complete": "refactoring_analysis_complete",
            }
        else:
            status_mapping = {
                f"{tool_name}_in_progress": "code_review_in_progress",
                f"pause_for_{tool_name}": "pause_for_code_review",
                f"{tool_name}_required": "code_review_required",
                f"{tool_name}_complete": "code_review_complete",
            }

        if response_data["status"] in status_mapping:
            response_data["status"] = status_mapping[response_data["status"]]

        # Rename status field and add mode-specific sub-fields
        if f"{tool_name}_status" in response_data:
            if request.mode == "cleanup":
                response_data["refactoring_status"] = response_data.pop(f"{tool_name}_status")
                refactor_types: dict = {}
                for issue in self.consolidated_findings.issues_found:
                    issue_type = issue.get("type", "unknown")
                    refactor_types[issue_type] = refactor_types.get(issue_type, 0) + 1
                response_data["refactoring_status"]["opportunities_by_type"] = refactor_types
                response_data["refactoring_status"]["refactor_confidence"] = request.confidence
            else:
                response_data["code_review_status"] = response_data.pop(f"{tool_name}_status")
                issues_by_severity: dict = {}
                for issue in self.consolidated_findings.issues_found:
                    severity = issue.get("severity", "unknown")
                    issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
                response_data["code_review_status"]["issues_by_severity"] = issues_by_severity
                response_data["code_review_status"]["review_validation_type"] = self.get_review_validation_type(request)

        # Map completion keys
        if request.mode == "cleanup":
            if f"complete_{tool_name}" in response_data:
                response_data["complete_refactoring"] = response_data.pop(f"complete_{tool_name}")
            if f"{tool_name}_complete" in response_data:
                response_data["refactoring_complete"] = response_data.pop(f"{tool_name}_complete")
        else:
            if f"complete_{tool_name}" in response_data:
                response_data["complete_code_review"] = response_data.pop(f"complete_{tool_name}")
            if f"{tool_name}_complete" in response_data:
                response_data["code_review_complete"] = response_data.pop(f"{tool_name}_complete")

        return response_data

    # ------------------------------------------------------------------
    # Required abstract methods from BaseTool
    # ------------------------------------------------------------------

    def get_request_model(self):
        """Return the merged workflow request model."""
        return CodeReviewRequest

    async def prepare_prompt(self, request) -> str:
        """Not used — workflow tools use execute_workflow() directly."""
        return ""
