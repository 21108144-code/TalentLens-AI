"""
Schemas Package
===============

Pydantic schemas for API request/response validation.
"""

from schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    Token,
    TokenData
)
from schemas.resume import (
    ResumeBase,
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeDetailResponse,
    ResumeUploadResponse,
    ResumeAnalysis,
    SkillInfo,
    WorkExperience,
    Education
)
from schemas.job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobSearchParams
)
from schemas.match import (
    MatchCreate,
    MatchResponse,
    MatchDetailResponse,
    MatchListResponse,
    MatchScoreBreakdown,
    MatchExplanation,
    SkillMatch
)
from schemas.recommendation import (
    RecommendedJob,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationFilters,
    RecommendationExplanation
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserLogin", "UserUpdate", "UserResponse", "Token", "TokenData",
    # Resume
    "ResumeBase", "ResumeCreate", "ResumeUpdate", "ResumeResponse", "ResumeDetailResponse",
    "ResumeUploadResponse", "ResumeAnalysis", "SkillInfo", "WorkExperience", "Education",
    # Job
    "JobBase", "JobCreate", "JobUpdate", "JobResponse", "JobListResponse", "JobSearchParams",
    # Match
    "MatchCreate", "MatchResponse", "MatchDetailResponse", "MatchListResponse",
    "MatchScoreBreakdown", "MatchExplanation", "SkillMatch",
    # Recommendation
    "RecommendedJob", "RecommendationRequest", "RecommendationResponse",
    "RecommendationFilters", "RecommendationExplanation"
]
