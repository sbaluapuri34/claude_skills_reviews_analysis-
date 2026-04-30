from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AccessType = Literal["API", "partner_api", "scraping", "unsupported"]
ComplianceLevel = Literal["safe", "restricted", "high-risk"]


@dataclass(frozen=True)
class SourceCapability:
    source_name: str
    access_type: AccessType
    compliance_level: ComplianceLevel
    enabled_by_default: bool
    requires_api_key: bool
    one_time_playwright_allowed: bool = False


SOURCE_CAPABILITY_MATRIX: dict[str, SourceCapability] = {
    "reddit_claudeai": SourceCapability(
        source_name="reddit_claudeai",
        access_type="API",
        compliance_level="safe",
        enabled_by_default=True,
        requires_api_key=True,
    ),
    "reddit_claude": SourceCapability(
        source_name="reddit_claude",
        access_type="API",
        compliance_level="safe",
        enabled_by_default=True,
        requires_api_key=True,
    ),
    "reddit_claudeskills": SourceCapability(
        source_name="reddit_claudeskills",
        access_type="API",
        compliance_level="safe",
        enabled_by_default=True,
        requires_api_key=True,
    ),
    "trustpilot_claude_ai": SourceCapability(
        source_name="trustpilot_claude_ai",
        access_type="scraping",
        compliance_level="high-risk",
        enabled_by_default=False,
        requires_api_key=False,
        one_time_playwright_allowed=True,
    ),
    "g2_claude_reviews": SourceCapability(
        source_name="g2_claude_reviews",
        access_type="scraping",
        compliance_level="high-risk",
        enabled_by_default=False,
        requires_api_key=False,
        one_time_playwright_allowed=True,
    ),
    "google_play_claude": SourceCapability(
        source_name="google_play_claude",
        access_type="partner_api",
        compliance_level="restricted",
        enabled_by_default=False,
        requires_api_key=True,
        one_time_playwright_allowed=True,
    ),
}

