import random

import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from main import app
from faker import Faker


@pytest.mark.asyncio
async def test_update_pereval(transaction, create_pereval):
    # Создаем перевал
    fake = Faker()
    submit_data = create_pereval()

    # Отправляем запрос на создание перевала
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response_create = await client.post("/submit/submitData", json=submit_data)
        assert response_create.status_code == 200
        data = response_create.json()
        assert "share_link" in data

        # Обновляем все поля перевала, кроме данных пользователя
        pereval_id = data["share_link"].split("/")[-1]
        updated_data = {
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
                {"url": fake.image_url(), "title": fake.sentence()},
                {"url": fake.image_url(), "title": fake.sentence()}
            ]
        }

        # Отправляем запрос на обновление перевала
        response_patch = await client.patch(
            f"/submit/submitData/{pereval_id}",
            json=updated_data
        )
        assert response_patch.status_code == 200

        # Проверяем, что данные обновлены
        response_get = await client.get(f"/submit/submitData/{pereval_id}")
        assert response_get.status_code == 200
        updated_data_response = response_get.json()

        assert updated_data_response["title"] == updated_data["title"]
        assert updated_data_response["beauty_title"] == updated_data["beauty_title"]
        assert updated_data_response["other_titles"] == updated_data["other_titles"]
        assert updated_data_response["connect"] == updated_data["connect"]
        assert updated_data_response["coords"]["latitude"] == updated_data["coords"]["latitude"]
        assert updated_data_response["coords"]["longitude"] == updated_data["coords"]["longitude"]
        assert updated_data_response["coords"]["height"] == updated_data["coords"]["height"]
        assert updated_data_response["level"]["winter"] == updated_data["level"]["winter"]
        assert updated_data_response["level"]["summer"] == updated_data["level"]["summer"]
        assert updated_data_response["level"]["autumn"] == updated_data["level"]["autumn"]
        assert updated_data_response["level"]["spring"] == updated_data["level"]["spring"]
        assert len(updated_data_response["images"]) == len(updated_data["images"])
        for i, image in enumerate(updated_data["images"]):
            assert updated_data_response["images"][i]["url"] == image["url"]
            assert updated_data_response["images"][i]["title"] == image["title"]
