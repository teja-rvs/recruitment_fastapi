import pytest
import pytest_asyncio

from tests.factories import PermissionFactory, RoleFactory

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def roles(setup_factory_sessions):
    return [
        await RoleFactory.create_async(name="Role One", key="role_one"),
        await RoleFactory.create_async(name="Role Two", key="role_two"),
        await RoleFactory.create_async(name="Role Three", key="role_three"),
    ]


@pytest_asyncio.fixture
async def permissions(setup_factory_sessions):
    return [
        await PermissionFactory.create_async(name="candidates:view"),
        await PermissionFactory.create_async(name="candidates:create"),
        await PermissionFactory.create_async(name="candidates:update"),
    ]


@pytest.mark.asyncio
async def test_get_roles(client, create_user_with_permissions, auth_headers, roles):
    current_user = await create_user_with_permissions(["roles:access", "roles:view"])
    headers = await auth_headers(current_user)

    response = client.get("/admin/roles", headers=headers)

    assert response.status_code == 200

    response_data = response.json()

    expected_roles = [*roles, current_user.roles[0]]
    returned_by_id = {role["id"]: role for role in response_data}
    assert set(returned_by_id) == {role.id for role in expected_roles}
    for role in expected_roles:
        returned_role = returned_by_id[role.id]
        assert returned_role["name"] == role.name
        assert returned_role["key"] == role.key
        assert returned_role["created_at"]
        assert returned_role["updated_at"]
        assert "permissions" not in returned_role


@pytest.mark.asyncio
async def test_create_role(client, create_user_with_permissions, auth_headers):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:create", "roles:view"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        "/admin/roles",
        headers=headers,
        json={"name": "Hiring Manager"},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["name"] == "Hiring Manager"
    assert response_json["key"] == "hiring_manager"
    assert response_json["created_at"]
    assert response_json["updated_at"]
    assert "permissions" not in response_json


@pytest.mark.asyncio
async def test_created_role_is_listed(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:create", "roles:view"]
    )
    headers = await auth_headers(current_user)

    created = client.post(
        "/admin/roles",
        headers=headers,
        json={"name": "Hiring Manager"},
    )
    assert created.status_code == 200

    listed = client.get("/admin/roles", headers=headers)

    assert listed.status_code == 200
    assert {role["name"]: role["key"] for role in listed.json()} == {
        "Test Role": "test_role",
        "Hiring Manager": "hiring_manager",
    }


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("Test Role", id="same-name"),
        pytest.param("test role", id="same-key"),
    ],
)
@pytest.mark.asyncio
async def test_create_role_when_role_exists(
    client, create_user_with_permissions, auth_headers, name
):
    current_user = await create_user_with_permissions(["roles:access", "roles:create"])
    headers = await auth_headers(current_user)

    response = client.post("/admin/roles", headers=headers, json={"name": name})

    assert response.status_code == 409
    assert response.json()["detail"] == "Role exists"


@pytest.mark.asyncio
async def test_assign_permissions_with_invalid_role(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        "/admin/roles/100/assign_permissions",
        headers=headers,
        json=[1, 2, 3],
    )

    assert response.status_code == 404

    response_data = response.json()
    assert response_data["detail"] == "Role not found"


@pytest.mark.asyncio
async def test_assign_permissions_with_invalid_permissions(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    headers = await auth_headers(current_user)
    role = current_user.roles[0]

    response = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[123],
    )

    assert response.status_code == 400

    response_json = response.json()
    assert response_json["detail"] == "Provide correct permission ids"


@pytest.mark.asyncio
async def test_assign_permissions_successful(
    client, create_user_with_permissions, auth_headers, permissions
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    headers = await auth_headers(current_user)
    role = current_user.roles[0]

    response = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[permission.id for permission in permissions],
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["id"] == role.id
    assert response_json["name"] == "Test Role"
    assert response_json["key"] == "test_role"
    assert {permission["name"] for permission in response_json["permissions"]} == {
        "roles:access",
        "roles:assign_permissions",
        "candidates:view",
        "candidates:create",
        "candidates:update",
    }


def _assert_validation_error(response, loc: tuple[str, ...]) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(tuple(error["loc"]) == loc for error in errors)


@pytest.mark.asyncio
async def test_assign_permissions_to_another_role(
    client, create_user_with_permissions, auth_headers, permissions
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:view", "roles:assign_permissions"]
    )
    target_role = await RoleFactory.create_async(name="Role One", key="role_one")
    headers = await auth_headers(current_user)

    response = client.post(
        f"/admin/roles/{target_role.id}/assign_permissions",
        headers=headers,
        json=[permission.id for permission in permissions],
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["id"] == target_role.id
    assert response_json["name"] == "Role One"
    assert response_json["key"] == "role_one"
    assert {permission["name"] for permission in response_json["permissions"]} == {
        "candidates:view",
        "candidates:create",
        "candidates:update",
    }


@pytest.mark.asyncio
async def test_role_with_assigned_permissions_is_listed(
    client, create_user_with_permissions, auth_headers, permissions
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:view", "roles:assign_permissions"]
    )
    target_role = await RoleFactory.create_async(name="Role One", key="role_one")
    headers = await auth_headers(current_user)

    assigned = client.post(
        f"/admin/roles/{target_role.id}/assign_permissions",
        headers=headers,
        json=[permission.id for permission in permissions],
    )
    assert assigned.status_code == 200

    listed = client.get("/admin/roles", headers=headers)

    assert listed.status_code == 200
    assert {role["name"]: role["key"] for role in listed.json()} == {
        "Test Role": "test_role",
        "Role One": "role_one",
    }


@pytest.mark.asyncio
async def test_assign_permissions_with_partially_invalid_permission_ids(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    role = await RoleFactory.create_async(name="Role One", key="role_one")
    kept_permission = await PermissionFactory.create_async(name="candidates:view")
    rejected_permission = await PermissionFactory.create_async(name="candidates:create")
    headers = await auth_headers(current_user)

    seeded = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[kept_permission.id],
    )
    assert seeded.status_code == 200

    response = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[rejected_permission.id, 999],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Provide correct permission ids"

    unchanged = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[kept_permission.id],
    )
    assert unchanged.status_code == 200
    assert [permission["name"] for permission in unchanged.json()["permissions"]] == [
        "candidates:view"
    ]


@pytest.mark.asyncio
async def test_assign_existing_permission_does_not_duplicate(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    role = await RoleFactory.create_async(name="Role One", key="role_one")
    permission = await PermissionFactory.create_async(name="candidates:view")
    headers = await auth_headers(current_user)

    first = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[permission.id],
    )
    assert first.status_code == 200

    second = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[permission.id],
    )

    assert second.status_code == 200
    assert [item["name"] for item in second.json()["permissions"]] == [
        "candidates:view"
    ]


