import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_get_all_perevals(transaction, create_pereval):
    """
    Тест проверяет создание нескольких перевалов и получение их через общий эндпоинт.
    """
    submit_data_list = []

    # Генерация данных для 3 перевалов через фикстуру
    for _ in range(3):
        submit_data = create_pereval()  # Вызываем фикстуру как функцию
        submit_data_list.append(submit_data)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Создаем перевалы через POST-запросы
        for submit_data in submit_data_list:
            response = await client.post("/submit/submitData", json=submit_data)
            assert response.status_code == 200, f"Failed to create pereval: {response.text}"

        # Получаем список всех перевалов
        response_get_all = await client.get("/submit/submitData/")
        assert response_get_all.status_code == 200, f"Failed to get all perevals: {response_get_all.text}"

        # Проверяем, что результат - это список с ожидаемым количеством перевалов
        result = response_get_all.json()
        assert isinstance(result, list), "Expected a list of perevals"
        assert len(result) >= len(submit_data_list), f"Expected at least {len(submit_data_list)} perevals, but got {len(result)}"

        # Проверяем, что созданные перевалы есть в списке
        created_titles = {data["title"] for data in submit_data_list}
        retrieved_titles = {pereval["title"] for pereval in result if "title" in pereval}
        assert created_titles.issubset(retrieved_titles), "Not all created perevals were retrieved"
