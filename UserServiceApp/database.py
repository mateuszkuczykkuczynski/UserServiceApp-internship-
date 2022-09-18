from sqlmodel import create_engine


POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password"
POSTGRES_HOST = "host.docker.internal"
POSTGRES_PORT = 5432
POSTGRES_DB_NAME = "user_db"


DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

