import pytest


@pytest.mark.asyncio
async def test_create_task(tasks_client):
    client, current_user = tasks_client

    response = await client.post(
        "/tasks/",
        json={"title": "Write tests",
            "description": "Cover API routes",
            "priority": 5,
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] is not None
    assert response.json()["title"] == "Write tests"
    assert response.json()["description"] == "Cover API routes"
    assert response.json()["priority"] == 5
    assert response.json()["status"] == "pending"
    assert response.json()["owner_id"] == current_user.id
    assert "created_at" in response.json()


@pytest.mark.asyncio
async def test_read_tasks_returns_created_tasks(tasks_client):
    client, current_user = tasks_client
    await client.post( "/tasks/",
        json={"title": "First task", "description": "one", "priority": 1},
    )
    await client.post("/tasks/",
        json={"title": "Second task", "description": "two", "priority": 2},
    )

    response = await client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {task["owner_id"] for task in response.json()} == {current_user.id}
    assert {task["title"] for task in response.json()} == {"First task", "Second task"}


@pytest.mark.asyncio
async def test_read_tasks_validates_sort_by(tasks_client):
    client, _ = tasks_client
    response = await client.get("/tasks/", params={"sort_by": "unknown"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_task_returns_404_for_missing_task(tasks_client):
    client, _ = tasks_client
    response = await client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_update_task(tasks_client):
    client, _ = tasks_client
    create_response = await client.post("/tasks/",
        json={"title": "Old title", "description": "old", "priority": 1},
    )
    task_id = create_response.json()["id"]

    response = await client.patch(f"/tasks/{task_id}",
        json={"title": "New title", "priority": 10},
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "New title"
    assert response.json()["priority"] == 10


@pytest.mark.asyncio
async def test_update_task_returns_404_for_missing_task(tasks_client):
    client, _ = tasks_client
    response = await client.patch("/tasks/999",
        json={"title": "New title"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

@pytest.mark.asyncio
async def test_delete_task(tasks_client):
    client, _ = tasks_client
    create_response = await client.post("/tasks/",
        json={"title": "Task to delete", "description": "bye"},
    )
    task_id = create_response.json()["id"]
    response = await client.delete(f"/tasks/{task_id}")
    get_response = await client.get(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_task_returns_404_for_missing_task(tasks_client):
    client, _ = tasks_client
    response = await client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_search_tasks(tasks_client):
    client, _ = tasks_client
    await client.post( "/tasks/",
        json={"title": "Read FastAPI docs", "description": "Study routing"},
                       )
    await client.post( "/tasks/",
        json={"title": "Write tests", "description": "Cover FastAPI app"},
    )
    await client.post( "/tasks/",
        json={"title": "Buy groceries", "description": "Milk and bread"},
    )

    response = await client.get("/tasks/search", params={"q": "FastAPI"})

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {task["title"] for task in response.json()} == {
        "Read FastAPI docs",
        "Write tests",
    }


@pytest.mark.asyncio
async def test_top_priority_tasks_validates_limit(tasks_client):
    client, _ = tasks_client
    response = await client.get("/tasks/top", params={"n": 0})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_top_priority_tasks_returns_limited_results(tasks_client):
    client, _ = tasks_client
    await client.post("/tasks/",
        json={"title": "Low", "description": "low", "priority": 1},
    )
    await client.post("/tasks/",
        json={"title": "High", "description": "high", "priority": 10},
    )
    await client.post("/tasks/",
        json={"title": "Medium", "description": "medium", "priority": 5},
    )

    response = await client.get("/tasks/top", params={"n": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert [task["title"] for task in response.json()] == ["High", "Medium"]
