"""
Pydantic models for API payloads and responses.
"""

from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    """
    Basic user representation.
    
    Attributes:
        user_id: Unique user identifier.
        name: Optional user name.
        score: Optional recommendation score.
    """

    user_id: int
    name: Optional[str] = None
    score: Optional[float] = None


class Job(BaseModel):
    """
    Job representation for API responses.
    
    Attributes:
        job_id: Unique job identifier.
        title: Job title.
        company: Optional company name.
        location: Optional job location.
        job_posting_url: Optional URL to job posting.
        normalized_salary: Optional normalized salary value.
        score: Recommendation score (similarity).
    """

    job_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_posting_url: Optional[str] = None
    normalized_salary: Optional[float] = None
    score: float


class RecommendationResponse(BaseModel):
    """
    Generic recommendation wrapper for API responses.
    
    Attributes:
        user: The user for whom recommendations are generated.
        friends: Optional list of friend recommendations.
        people_you_may_know: Optional list of people suggestions.
        jobs: Optional list of job recommendations.
        direct_friends_count: Optional count of direct friends.
        friends_of_friends_count: Optional count of friends of friends.
    """

    user: User
    friends: List[User] | None = None
    people_you_may_know: List[User] | None = None
    jobs: List[Job] | None = None
    direct_friends_count: Optional[int] = None
    friends_of_friends_count: Optional[int] = None

