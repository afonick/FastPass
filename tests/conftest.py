import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db import async_session_null_pool, InternalError


@pytest.fixture(scope="session")
async def test_session():
    async with async_session_null_pool() as session:
        try:
            yield session
        except InternalError:
            await session.rollback()


@pytest.fixture(scope="session")
async def transaction(test_session: AsyncSession):
    async with test_session.begin():
        yield test_session
    await test_session.rollback()


# Фикстура для создания перевала
@pytest.fixture
def create_pereval():
    def generate_pereval():
        from faker import Faker
        import random

        fake = Faker()
        return {
            "user": {
                "email": fake.email(),
                "fam": fake.last_name(),
                "name": fake.first_name(),
                "otc": fake.first_name_male(),
                "phone": fake.phone_number(),
            },
            "title": f"Test Pereval {random.randint(3000, 10000)}",
            "beauty_title": f"Красивый перевал {random.randint(1, 1000)}",
            "other_titles": f"Переход {random.randint(1, 1000)}, Тур 2024",
            "connect": fake.text(max_nb_chars=50),
            "coords": {
                "latitude": round(random.uniform(-90, 90), 4),
                "longitude": round(random.uniform(-180, 180), 4),
                "height": random.randint(100, 5000),
            },
            "level": {
                "winter": random.choice(["3A", "3B", "2A", "2B"]),
                "summer": random.choice(["2A", "2B", "1A", "1B"]),
                "autumn": random.choice(["1A", "1B", "2A"]),
                "spring": random.choice(["2A", "2B", "1A"]),
            },
            "images": [
                {"url": fake.image_url(), "title": f"Image {random.randint(1, 100)}"},
                {"url": fake.image_url(), "title": f"Image {random.randint(101, 200)}"},
            ],
        }

    return generate_pereval
