import pytest
from jose import jwt
from app import schemas
from app.config import settings


# def test_root(client):
#     res = client.get('/')
#     assert res.json().get('message') == 'Hello World!!!'
#     assert res.status_code == 200


def test_create_user(client):
    email = 'hello123@gmail.com'
    password = 'password123'
    res = client.post(
        '/users/', json={'email': email, 'password': password})
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == email
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        '/login', data={'username': test_user['email'], 'password': test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, [settings.algorithm])
    idx: str = payload.get("user_id")
    assert idx == test_user['id']
    assert login_res.token_type == 'bearer'
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('hello123@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('hello123@gmail.com', None, 422),
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={'username': email, 'password': password})

    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid credentials'


@pytest.mark.parametrize(
    "scope, user_scopes, denied_access", [
        (["trade"], ["trade"], False),
        (["trade"], [], True),
        (["admin"], ["admin"], False),
        (["admin"], [], True),
    ]
)
def test_update_user_permission(
        test_admin, test_user, client,
        scope, user_scopes, denied_access):
    response = client.post(
        f"/update-permission/{test_user['id']}",
        data={"scope": scope, "denied_access": denied_access,
              "current_user": test_admin}
    )
    assert response.status_code == 201
    assert test_user.scopes == user_scopes


def test_trade_access(client, test_trader):
    response = client.get("/test-trade-access/", data={"user": test_trader})
    assert response.status_code == 200

