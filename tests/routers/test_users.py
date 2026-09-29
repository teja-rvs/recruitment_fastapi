import pytest
import pytest_asyncio

from tests.factories import RoleFactory, UserFactory

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def users(setup_factory_sessions):
    return [
        await UserFactory.create_async(),
        await UserFactory.create_async(),
        await UserFactory.create_async(),
    ]


@pytest.mark.asyncio
async def test_get_users(client, create_user_with_permissions, auth_headers, users):
    current_user = await create_user_with_permissions(["users:access", "users:view"])
    headers = await auth_headers(current_user)

    response = client.get("/users", headers=headers)

    assert response.status_code == 200

    response_data = response.json()

    expected_users = [*users, current_user]
    returned_by_id = {user["id"]: user for user in response_data}
    assert set(returned_by_id) == {user.id for user in expected_users}
    for user in expected_users:
        returned_user = returned_by_id[user.id]
        assert returned_user["email"] == user.email
        assert "password_hash" not in returned_user


@pytest.mark.asyncio
async def test_get_roles(client, create_user_with_permissions, auth_headers):
    current_user = await create_user_with_permissions(["users:access", "users:view"])
    headers = await auth_headers(current_user)

    response = client.get(f"/users/{current_user.id}/roles", headers=headers)

    assert response.status_code == 200

    response_data = response.json()
    assert [role["name"] for role in response_data] == ["Test Role"]


@pytest.mark.asyncio
async def test_assign_role_with_invalid_user(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:assign_roles"]
    )
    headers = await auth_headers(current_user)

    response = client.post("/users/100/assign_roles", headers=headers, json=[1, 2, 3])

    assert response.status_code == 404

    response_data = response.json()
    assert response_data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_assign_role_with_invalid_roles(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:assign_roles"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        f"/users/{current_user.id}/assign_roles",
        headers=headers,
        json=[123],  # invalid role id
    )

    assert response.status_code == 400

    response_json = response.json()

    assert response_json["detail"] == "Provide correct role ids"


@pytest_asyncio.fixture
async def roles(setup_factory_sessions):
    return [
        await RoleFactory.create_async(name="Role One"),
        await RoleFactory.create_async(name="Role Two"),
        await RoleFactory.create_async(name="Role Three"),
    ]


