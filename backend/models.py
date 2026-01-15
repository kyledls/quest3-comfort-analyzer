"""Pydantic models for API responses."""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AccessoryRanking(BaseModel):
    """Model for accessory ranking data."""
    accessory_name: str
    accessory_type: str
    mention_count: int
    avg_sentiment: float
    positive_mentions: int
    negative_mentions: int
    recommendation_score: Optional[float] = None


class ComfortIssue(BaseModel):
    """Model for comfort issue data."""
    issue_type: str
    count: int
    severity: Optional[str] = None
    display_name: Optional[str] = None


class SourceDistribution(BaseModel):
    """Model for source distribution data."""
    source_name: str
    review_count: int


class AccessoryMention(BaseModel):
    """Model for individual accessory mention."""
    context_snippet: str
    sentiment_score: float
    title: Optional[str] = None
    url: Optional[str] = None
    source_name: Optional[str] = None


class AccessoryDetail(BaseModel):
    """Model for detailed accessory information."""
    accessory_name: str
    accessory_type: Optional[str] = None
    mention_count: int
    avg_sentiment: float
    mentions: List[AccessoryMention]
    pros: List[str] = []
    cons: List[str] = []


class DashboardStats(BaseModel):
    """Model for overall dashboard statistics."""
    total_reviews: int
    total_accessory_mentions: int
    total_comfort_issues: int
    unique_accessories: int
    top_accessory: Optional[str] = None
    most_common_issue: Optional[str] = None


class IssueSolution(BaseModel):
    """Model for comfort issue solutions."""
    issue_type: str
    display_name: str
    solutions: List[str]
