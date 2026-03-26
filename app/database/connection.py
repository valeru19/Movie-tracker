from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://admin:secret@localhost:27017/movies_db?authSource=admin"
    mongo_db_name: str = "movies_db"

    class Config:
        env_file = ".env"


settings = Settings()


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


db_instance = MongoDB()


async def connect_db():
    db_instance.client = AsyncIOMotorClient(settings.mongo_url)
    db_instance.db = db_instance.client[settings.mongo_db_name]

    await db_instance.db.movies.create_index("title")
    await db_instance.db.movies.create_index("year")
    await db_instance.db.movies.create_index("rating")
    await db_instance.db.movies.create_index("genre")
    await db_instance.db.movies.create_index("director")
    await db_instance.db.movies.create_index("status")
    await db_instance.db.movies.create_index("actors")

    print("✅ Connected to MongoDB")


async def close_db():
    if db_instance.client:
        db_instance.client.close()
        print("🔌 MongoDB connection closed")


def get_collection():
    return db_instance.db.movies