@pytest.mark.asyncio
async def test_assign_roles_successful(
    client, create_user_with_permissions, auth_headers, roles
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:assign_roles"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        f"/users/{current_user.id}/assign_roles",
        headers=headers,
        json=[role.id for role in roles],
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["id"] == current_user.id
    assert "password_hash" not in response_json
    assert {role["name"] for role in response_json["roles"]} == {
        "Test Role",
        "Role One",
        "Role Two",
        "Role Three",
    }


def _assert_validation_error(response, loc: tuple[str, ...]) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(tuple(error["loc"]) == loc for error in errors)


@pytest.mark.asyncio
async def test_get_roles_with_invalid_user(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(["users:access", "users:view"])
    headers = await auth_headers(current_user)

    response = client.get("/users/100/roles", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_assign_roles_to_another_user(
    client, create_user_with_permissions, auth_headers, roles
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:view", "users:assign_roles"]
    )
    target_user = await UserFactory.create_async()
    headers = await auth_headers(current_user)

    response = client.post(
        f"/users/{target_user.id}/assign_roles",
        headers=headers,
        json=[role.id for role in roles],
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["id"] == target_user.id
    assert "password_hash" not in response_json
    assert {role["name"] for role in response_json["roles"]} == {
        "Role One",
        "Role Two",
        "Role Three",
    }


@pytest.mark.asyncio
async def test_assigned_roles_are_listed_for_target_user_only(
    client, create_user_with_permissions, auth_headers, roles
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:view", "users:assign_roles"]
    )
    target_user = await UserFactory.create_async()
    headers = await auth_headers(current_user)

    assigned = client.post(
        f"/users/{target_user.id}/assign_roles",
        headers=headers,
        json=[role.id for role in roles],
    )
    assert assigned.status_code == 200

    target_roles = client.get(f"/users/{target_user.id}/roles", headers=headers)
    assert target_roles.status_code == 200
    assert {role["name"] for role in target_roles.json()} == {
        "Role One",
        "Role Two",
        "Role Three",
    }

    caller_roles = client.get(f"/users/{current_user.id}/roles", headers=headers)
    assert caller_roles.status_code == 200
    assert [role["name"] for role in caller_roles.json()] == ["Test Role"]


@pytest.mark.asyncio
async def test_assign_roles_with_partially_invalid_role_ids(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:view", "users:assign_roles"]
    )
    role = await RoleFactory.create_async(name="Role One")
    headers = await auth_headers(current_user)

    response = client.post(
        f"/users/{current_user.id}/assign_roles",
        headers=headers,
        json=[role.id, 999],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Provide correct role ids"

    roles_response = client.get(f"/users/{current_user.id}/roles", headers=headers)
    assert roles_response.status_code == 200
    assert [role_data["name"] for role_data in roles_response.json()] == ["Test Role"]


@pytest.mark.asyncio
async def test_assign_existing_role_does_not_duplicate(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:view", "users:assign_roles"]
    )
    headers = await auth_headers(current_user)

    existing_roles = client.get(f"/users/{current_user.id}/roles", headers=headers)
    assert existing_roles.status_code == 200
    existing_role_id = existing_roles.json()[0]["id"]

    response = client.post(
        f"/users/{current_user.id}/assign_roles",
        headers=headers,
        json=[existing_role_id],
    )

    assert response.status_code == 200
    assert [role["name"] for role in response.json()["roles"]] == ["Test Role"]


@pytest.mark.asyncio
async def test_assign_roles_rejects_empty_role_ids(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:assign_roles"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        f"/users/{current_user.id}/assign_roles",
        headers=headers,
        json=[],
    )

    _assert_validation_error(response, ("body",))


@pytest.mark.asyncio
async def test_get_roles_rejects_non_positive_user_id(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(["users:access", "users:view"])
    headers = await auth_headers(current_user)

    response = client.get("/users/0/roles", headers=headers)

    _assert_validation_error(response, ("path", "id"))


@pytest.mark.asyncio
async def test_assign_roles_rejects_non_positive_user_id(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["users:access", "users:assign_roles"]
    )
    headers = await auth_headers(current_user)

    response = client.post("/users/0/assign_roles", headers=headers, json=[1])

    _assert_validation_error(response, ("path", "id"))


@pytest.mark.parametrize(
    ("method", "path"),
    [
        pytest.param("get", "/users", id="list-users"),
        pytest.param("get", "/users/1/roles", id="get-roles"),
        pytest.param("post", "/users/1/assign_roles", id="assign-roles"),
    ],
)
def test_users_routes_require_authentication(client, method, path):
    kwargs = {"json": [1]} if method == "post" else {}
    response = client.request(method, path, **kwargs)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.parametrize(
    ("permissions", "method", "path"),
    [
        pytest.param(
            ["users:access"],
            "get",
            "/users",
            id="list-access-only",
        ),
        pytest.param(
            ["users:access"],
            "get",
            "/users/{user_id}/roles",
            id="roles-access-only",
        ),
        pytest.param(
            ["users:access"],
            "post",
            "/users/{user_id}/assign_roles",
            id="assign-access-only",
        ),
        pytest.param(
            ["users:view"],
            "get",
            "/users",
            id="list-without-access",
        ),
        pytest.param(
            ["users:view"],
            "get",
            "/users/{user_id}/roles",
            id="roles-without-access",
        ),
        pytest.param(
            ["users:assign_roles"],
            "post",
            "/users/{user_id}/assign_roles",
            id="assign-without-access",
        ),
        pytest.param(
            ["users:access", "users:view"],
            "post",
            "/users/{user_id}/assign_roles",
            id="assign-without-assign-permission",
        ),
        pytest.param(
            ["users:access", "users:assign_roles"],
            "get",
            "/users",
            id="list-without-view-permission",
        ),
        pytest.param(
            ["users:access", "users:assign_roles"],
            "get",
            "/users/{user_id}/roles",
            id="roles-without-view-permission",
        ),
    ],
)
@pytest.mark.asyncio
async def test_users_routes_forbidden_without_required_permission(
    client, create_user_with_permissions, auth_headers, permissions, method, path
):
    current_user = await create_user_with_permissions(permissions)
    headers = await auth_headers(current_user)
    kwargs = {"headers": headers}
    if method == "post":
        kwargs["json"] = [1]

    response = client.request(method, path.format(user_id=current_user.id), **kwargs)

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"
