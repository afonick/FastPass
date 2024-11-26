import pytest
from faker import Faker
from httpx import AsyncClient
from httpx import ASGITransport
from main import app


@pytest.mark.asyncio
async def test_get_perevals_by_full_user_data(create_pereval):
    # Создаем пользователя
    fake = Faker()
    base_user = {
        "email": fake.email(),
        "fam": fake.last_name(),
        "name": fake.first_name(),
        "otc": fake.first_name_male(),
        "phone": fake.phone_number(),
    }
    # Создаем три перевала для одного пользователя
    submit_data_list = [
        {**create_pereval(), "user": base_user} for _ in range(3)
    ]

    # Отправляем запросы на создание перевалов
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        for submit_data in submit_data_list:
            response = await client.post("/submit/submitData", json=submit_data)
            assert response.status_code == 200
            data = response.json()
            assert "share_link" in data

        # Получаем перевалы по полным данным пользователя
        query_params = (
            f"?user__email={base_user['email']}"
            f"&user__fam={base_user['fam']}"
            f"&user__name={base_user['name']}"
            f"&user__otc={base_user['otc']}"
        )
        response_get = await client.get(f"/submit/submitData/by_user/{query_params}")
        assert response_get.status_code == 200

        result = response_get.json()
        assert len(result) == 3
        assert all(
            item["user"]["email"] == base_user["email"]
            and item["user"]["fam"] == base_user["fam"]
            and item["user"]["name"] == base_user["name"]
            and item["user"]["otc"] == base_user["otc"]
            for item in result
        )
