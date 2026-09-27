from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from recruitment_fastapi.models import Candidate, RecruitmentStep
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository
from tests.factories import (
    BackgroundVerificationStepFactory,
    DsAlgoInterviewStepFactory,
    EntryCandidateFactory,
    HldInterviewStepFactory,
    LldInterviewStepFactory,
    PhoneScreenerStepFactory,
    RecruitmentStepFactory,
)

pytestmark = pytest.mark.integration

_FUTURE_DATE = "future"
_TODAY_DATE = "today"


def _future_interview_date() -> str:
    return (datetime.now(tz=UTC).date() + timedelta(days=1)).isoformat()


def _today() -> str:
    return datetime.now(tz=UTC).date().isoformat()


def _resolve_dates(payload: dict | None) -> dict | None:
    if payload is None:
        return None

    resolved = dict(payload)
    interview_date = resolved.get("interview_date")
    if interview_date == _FUTURE_DATE:
        resolved["interview_date"] = _future_interview_date()
    elif interview_date == _TODAY_DATE:
        resolved["interview_date"] = _today()
    return resolved


@pytest_asyncio.fixture
async def candidate(setup_factory_sessions):
    return await EntryCandidateFactory.create_async()


@pytest_asyncio.fixture
async def recruitment_steps(candidate):
    return [
        await RecruitmentStepFactory.create_async(candidate=candidate),
        await PhoneScreenerStepFactory.create_async(candidate=candidate),
        await DsAlgoInterviewStepFactory.create_async(candidate=candidate),
        await LldInterviewStepFactory.create_async(candidate=candidate),
        await HldInterviewStepFactory.create_async(candidate=candidate),
        await BackgroundVerificationStepFactory.create_async(candidate=candidate),
    ]


@pytest_asyncio.fixture
async def phone_screener_step(candidate):
    return await PhoneScreenerStepFactory.create_async(candidate=candidate)


def _assert_validation_error(response, loc: tuple[str, ...]) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(tuple(error["loc"]) == loc for error in errors)


async def _transition_step(session_factory, step, *transitions, **fields) -> None:
    async with session_factory() as session:
        persisted = await session.get(RecruitmentStep, step.id)
        for transition in transitions:
            getattr(persisted, transition)()
        for name, value in fields.items():
            setattr(persisted, name, value)
        await session.commit()


def _listed_step(client, headers, step_id: int) -> dict:
    response = client.get("/recruitment_steps", headers=headers)
    assert response.status_code == 200
    return next(step for step in response.json() if step["id"] == step_id)


@pytest.mark.asyncio
async def test_get_recruitment_steps(
    client, create_user_with_permissions, auth_headers, candidate, recruitment_steps
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:view"]
    )
    headers = await auth_headers(current_user)

    response = client.get("/recruitment_steps", headers=headers)

    assert response.status_code == 200

    response_json = response.json()
    returned_by_id = {step["id"]: step for step in response_json}
    assert set(returned_by_id) == {step.id for step in recruitment_steps}

    for step in recruitment_steps:
        returned_step = returned_by_id[step.id]
        assert returned_step["type"] == step.type
        assert returned_step["status"] == "initialized"
        assert returned_step["feedback"] == step.feedback
        assert returned_step["interview_date"] is None
        assert returned_step["interviewer"] is None
        assert returned_step["created_at"]
        assert returned_step["updated_at"]
        assert returned_step["candidate"]["id"] == candidate.id
        assert returned_step["candidate"]["email"] == candidate.email
        assert returned_step["candidate"]["type"] == "entry_candidate"


