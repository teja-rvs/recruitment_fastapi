import pytest

from tests.factories import PermissionFactory, RoleFactory, UserFactory


def snake_case(text: str) -> str:
    return text.lower().replace(" ", "_")


@pytest.fixture
def create_user_with_permissions():
    async def create_user(
        permissions: list[str] | None = None,
        role: str = "Test Role",
    ):
        permissions = permissions or []

        created_permissions = [
            await PermissionFactory.create_async(name=permission)
            for permission in permissions
        ]

        created_role = await RoleFactory.create_async(
            name=role,
            key=snake_case(role),
            permissions=created_permissions,
        )

        return await UserFactory.create_async(
            roles=[created_role],
        )

    return create_user


@pytest.fixture
async def users():
    return [
        await UserFactory.create_async(id=1),
        await UserFactory.create_async(id=2),
        await UserFactory.create_async(id=3),
    ]
