import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from main import app


@pytest.mark.asyncio
async def test_create_and_get_pereval(transaction, create_pereval):
    submit_data = create_pereval()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post("/submit/submitData", json=submit_data)

        assert response.status_code == 200, f"Failed to create pereval: {response.text}"
        data = response.json()
        assert "share_link" in data, "Response does not contain share_link"
        assert data["message"] == "Данные успешно отправлены", f"Unexpected message: {data['message']}"

        pereval_id = data["share_link"].split("/")[-1]

        response_get = await client.get(f"/submit/submitData/{pereval_id}")
        assert response_get.status_code == 200, f"Failed to get pereval: {response_get.text}"

        pereval_data = response_get.json()
        assert pereval_data["title"] == submit_data["title"], "Titles do not match"