@pytest.mark.asyncio
async def test_assign_interviewer(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        [
            "recruitment_steps:access",
            "recruitment_steps:assign_interviewer",
            "recruitment_steps:view",
        ]
    )
    interviewer = await create_user_with_permissions([], role="Recruiter")
    headers = await auth_headers(current_user)
    await _transition_step(session_factory, phone_screener_step, "start")
    interview_date = _future_interview_date()

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/assign_interviewer",
        headers=headers,
        json={
            "interviewer_id": interviewer.id,
            "interview_date": interview_date,
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["id"] == phone_screener_step.id
    assert response_json["type"] == "phone_screener_step"
    assert response_json["status"] == "interview_scheduled"
    assert response_json["interview_date"] == interview_date
    assert response_json["interviewer"]["id"] == interviewer.id
    assert response_json["interviewer"]["email"] == interviewer.email
    assert "password_hash" not in response_json["interviewer"]

    listed = _listed_step(client, headers, phone_screener_step.id)
    assert listed["status"] == "interview_scheduled"
    assert listed["interview_date"] == interview_date
    assert listed["interviewer"]["id"] == interviewer.id


@pytest.mark.asyncio
async def test_assign_interviewer_with_interview_date_only(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:assign_interviewer"]
    )
    headers = await auth_headers(current_user)
    await _transition_step(session_factory, phone_screener_step, "start")
    interview_date = _future_interview_date()

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/assign_interviewer",
        headers=headers,
        json={"interview_date": interview_date},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["status"] == "in_progress"
    assert response_json["interview_date"] == interview_date
    assert response_json["interviewer"] is None


@pytest.mark.asyncio
async def test_assign_interviewer_with_interviewer_only(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:assign_interviewer"]
    )
    interviewer = await create_user_with_permissions([], role="Recruiter")
    headers = await auth_headers(current_user)
    await _transition_step(session_factory, phone_screener_step, "start")

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/assign_interviewer",
        headers=headers,
        json={"interviewer_id": interviewer.id},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["status"] == "in_progress"
    assert response_json["interview_date"] is None
    assert response_json["interviewer"]["id"] == interviewer.id
    assert response_json["interviewer"]["email"] == interviewer.email
    assert "password_hash" not in response_json["interviewer"]


@pytest.mark.asyncio
async def test_assign_interviewer_when_interviewer_not_found(
    client, create_user_with_permissions, auth_headers, phone_screener_step
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:assign_interviewer"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/assign_interviewer",
        headers=headers,
        json={
            "interviewer_id": 999,
            "interview_date": _future_interview_date(),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interviewer not found"


@pytest.mark.asyncio
async def test_assign_interviewer_when_user_lacks_allowed_role(
    client, create_user_with_permissions, auth_headers, phone_screener_step
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:assign_interviewer"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/assign_interviewer",
        headers=headers,
        json={
            "interviewer_id": current_user.id,
            "interview_date": _future_interview_date(),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interviewer not found"


@pytest.mark.asyncio
async def test_interview_complete(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        [
            "recruitment_steps:access",
            "recruitment_steps:review",
            "recruitment_steps:view",
        ]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        "schedule_interview",
        interviewer_id=current_user.id,
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/interview_complete",
        headers=headers,
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["id"] == phone_screener_step.id
    assert response_json["status"] == "in_review"
    assert response_json["interviewer"]["id"] == current_user.id

    listed = _listed_step(client, headers, phone_screener_step.id)
    assert listed["status"] == "in_review"


@pytest.mark.asyncio
async def test_review(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        [
            "recruitment_steps:access",
            "recruitment_steps:review",
            "recruitment_steps:view",
        ]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        "schedule_interview",
        "interview_complete",
        interviewer_id=current_user.id,
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/review",
        headers=headers,
        json={"review": "Test review"},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["status"] == "in_review"
    assert response_json["feedback"] == "Test review"

    listed = _listed_step(client, headers, phone_screener_step.id)
    assert listed["feedback"] == "Test review"
    assert listed["status"] == "in_review"


@pytest.mark.asyncio
async def test_review_when_step_is_not_in_review(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:review"]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        interviewer_id=current_user.id,
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/review",
        headers=headers,
        json={"review": "Test review"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Recruitment step must be in review stage"


@pytest.mark.asyncio
async def test_approve(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    candidate,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        [
            "recruitment_steps:access",
            "recruitment_steps:approve",
            "recruitment_steps:view",
        ]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        "schedule_interview",
        "interview_complete",
        interviewer_id=current_user.id,
        feedback="Test review",
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/approve",
        headers=headers,
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["status"] == "approved"
    assert response_json["feedback"] == "Test review"

    listed = _listed_step(client, headers, phone_screener_step.id)
    assert listed["status"] == "approved"

    async with session_factory() as session:
        row = await session.get(Candidate, candidate.id)
        candidate_status = row.status

    assert candidate_status == "recruited"


@pytest.mark.asyncio
async def test_approve_without_feedback(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:approve"]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        "schedule_interview",
        "interview_complete",
        interviewer_id=current_user.id,
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/approve",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Provide feedback before approval"


@pytest.mark.asyncio
async def test_reject(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    candidate,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        [
            "recruitment_steps:access",
            "recruitment_steps:reject",
            "recruitment_steps:view",
        ]
    )
    headers = await auth_headers(current_user)
    other_step = await DsAlgoInterviewStepFactory.create_async(candidate=candidate)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        "schedule_interview",
        "interview_complete",
        interviewer_id=current_user.id,
        feedback="Test review",
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/reject",
        headers=headers,
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["status"] == "rejected"
    assert response_json["feedback"] == "Test review"

    listed = _listed_step(client, headers, phone_screener_step.id)
    assert listed["status"] == "rejected"
    other_listed = _listed_step(client, headers, other_step.id)
    assert other_listed["status"] == "cancelled"

    async with session_factory() as session:
        row = await session.get(Candidate, candidate.id)
        steps = await RecruitmentStepRepository(session).find_by_candidate(candidate.id)
        candidate_status = row.status
        step_statuses = {step.id: step.status for step in steps}
    assert candidate_status == "rejected"
    assert step_statuses[phone_screener_step.id] == "rejected"
    assert step_statuses[other_step.id] == "cancelled"


@pytest.mark.asyncio
async def test_reject_without_feedback(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:reject"]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        "start",
        "schedule_interview",
        "interview_complete",
        interviewer_id=current_user.id,
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/reject",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Provide feedback before rejection"


@pytest.mark.parametrize(
    ("action", "json_body", "permissions"),
    [
        pytest.param(
            "assign_interviewer",
            {"interviewer_id": 1, "interview_date": _FUTURE_DATE},
            ["recruitment_steps:access", "recruitment_steps:assign_interviewer"],
            id="assign-interviewer",
        ),
        pytest.param(
            "interview_complete",
            None,
            ["recruitment_steps:access", "recruitment_steps:review"],
            id="interview-complete",
        ),
        pytest.param(
            "review",
            {"review": "Test review"},
            ["recruitment_steps:access", "recruitment_steps:review"],
            id="review",
        ),
        pytest.param(
            "approve",
            None,
            ["recruitment_steps:access", "recruitment_steps:approve"],
            id="approve",
        ),
        pytest.param(
            "reject",
            None,
            ["recruitment_steps:access", "recruitment_steps:reject"],
            id="reject",
        ),
    ],
)
@pytest.mark.asyncio
async def test_recruitment_step_routes_return_not_found(
    client,
    create_user_with_permissions,
    auth_headers,
    action,
    json_body,
    permissions,
):
    current_user = await create_user_with_permissions(permissions)
    headers = await auth_headers(current_user)
    kwargs = {"headers": headers}
    if json_body is not None:
        kwargs["json"] = _resolve_dates(json_body)

    response = client.post(f"/recruitment_steps/100/{action}", **kwargs)

    assert response.status_code == 404
    assert response.json()["detail"] == "Step not found"


@pytest.mark.parametrize(
    ("action", "json_body", "permission"),
    [
        pytest.param(
            "interview_complete",
            None,
            "recruitment_steps:review",
            id="interview-complete",
        ),
        pytest.param(
            "review",
            {"review": "Test review"},
            "recruitment_steps:review",
            id="review",
        ),
        pytest.param("approve", None, "recruitment_steps:approve", id="approve"),
        pytest.param("reject", None, "recruitment_steps:reject", id="reject"),
    ],
)
@pytest.mark.asyncio
async def test_interviewer_routes_forbidden_for_non_interviewer(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
    action,
    json_body,
    permission,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", permission]
    )
    interviewer = await create_user_with_permissions([], role="Recruiter")
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory, phone_screener_step, interviewer_id=interviewer.id
    )

    kwargs = {"headers": headers}
    if json_body is not None:
        kwargs["json"] = _resolve_dates(json_body)

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/{action}",
        **kwargs,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.parametrize(
    ("payload", "loc"),
    [
        pytest.param(
            {"interviewer_id": 0, "interview_date": _FUTURE_DATE},
            ("body", "interviewer_id"),
            id="interviewer-id-not-positive",
        ),
        pytest.param(
            {"interviewer_id": -1},
            ("body", "interviewer_id"),
            id="interviewer-id-negative",
        ),
        pytest.param(
            {"interview_date": "2000-01-01"},
            ("body", "interview_date"),
            id="interview-date-in-the-past",
        ),
        pytest.param(
            {"interview_date": _TODAY_DATE},
            ("body", "interview_date"),
            id="interview-date-today",
        ),
    ],
)
@pytest.mark.asyncio
async def test_assign_interviewer_rejects_invalid_payload(
    client,
    create_user_with_permissions,
    auth_headers,
    phone_screener_step,
    payload,
    loc,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:assign_interviewer"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/assign_interviewer",
        headers=headers,
        json=_resolve_dates(payload),
    )

    _assert_validation_error(response, loc)


@pytest.mark.parametrize(
    ("payload", "loc"),
    [
        pytest.param({"review": "ab"}, ("body", "review"), id="review-too-short"),
        pytest.param({}, ("body", "review"), id="missing-review"),
    ],
)
@pytest.mark.asyncio
async def test_review_rejects_invalid_payload(
    client,
    create_user_with_permissions,
    auth_headers,
    session_factory,
    phone_screener_step,
    payload,
    loc,
):
    current_user = await create_user_with_permissions(
        ["recruitment_steps:access", "recruitment_steps:review"]
    )
    headers = await auth_headers(current_user)
    await _transition_step(
        session_factory,
        phone_screener_step,
        interviewer_id=current_user.id,
    )

    response = client.post(
        f"/recruitment_steps/{phone_screener_step.id}/review",
        headers=headers,
        json=_resolve_dates(payload),
    )

    _assert_validation_error(response, loc)


@pytest.mark.parametrize(
    ("action", "json_body", "permissions"),
    [
        pytest.param(
            "assign_interviewer",
            {"interviewer_id": 1},
            ["recruitment_steps:access", "recruitment_steps:assign_interviewer"],
            id="assign-interviewer",
        ),
        pytest.param(
            "interview_complete",
            None,
            ["recruitment_steps:access", "recruitment_steps:review"],
            id="interview-complete",
        ),
        pytest.param(
            "review",
            {"review": "Test review"},
            ["recruitment_steps:access", "recruitment_steps:review"],
            id="review",
        ),
        pytest.param(
            "approve",
            None,
            ["recruitment_steps:access", "recruitment_steps:approve"],
            id="approve",
        ),
        pytest.param(
            "reject",
            None,
            ["recruitment_steps:access", "recruitment_steps:reject"],
            id="reject",
        ),
    ],
)
@pytest.mark.asyncio
async def test_recruitment_step_routes_reject_non_positive_step_id(
    client,
    create_user_with_permissions,
    auth_headers,
    action,
    json_body,
    permissions,
):
    current_user = await create_user_with_permissions(permissions)
    headers = await auth_headers(current_user)
    kwargs = {"headers": headers}
    if json_body is not None:
        kwargs["json"] = _resolve_dates(json_body)

    response = client.post(f"/recruitment_steps/0/{action}", **kwargs)

    _assert_validation_error(response, ("path", "id"))


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        pytest.param("get", "/recruitment_steps", None, id="list"),
        pytest.param(
            "post",
            "/recruitment_steps/1/assign_interviewer",
            {"interviewer_id": 1, "interview_date": _FUTURE_DATE},
            id="assign-interviewer",
        ),
        pytest.param(
            "post",
            "/recruitment_steps/1/interview_complete",
            None,
            id="interview-complete",
        ),
        pytest.param(
            "post",
            "/recruitment_steps/1/review",
            {"review": "Test review"},
            id="review",
        ),
        pytest.param("post", "/recruitment_steps/1/approve", None, id="approve"),
        pytest.param("post", "/recruitment_steps/1/reject", None, id="reject"),
    ],
)
def test_recruitment_step_routes_require_authentication(
    client, method, path, json_body
):
    kwargs = {} if json_body is None else {"json": _resolve_dates(json_body)}
    response = client.request(method, path, **kwargs)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.parametrize(
    ("permissions", "method", "path", "json_body"),
    [
        pytest.param(
            ["recruitment_steps:access"],
            "get",
            "/recruitment_steps",
            None,
            id="list-access-only",
        ),
        pytest.param(
            ["recruitment_steps:view"],
            "get",
            "/recruitment_steps",
            None,
            id="list-without-access",
        ),
        pytest.param(
            ["recruitment_steps:access", "recruitment_steps:assign_interviewer"],
            "get",
            "/recruitment_steps",
            None,
            id="list-without-view-permission",
        ),
        pytest.param(
            ["recruitment_steps:access"],
            "post",
            "/recruitment_steps/1/assign_interviewer",
            {"interviewer_id": 1},
            id="assign-access-only",
        ),
        pytest.param(
            ["recruitment_steps:assign_interviewer"],
            "post",
            "/recruitment_steps/1/assign_interviewer",
            {"interviewer_id": 1},
            id="assign-without-access",
        ),
        pytest.param(
            ["recruitment_steps:access", "recruitment_steps:view"],
            "post",
            "/recruitment_steps/1/assign_interviewer",
            {"interviewer_id": 1},
            id="assign-without-assign-permission",
        ),
        pytest.param(
            ["recruitment_steps:access"],
            "post",
            "/recruitment_steps/1/interview_complete",
            None,
            id="interview-complete-access-only",
        ),
        pytest.param(
            ["recruitment_steps:review"],
            "post",
            "/recruitment_steps/1/interview_complete",
            None,
            id="interview-complete-without-access",
        ),
        pytest.param(
            ["recruitment_steps:access", "recruitment_steps:view"],
            "post",
            "/recruitment_steps/1/interview_complete",
            None,
            id="interview-complete-without-review-permission",
        ),
        pytest.param(
            ["recruitment_steps:access"],
            "post",
            "/recruitment_steps/1/review",
            {"review": "Test review"},
            id="review-access-only",
        ),
        pytest.param(
            ["recruitment_steps:review"],
            "post",
            "/recruitment_steps/1/review",
            {"review": "Test review"},
            id="review-without-access",
        ),
        pytest.param(
            ["recruitment_steps:access", "recruitment_steps:view"],
            "post",
            "/recruitment_steps/1/review",
            {"review": "Test review"},
            id="review-without-review-permission",
        ),
        pytest.param(
            ["recruitment_steps:access"],
            "post",
            "/recruitment_steps/1/approve",
            None,
            id="approve-access-only",
        ),
        pytest.param(
            ["recruitment_steps:approve"],
            "post",
            "/recruitment_steps/1/approve",
            None,
            id="approve-without-access",
        ),
        pytest.param(
            ["recruitment_steps:access", "recruitment_steps:view"],
            "post",
            "/recruitment_steps/1/approve",
            None,
            id="approve-without-approve-permission",
        ),
        pytest.param(
            ["recruitment_steps:access"],
            "post",
            "/recruitment_steps/1/reject",
            None,
            id="reject-access-only",
        ),
        pytest.param(
            ["recruitment_steps:reject"],
            "post",
            "/recruitment_steps/1/reject",
            None,
            id="reject-without-access",
        ),
        pytest.param(
            ["recruitment_steps:access", "recruitment_steps:view"],
            "post",
            "/recruitment_steps/1/reject",
            None,
            id="reject-without-reject-permission",
        ),
    ],
)
@pytest.mark.asyncio
async def test_recruitment_step_routes_forbidden_without_required_permission(
    client,
    create_user_with_permissions,
    auth_headers,
    permissions,
    method,
    path,
    json_body,
):
    current_user = await create_user_with_permissions(permissions)
    headers = await auth_headers(current_user)
    kwargs = {"headers": headers}
    if json_body is not None:
        kwargs["json"] = _resolve_dates(json_body)

    response = client.request(method, path, **kwargs)

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"
