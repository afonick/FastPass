import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from main import app
from src.models.pereval import Status


@pytest.mark.asyncio
async def test_update_pereval_status(transaction, create_pereval):
    submit_data = create_pereval()

    # Отправляем запрос на создание перевала
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response_create = await client.post("/submit/submitData", json=submit_data)
        assert response_create.status_code == 200
        data = response_create.json()
        assert "share_link" in data

        # Извлекаем pereval_id из share_link
        pereval_id = data["share_link"].split("/")[-1]
        status = Status.accepted

        # Обновляем статус перевала через параметры URL
        response_patch = await client.patch(
            f"/submit/submitData/update-status/{pereval_id}?status={status.value}"  # Параметр в URL
        )
        assert response_patch.status_code == 200

        # Проверяем, что статус обновлен
        response_get = await client.get(f"/submit/submitData/{pereval_id}")
        assert response_get.status_code == 200
        updated_data = response_get.json()

        # Проверяем, что статус в ответе совпадает с ожидаемым
        assert updated_data["status"] == status.value
