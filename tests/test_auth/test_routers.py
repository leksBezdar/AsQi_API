from ..conftest import client

async def test_add_role():
    response = await client.post("/create_role", json={
        "name": "user",
        "is_active_subscription": False,
        "permissions": {}
    })
    
    assert response.status_code == 201

async def test_register():
    response = await client.post("/registration", json={
        "email": "user@example.com",
        "username": "string",
        "is_active": False,
        "is_superuser": False,
        "is_verified": False,
        "password": "String_11",
    })

    assert response.status_code == 201
