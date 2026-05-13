# backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# URL базы берем из .env файла или используем дефолт
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://library_user:secure_password_123@localhost:5432/library_system")

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False, # Поставьте True, если хотите видеть SQL-запросы в консоли
    pool_size=10,
    max_overflow=20
)

# Фабрика сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Функция-зависимость для получения сессии в роутах
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()