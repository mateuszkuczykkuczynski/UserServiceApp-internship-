import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from UserServiceApp.models import User
from UserServiceApp.main import app


POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password"
POSTGRES_HOST = "db"
POSTGRES_PORT = 5432
POSTGRES_DB_NAME = "user_db"

client = TestClient(app)


@pytest.fixture(name="session")
def session_fixture():
    TEST_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/" \
                        f"{POSTGRES_DB_NAME}"
    engine = create_engine(TEST_DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def create_test_user():
    user = User(countryCode="61611", dateOfBirth="12.07.1998", firstName="Mateusz", lastName="Kuczynski",
                nickname="Kuczyk", gender="male", email="mati@gmail.com", id=1)
    return user


def generate_post_user():
    return {
        "countryCode": "61611",
        "dateOfBirth": "12.07.1998",
        "firstName": "Mateusz",
        "lastName": "Kuczynski",
        "nickname": "Kuczyk",
        "gender": "male",
        "email": "mati@gmail.com"}


def generate_get_response_user():
    return {
        "countryCode": "61611",
        "dateOfBirth": "12.07.1998",
        "firstName": "Mateusz",
        "lastName": "Kuczynski",
        "nickname": "Kuczyk",
        "gender": "male",
        "email": "mati@gmail.com",
        "id": 1}


def generate_put_user_request():
    return {
        "countryCode": "6161161611",
        "dateOfBirth": "12.07.1998",
        "firstName": "Mateuszek",
        "lastName": "Kuczynski",
        "nickname": "Kuczyk",
        "gender": "male",
        "email": "mati@gmail.com"}


def generate_put_response_user():
    return {
        "countryCode": "6161161611",
        "dateOfBirth": "12.07.1998",
        "firstName": "Mateuszek",
        "lastName": "Kuczynski",
        "nickname": "Kuczyk",
        "gender": "male",
        "email": "mati@gmail.com",
        "id": 1}


def generate_get_response_users_list():
    return [{
        "countryCode": "61611",
        "dateOfBirth": "12.07.1998",
        "firstName": "Mateusz",
        "lastName": "Kuczynski",
        "nickname": "Kuczyk",
        "gender": "male",
        "email": "mati@gmail.com",
        "id": 1}]


def user_not_found():
    return {'detail': 'User Not Found'}


def method_not_allowed():
    return {'detail': 'Method Not Allowed'}


def mutual_exclusivity():
    return {'detail': 'Request cannot be processed because parameters are mutually exclusive.'}


def test_add_a_new_user(session: Session):
    response = client.post("/v2/users",
                           json=generate_post_user())
    data = response.json()
    assert response.status_code == 200
    assert data["countryCode"] == "61611"
    assert data["dateOfBirth"] == "12.07.1998"
    assert data["firstName"] == "Mateusz"
    assert data["lastName"] == "Kuczynski"
    assert data["nickname"] == "Kuczyk"
    assert data["gender"] == "male"
    assert data["email"] == "mati@gmail.com"
    assert data["id"] is not None
    user = session.get(User, data['id'])
    session.delete(user)
    session.commit()


def test_add_a_new_user_invalid_method():
    response = client.put("/v2/users")
    assert response.status_code == 405
    assert response.json() == method_not_allowed()


def test_get_user_info_by_id(session: Session):
    session.add(create_test_user())
    session.commit()
    response = client.get("/v2/users/1")
    assert response.status_code == 200
    assert response.json() == generate_get_response_user()
    user = session.get(User, 1)
    session.delete(user)
    session.commit()


def test_get_user_info_invalid_id():
    response = client.get("/v2/users/100")
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_get_user_info_invalid_method():
    response = client.post("/v2/users/1")
    assert response.status_code == 405
    assert response.json() == method_not_allowed()


def test_delete_user(session: Session):
    session.add(create_test_user())
    session.commit()
    response = client.delete("/v2/users/1")
    assert response.status_code == 200


def test_delete_user_invalid_id():
    response = client.delete("/v2/users/1234")
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_update_user_info(session: Session):
    session.add(create_test_user())
    session.commit()
    response = client.put("/v2/users/1", json=generate_put_user_request())
    assert response.status_code == 200
    assert response.json() == generate_put_response_user()
    user = session.get(User, 1)
    session.delete(user)
    session.commit()


def test_update_user_info_invalid_id(session: Session):
    session.add(create_test_user())
    session.commit()
    response = client.put("/v2/users/12", json=generate_put_user_request())
    assert response.status_code == 404
    assert response.json() == user_not_found()
    user = session.get(User, 1)
    session.delete(user)
    session.commit()


@pytest.mark.parametrize("test_input,expected,status_code",
                         [('/v2/users', generate_get_response_users_list(), 200),
                          ('v2/users?ids=1', generate_get_response_users_list(), 200),
                          ('v2/users?emails=mati%40gmail.com', generate_get_response_users_list(), 200),
                          ('v2/users?nicknames=Kuczyk', generate_get_response_users_list(), 200),
                          ('v2/users?ids=12345', user_not_found(), 404),
                          ('v2/users?emails=matikuku%40gmail.com', user_not_found(), 404),
                          ('v2/users?nicknames=Kuczykowek', user_not_found(), 404),
                          ('v2/users?ids=1&emails=mati%40gmail.com&nicknames=Kuczyk', mutual_exclusivity(), 400),
                          ('v2/users?ids=1&emails=mati%40gmail.com', mutual_exclusivity(), 400),
                          ('v2/users?ids=1&nicknames=Kuczyk', mutual_exclusivity(), 400),
                          ('v2/users?emails=mati%40gmail.com&nicknames=Kuczyk', mutual_exclusivity(), 400)])
def test_search_and_filter_users(test_input, expected, status_code, session: Session):
    session.add(create_test_user())
    session.commit()
    response = client.get(test_input)
    assert response.status_code == status_code
    assert response.json() == expected
    user = session.get(User, 1)
    session.delete(user)
    session.commit()

