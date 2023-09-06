import asyncio, os, sys
sys.path.append(os.getcwd())

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from contextlib import asynccontextmanager

from src.configs.config import DATABASE_URI
from src.models.base import Base


local_db_engine = create_async_engine(DATABASE_URI, echo=False, pool_pre_ping=True)
Session = sessionmaker(bind=local_db_engine, class_=AsyncSession, expire_on_commit=False) #фабрика сеансов

@asynccontextmanager
async def session_scope():
    async with Session() as session:
        async with session.begin(): 
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


async def recreate_database(conn: object) -> None:
    '''Пересоздает таблицы в БД'''

    await conn.run_sync(Base.metadata.drop_all) #удалить все в local_db_engine
    await conn.run_sync(Base.metadata.create_all) #создать все в local_db_engine


async def main() -> None:
    async with local_db_engine.begin() as conn: 
        await recreate_database(conn)
    await local_db_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

