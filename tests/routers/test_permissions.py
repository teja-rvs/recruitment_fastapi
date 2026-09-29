import pytest
import pytest_asyncio

from tests.factories import PermissionFactory

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def permissions(setup_factory_sessions):
    return [
        await PermissionFactory.create_async(name="candidates:view"),
        await PermissionFactory.create_async(name="candidates:create"),
        await PermissionFactory.create_async(name="candidates:update"),
    ]


@pytest.mark.asyncio
async def test_get_permissions(
    client, create_user_with_permissions, auth_headers, permissions
):
    granted = ["permissions:access", "permissions:view"]
    current_user = await create_user_with_permissions(granted)
    headers = await auth_headers(current_user)

    response = client.get("/admin/permissions", headers=headers)

    assert response.status_code == 200

    response_data = response.json()
    returned_by_name = {permission["name"]: permission for permission in response_data}
    assert set(returned_by_name) == {permission.name for permission in permissions} | set(
        granted
    )
    for permission in permissions:
        returned_permission = returned_by_name[permission.name]
        assert returned_permission["id"] == permission.id
        assert returned_permission["created_at"]
        assert returned_permission["updated_at"]
    for name in granted:
        returned_permission = returned_by_name[name]
        assert returned_permission["created_at"]
        assert returned_permission["updated_at"]


@pytest.mark.asyncio
async def test_create_permission(client, create_user_with_permissions, auth_headers):
    current_user = await create_user_with_permissions(
        ["permissions:access", "permissions:create", "permissions:view"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        "/admin/permissions",
        headers=headers,
        json={"model": "candidates", "permission": "view"},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["name"] == "candidates:view"
    assert response_json["created_at"]
    assert response_json["updated_at"]


@pytest.mark.asyncio
async def test_created_permission_is_listed(
    client, create_user_with_permissions, auth_headers
):
    current_user = await create_user_with_permissions(
        ["permissions:access", "permissions:create", "permissions:view"]
    )
    headers = await auth_headers(current_user)

    created = client.post(
        "/admin/permissions",
        headers=headers,
        json={"model": "candidates", "permission": "view"},
    )
    assert created.status_code == 200

    listed = client.get("/admin/permissions", headers=headers)

    assert listed.status_code == 200
    assert {permission["name"] for permission in listed.json()} == {
        "permissions:access",
        "permissions:create",
        "permissions:view",
        "candidates:view",
    }


@pytest.mark.parametrize(
    ("model", "permission"),
    [
        pytest.param("permissions", "access", id="existing-access"),
        pytest.param("permissions", "create", id="existing-create"),
    ],
)
@pytest.mark.asyncio
async def test_create_permission_when_permission_exists(
    client, create_user_with_permissions, auth_headers, model, permission
):
    current_user = await create_user_with_permissions(
        ["permissions:access", "permissions:create"]
    )
    headers = await auth_headers(current_user)

    response = client.post(
        "/admin/permissions",
        headers=headers,
        json={"model": model, "permission": permission},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Permission already exists"


def _assert_validation_error(response, loc: tuple[str, ...]) -> None:
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(tuple(error["loc"]) == loc for error in errors)


@pytest.mark.parametrize(
    ("payload", "loc"),
    [
        pytest.param(
            {"model": "ab", "permission": "view"},
            ("body", "model"),
            id="model-too-short",
        ),
        pytest.param(
            {"model": "candidates", "permission": "ab"},
            ("body", "permission"),
            id="permission-too-short",
        ),
        pytest.param(
            {"permission": "view"},
            ("body", "model"),
            id="missing-model",
        ),
        pytest.param(
            {"model": "candidates"},
            ("body", "permission"),
            id="missing-permission",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_permission_rejects_invalid_payload(
    client, create_user_with_permissions, auth_headers, payload, loc
):
    current_user = await create_user_with_permissions(
        ["permissions:access", "permissions:create"]
    )
    headers = await auth_headers(current_user)

    response = client.post("/admin/permissions", headers=headers, json=payload)

    _assert_validation_error(response, loc)


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        pytest.param("get", "/admin/permissions", None, id="list-permissions"),
        pytest.param(
            "post",
            "/admin/permissions",
            {"model": "candidates", "permission": "view"},
            id="create-permission",
        ),
    ],
)
def test_permissions_routes_require_authentication(client, method, path, json_body):
    kwargs = {} if json_body is None else {"json": json_body}
    response = client.request(method, path, **kwargs)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.parametrize(
    ("permissions", "method", "path"),
    [
        pytest.param(
            ["permissions:access"],
            "get",
            "/admin/permissions",
            id="list-access-only",
        ),
        pytest.param(
            ["permissions:access"],
            "post",
            "/admin/permissions",
            id="create-access-only",
        ),
        pytest.param(
            ["permissions:view"],
            "get",
            "/admin/permissions",
            id="list-without-access",
        ),
        pytest.param(
            ["permissions:create"],
            "post",
            "/admin/permissions",
            id="create-without-access",
        ),
        pytest.param(
            ["permissions:access", "permissions:view"],
            "post",
            "/admin/permissions",
            id="create-without-create-permission",
        ),
        pytest.param(
            ["permissions:access", "permissions:create"],
            "get",
            "/admin/permissions",
            id="list-without-view-permission",
        ),
    ],
)
@pytest.mark.asyncio
async def test_permissions_routes_forbidden_without_required_permission(
    client, create_user_with_permissions, auth_headers, permissions, method, path
):
    current_user = await create_user_with_permissions(permissions)
    headers = await auth_headers(current_user)
    kwargs = {"headers": headers}
    if method == "post":
        kwargs["json"] = {"model": "candidates", "permission": "view"}

    response = client.request(method, path, **kwargs)

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"
