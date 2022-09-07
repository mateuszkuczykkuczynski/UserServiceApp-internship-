import pytest
from fastapi.testclient import TestClient
from UserServiceApp.main import app

client = TestClient(app)


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


def generate_post_response_user():
    return {
        "countryCode": "41922",
        "dateOfBirth": "06.06.2000",
        "firstName": "Matt",
        "lastName": "Bubel",
        "nickname": "Booble",
        "gender": "male",
        "email": "booble@gmail.com",
        "id": 2}


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
        "countryCode": "6161161611",
        "dateOfBirth": "12.07.1998",
        "firstName": "Mateuszek",
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


def test_add_a_new_user():
    response = client.post("/v1/users",
                           json={
                               "countryCode": "41922",
                               "dateOfBirth": "06.06.2000",
                               "firstName": "Matt",
                               "lastName": "Bubel",
                               "nickname": "Booble",
                               "gender": "male",
                               "email": "booble@gmail.com"
                           },
                           )
    assert response.status_code == 200
    assert response.json() == generate_post_response_user()


def test_add_a_new_user_invalid_method():
    response = client.put("/v1/users")
    assert response.status_code == 405
    assert response.json() == method_not_allowed()


def test_get_user_info():
    response = client.get("/v1/users/1")
    assert response.status_code == 200
    assert response.json() == generate_get_response_user()


def test_get_user_info_invalid_id():
    response = client.get("/v1/users/100")
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_get_user_info_invalid_method():
    response = client.post("/v1/users/1")
    assert response.status_code == 405
    assert response.json() == method_not_allowed()


def test_update_user_info():
    response = client.put("/v1/users/1",
                          json={
                              "countryCode": "6161161611",
                              "dateOfBirth": "12.07.1998",
                              "firstName": "Mateuszek",
                              "lastName": "Kuczynski",
                              "nickname": "Kuczyk",
                              "gender": "male",
                              "email": "mati@gmail.com",
                          },
                          )
    assert response.status_code == 200
    assert response.json() == generate_put_response_user()


def test_update_user_info_invalid_id():
    response = client.put("/v1/users/12",
                          json={
                              "countryCode": "6161161611",
                              "dateOfBirth": "12.07.1998",
                              "firstName": "Mateuszek",
                              "lastName": "Kuczynski",
                              "nickname": "Kuczyk",
                              "gender": "male",
                              "email": "mati@gmail.com",
                          })
    assert response.status_code == 404
    assert response.json() == user_not_found()


def test_delete_user():
    response = client.delete("/v1/users/2")
    assert response.status_code == 200


def test_delete_user_invalid_id():
    response = client.delete("/v1/users/1234")
    assert response.status_code == 404
    assert response.json() == user_not_found()


@pytest.mark.parametrize("test_input,expected,status_code",
                         [('/v1/users', generate_get_response_users_list(), 200),
                          ('v1/users?ids=1', generate_get_response_users_list(), 200),
                          ('v1/users?emails=mati%40gmail.com', generate_get_response_users_list(), 200),
                          ('v1/users?nicknames=Kuczyk', generate_get_response_users_list(), 200),
                          ('v1/users?ids=12345', user_not_found(), 404),
                          ('v1/users?emails=matikuku%40gmail.com', user_not_found(), 404),
                          ('v1/users?nicknames=Kuczykowek', user_not_found(), 404),
                          ('v1/users?ids=1&emails=mati%40gmail.com&nicknames=Kuczyk', mutual_exclusivity(), 400),
                          ('v1/users?ids=1&emails=mati%40gmail.com', mutual_exclusivity(), 400),
                          ('v1/users?ids=1&nicknames=Kuczyk', mutual_exclusivity(), 400),
                          ('v1/users?emails=mati%40gmail.com&nicknames=Kuczyk', mutual_exclusivity(), 400)])
def test_search_and_filter_users(test_input, expected, status_code):
    response = client.get(test_input)
    assert response.status_code == status_code
    assert response.json() == expected