@pytest.mark.asyncio
async def test_assign_permissions_rejects_empty_permission_ids(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    headers = await auth_headers(current_user)
    role = current_user.roles[0]

    response = client.post(
        f"/admin/roles/{role.id}/assign_permissions",
        headers=headers,
        json=[],
    )

    _assert_validation_error(response, ("body",))


@pytest.mark.asyncio
async def test_assign_permissions_rejects_non_positive_role_id(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["roles:access", "roles:assign_permissions"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        "/admin/roles/0/assign_permissions",
        headers=headers,
        json=[1],
    )

    _assert_validation_error(response, ("path", "id"))


@pytest.mark.parametrize(
    ("payload", "loc"),
    [
        pytest.param({"name": "Ab"}, ("body", "name"), id="name-too-short"),
        pytest.param(
            {"name": "Role 1"},
            ("body", "name"),
            id="name-invalid-characters",
        ),
        pytest.param({}, ("body", "name"), id="missing-name"),
    ],
)
@pytest.mark.asyncio
async def test_create_role_rejects_invalid_name(
    client, create_user_with_permissions, auth_headers, payload, loc
):
    current_user = await create_user_with_permissions(["roles:access", "roles:create"])
    headers = await auth_headers(current_user)

    response = client.post("/admin/roles", headers=headers, json=payload)

    _assert_validation_error(response, loc)


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        pytest.param("get", "/admin/roles", None, id="list-roles"),
        pytest.param(
            "post",
            "/admin/roles",
            {"name": "Hiring Manager"},
            id="create-role",
        ),
        pytest.param(
            "post",
            "/admin/roles/1/assign_permissions",
            [1],
            id="assign-permissions",
        ),
    ],
)
def test_roles_routes_require_authentication(client, method, path, json_body):
    kwargs = {} if json_body is None else {"json": json_body}
    response = client.request(method, path, **kwargs)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.parametrize(
    ("permissions", "method", "path"),
    [
        pytest.param(
            ["roles:access"],
            "get",
            "/admin/roles",
            id="list-access-only",
        ),
        pytest.param(
            ["roles:access"],
            "post",
            "/admin/roles",
            id="create-access-only",
        ),
        pytest.param(
            ["roles:access"],
            "post",
            "/admin/roles/{role_id}/assign_permissions",
            id="assign-access-only",
        ),
        pytest.param(
            ["roles:view"],
            "get",
            "/admin/roles",
            id="list-without-access",
        ),
        pytest.param(
            ["roles:create"],
            "post",
            "/admin/roles",
            id="create-without-access",
        ),
        pytest.param(
            ["roles:assign_permissions"],
            "post",
            "/admin/roles/{role_id}/assign_permissions",
            id="assign-without-access",
        ),
        pytest.param(
            ["roles:access", "roles:view"],
            "post",
            "/admin/roles",
            id="create-without-create-permission",
        ),
        pytest.param(
            ["roles:access", "roles:view"],
            "post",
            "/admin/roles/{role_id}/assign_permissions",
            id="assign-without-assign-permission",
        ),
        pytest.param(
            ["roles:access", "roles:create"],
            "get",
            "/admin/roles",
            id="list-without-view-permission",
        ),
        pytest.param(
            ["roles:access", "roles:assign_permissions"],
            "get",
            "/admin/roles",
            id="list-without-view-with-assign",
        ),
        pytest.param(
            ["roles:access", "roles:create"],
            "post",
            "/admin/roles/{role_id}/assign_permissions",
            id="assign-without-assign-with-create",
        ),
    ],
)
@pytest.mark.asyncio
async def test_roles_routes_forbidden_without_required_permission(
    client, create_user_with_permissions, auth_headers, permissions, method, path
):
    current_user = await create_user_with_permissions(permissions)
    headers = await auth_headers(current_user)
    kwargs = {"headers": headers}
    if "assign_permissions" in path:
        kwargs["json"] = [1]
    elif method == "post":
        kwargs["json"] = {"name": "Hiring Manager"}

    response = client.request(
        method,
        path.format(role_id=current_user.roles[0].id),
        **kwargs,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"
