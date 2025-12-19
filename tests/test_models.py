"""
Unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from app.models import Job, RecommendationResponse, User


def test_user_minimal():
    """Test User with only required fields."""
    user = User(user_id=1)
    assert user.user_id == 1
    assert user.name is None
    assert user.score is None


def test_user_with_all_fields():
    """Test User with all fields."""
    user = User(user_id=1, name="Alice", score=0.95)
    assert user.user_id == 1
    assert user.name == "Alice"
    assert user.score == 0.95


def test_user_invalid_type():
    """Test User with invalid type."""
    with pytest.raises(ValidationError):
        User(user_id="not_an_int")


def test_job_minimal():
    """Test Job with only required fields."""
    job = Job(job_id="job1", title="Software Engineer", score=0.85)
    assert job.job_id == "job1"
    assert job.title == "Software Engineer"
    assert job.score == 0.85
    assert job.company is None
    assert job.location is None
    assert job.job_posting_url is None
    assert job.normalized_salary is None


def test_job_with_all_fields():
    """Test Job with all fields."""
    job = Job(
        job_id="job1",
        title="Software Engineer",
        company="Google",
        location="Paris",
        job_posting_url="https://example.com/job1",
        normalized_salary=100000.0,
        score=0.95,
    )
    assert job.job_id == "job1"
    assert job.title == "Software Engineer"
    assert job.company == "Google"
    assert job.location == "Paris"
    assert job.job_posting_url == "https://example.com/job1"
    assert job.normalized_salary == 100000.0
    assert job.score == 0.95


def test_job_missing_required():
    """Test Job with missing required fields."""
    with pytest.raises(ValidationError):
        Job(job_id="job1")  # Missing title and score


def test_recommendation_response_minimal():
    """Test RecommendationResponse with only user."""
    user = User(user_id=1)
    response = RecommendationResponse(user=user)
    assert response.user.user_id == 1
    assert response.friends is None
    assert response.people_you_may_know is None
    assert response.jobs is None
    assert response.direct_friends_count is None
    assert response.friends_of_friends_count is None


def test_recommendation_response_with_friends():
    """Test RecommendationResponse with friends."""
    user = User(user_id=1)
    friends = [
        User(user_id=2, name="Bob", score=5.0),
        User(user_id=3, name="Charlie", score=3.0),
    ]
    response = RecommendationResponse(
        user=user,
        friends=friends,
        direct_friends_count=10,
        friends_of_friends_count=50,
    )
    assert len(response.friends) == 2
    assert response.direct_friends_count == 10
    assert response.friends_of_friends_count == 50


def test_recommendation_response_with_people():
    """Test RecommendationResponse with people you may know."""
    user = User(user_id=1)
    people = [
        User(user_id=4, name="Dave", score=0.85),
        User(user_id=5, name="Eve", score=0.75),
    ]
    response = RecommendationResponse(user=user, people_you_may_know=people)
    assert len(response.people_you_may_know) == 2


def test_recommendation_response_with_jobs():
    """Test RecommendationResponse with jobs."""
    user = User(user_id=1)
    jobs = [
        Job(job_id="job1", title="Engineer", score=0.9),
        Job(job_id="job2", title="Developer", score=0.8),
    ]
    response = RecommendationResponse(user=user, jobs=jobs)
    assert len(response.jobs) == 2


def test_recommendation_response_complete():
    """Test RecommendationResponse with all fields."""
    user = User(user_id=1, name="Alice")
    friends = [User(user_id=2, name="Bob", score=5.0)]
    people = [User(user_id=3, name="Charlie", score=0.9)]
    jobs = [Job(job_id="job1", title="Engineer", score=0.85)]

    response = RecommendationResponse(
        user=user,
        friends=friends,
        people_you_may_know=people,
        jobs=jobs,
        direct_friends_count=10,
        friends_of_friends_count=50,
    )
    assert response.user.user_id == 1
    assert len(response.friends) == 1
    assert len(response.people_you_may_know) == 1
    assert len(response.jobs) == 1
    assert response.direct_friends_count == 10
    assert response.friends_of_friends_count == 50


def test_user_json_serialization():
    """Test that User can be serialized to JSON."""
    user = User(user_id=1, name="Alice", score=0.95)
    json_data = user.model_dump()
    assert json_data["user_id"] == 1
    assert json_data["name"] == "Alice"
    assert json_data["score"] == 0.95


def test_job_json_serialization():
    """Test that Job can be serialized to JSON."""
    job = Job(
        job_id="job1",
        title="Engineer",
        company="Google",
        score=0.9,
    )
    json_data = job.model_dump()
    assert json_data["job_id"] == "job1"
    assert json_data["title"] == "Engineer"
    assert json_data["company"] == "Google"
    assert json_data["score"] == 0.9
