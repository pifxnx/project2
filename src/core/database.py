from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from .config import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(settings.db_url)

sessionmaker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db():
    async with sessionmaker() as session:
        yield session
