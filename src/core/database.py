from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from .config import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(settings.db_url)

sync_engine = create_engine(settings.db_url_sync)

session_local_async = async_sessionmaker(async_engine, expire_on_commit=False)

session_local_sync = sessionmaker(sync_engine, expire_on_commit=False)


async def get_db():
    async with session_local_async() as session:
        yield session
