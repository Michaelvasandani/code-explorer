"""Data models for the baseline analyzer."""

from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class FileData:
    """Represents a source file to analyze."""
    path: str
    content: str


@dataclass_json
@dataclass
class Finding:
    """Represents a single analysis finding."""
    id: str
    type: str  # bug, smell, architecture, test_gap, documentation_gap, uncertainty
    subtype: Optional[str] = None
    location: str = ""
    confidence: str = "medium"  # high, medium, low
    explanation: str = ""
    evidence: Optional[str] = None
    tags: Optional[list[str]] = None


@dataclass_json
@dataclass
class Question:
    """Represents an onboarding question."""
    id: str
    question: str
    why_it_matters: str
    related_findings: list[str] = field(default_factory=list)
    areas_affected: list[str] = field(default_factory=list)


@dataclass_json
@dataclass
class FileAgentResult:
    """Result from analyzing a single file."""
    file_path: str
    summary: str
    findings: list[dict] = field(default_factory=list)
    raw_cost_usd: float = 0.0
    raw_latency_seconds: float = 0.0


@dataclass_json
@dataclass
class RepoMergeResult:
    """Result from repo-level merge analysis."""
    high_level_summary: dict = field(default_factory=dict)
    merged_findings: list[dict] = field(default_factory=list)


@dataclass_json
@dataclass
class AnalysisReport:
    """Final analysis report."""
    high_level_summary: dict
    findings: list[Finding]
    questions: list[Question]
    tool_limitations: dict
    metadata: dict
