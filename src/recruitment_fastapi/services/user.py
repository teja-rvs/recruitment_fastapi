from recruitment_fastapi.repositories.user import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def find(self, id):
        user = await self.repository.find(id)

        return user

    async def find_with_roles(self, id):
        user = await self.repository.find_with_roles(id)

        return user

    async def assign_roles(self, user, roles):
        for role in roles:
            if role not in user.roles:
                user.roles.append(role)

        return await self.repository.save(user)

    async def all(self):
        return await self.repository.all()
