import uvicorn
from fastapi import FastAPI, Query, status, HTTPException, Request, Response
from fastapi_redis_cache import FastApiRedisCache, cache
from fastapi.encoders import jsonable_encoder
from redis import Redis
from sqlmodel import Session, SQLModel, select, or_
from models import User, GetUser, PostUser
from database import engine


app = FastAPI()

REDIS_CONNECTION_STRING = 'redis://redis:6379'


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def delete_cache(id: int):
    r = Redis('redis')
    users = [user for user in r.scan_iter('*')]
    for user in users:
        decoded_value = r.get(user).decode('utf-8')
        if f'\"id\": {id}' in decoded_value:
            r.delete(user)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    redis_cache = FastApiRedisCache()
    redis_cache.init(host_url=REDIS_CONNECTION_STRING, prefix='users_cache',
                     response_header='X-Users-Cache', ignore_arg_types=[Request, Response, Session])


responses = {
    400: {"description": "Invalid Parameter Received"},
    404: {"description": "User Not Found"},
    405: {"description": "Method Not Allowed"},
    500: {"description": "Internal Server Error"},
    503: {"description": "Service Unavailable"}
}


def find_user_by_id_helper(ids):
    return select(User).where(or_(User.id == user_id for user_id in ids))


def find_user_by_nickname_helper(nicknames):
    return select(User).where((User.nickname == nicknames))


def find_user_by_email_helper(emails):
    return select(User).where((User.email == emails))


@app.post("/v2/users", responses=responses, response_model=GetUser, status_code=status.HTTP_200_OK)
async def add_a_new_user(user: PostUser):
    with Session(engine) as session:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        delete_cache(db_user.id)
        return db_user


@app.get("/v2/users/{id}", responses=responses, response_model=GetUser, status_code=status.HTTP_200_OK)
@cache(expire=60)
async def get_user_info(response: Response, id):
    with Session(engine) as session:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
        encoded_user = jsonable_encoder(user)
        return encoded_user


@app.put("/v2/users/{id}", responses=responses, response_model=GetUser, status_code=status.HTTP_200_OK)
async def update_user_info(id, user: PostUser):
    with Session(engine) as session:
        db_user = session.get(User, id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        delete_cache(db_user.id)
        return db_user


@app.delete("/v2/users/{id}", responses=responses, status_code=200)
async def delete_user(id):
    with Session(engine) as session:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
        session.delete(user)
        session.commit()
        delete_cache(user.id)


@app.get("/v2/users", responses=responses, status_code=200)
@cache(expire=60)
async def search_and_filter_users(response: Response, ids: list[int] = Query(default=None), emails: str = Query(default=None),
                                  nicknames: str = Query(default=None)) -> list:
    with Session(engine) as session:
        query_list = [ids, emails, nicknames]
        sorted_query_list = [i for i in query_list if i is not None]
        if len(sorted_query_list) == 0:
            results = select(User)
        elif len(sorted_query_list) == 1:
            if emails:
                results = find_user_by_email_helper(emails)
            if nicknames:
                results = find_user_by_nickname_helper(nicknames)
            if ids:
                results = find_user_by_id_helper(ids)
        elif len(sorted_query_list) > 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Request cannot be processed because parameters are mutually exclusive.")
        users = session.exec(results).all()
        encoded_user = jsonable_encoder(users)
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
        else:
            return encoded_user


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
