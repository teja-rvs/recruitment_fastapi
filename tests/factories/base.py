from typing import Any, TypeVar

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.field_meta import FieldMeta
from polyfactory.persistence import AsyncPersistenceProtocol
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T")


class AsyncSessionPersistence(AsyncPersistenceProtocol[T]):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def save(self, data: T) -> T:
        async with self.session_factory() as session:
            session.add(data)
            await session.commit()
            await self._refresh(session, data)
            return data

    async def save_many(self, data: list[T]) -> list[T]:
        async with self.session_factory() as session:
            session.add_all(data)
            await session.commit()
            for item in data:
                await self._refresh(session, item)
            return data

    async def _refresh(self, session: AsyncSession, data: T) -> None:
        await session.refresh(data)
        if not isinstance(data, DeclarativeBase):
            return

        relationship_names = [
            relationship.key for relationship in inspect(data).mapper.relationships
        ]
        if relationship_names:
            await session.refresh(data, attribute_names=relationship_names)


class BaseTestFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __set_relationships__ = False
    __set_foreign_keys__ = False
    __set_primary_key__ = False

    @classmethod
    def get_field_value(
        cls,
        field_meta: FieldMeta,
        field_build_parameters: Any | None = None,
        build_context: Any | None = None,
    ) -> Any:
        if field_meta.name == "type":
            identity = getattr(cls.__model__, "__mapper_args__", {}).get(
                "polymorphic_identity"
            )
            if identity is not None:
                return identity

        return super().get_field_value(
            field_meta,
            field_build_parameters=field_build_parameters,
            build_context=build_context,
        )
