# import pytest
# from fastapi.testclient import TestClient
# from sqlmodel import Session, SQLModel, create_engine
# from UserServiceApp.models import User
# from UserServiceApp.main import app
#
#
# POSTGRES_USER = "postgres"
# POSTGRES_PASSWORD = "password"
# POSTGRES_HOST = "host.docker.internal"
# POSTGRES_PORT = 5432
# POSTGRES_DB_NAME = "user_db"
#
# client = TestClient(app)
#
#
# @pytest.fixture(name="session")
# def session_fixture():
#     TEST_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/" \
#                         f"{POSTGRES_DB_NAME}"
#     engine = create_engine(TEST_DATABASE_URL, echo=True)
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         yield session
#
#
# def create_test_user():
#     user = User(countryCode="61611", dateOfBirth="12.07.1998", firstName="Mateusz", lastName="Kuczynski",
#                 nickname="Kuczyk", gender="male", email="mati@gmail.com", id=1)
#     return user
#
#
# def generate_response_user_for_db_connection():
#     return {
#         "countryCode": "61611",
#         "dateOfBirth": "12.07.1998",
#         "firstName": "Mateusz",
#         "lastName": "Kuczynski",
#         "nickname": "Kuczyk",
#         "gender": "male",
#         "email": "mati@gmail.com",
#         "id": 1}
#
#
# def test_db_connection(session: Session):
#     session.add(create_test_user())
#     session.commit()
#     user = session.get(User, 1)
#     assert user == generate_response_user_for_db_connection()
#     session.delete(user)
#     session.commit()
