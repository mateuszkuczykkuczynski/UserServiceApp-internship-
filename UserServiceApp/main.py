import json
import uvicorn
from fastapi import FastAPI, Query, status, HTTPException, Request, Response
from fastapi_redis_cache import FastApiRedisCache
from fastapi.encoders import jsonable_encoder
from redis import Redis
from sqlmodel import Session, SQLModel, select
from models import User, GetUser, PostUser
from database import engine


app = FastAPI()

REDIS_CONNECTION_STRING = 'redis://redis:6379'


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


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


def find_user_by_nickname_helper(nicknames: str, session: Session):
    result = session.exec(select(User).where(User.nickname == nicknames)).all()
    index = session.exec(select(User.id).where(User.nickname == nicknames)).all()
    return result, index


def find_user_by_email_helper(emails: str, session: Session):
    result = session.exec(select(User).where(User.email == emails)).all()
    index = session.exec(select(User.id).where(User.email == emails)).all()
    return result, index


def find_user_by_id_helper(index_list: list[int], session: Session):
    results_list = []
    for index in index_list:
        result = session.get(User, index)
        if result:
            results_list.append(session.get(User, index))
    return results_list


def find_all_users_helper(session: Session):
    users = select(User)
    result = session.exec(users).all()
    index = session.exec(select(User.id)).all()
    return result, index


def create_cache_user_key(id, user_data):
    try:
        FastApiRedisCache().add_to_cache(key=f"user_cache:main.create_key_user_id={id}", value=user_data, expire=100)
    except AttributeError as error:
        print(error)


def get_user_info_from_cache(id):
    r = Redis('redis')
    user_info = r.get(f"user_cache:main.get_user_key_id={id}")
    if user_info:
        user_info = json.loads(user_info)
        return user_info


def delete_caches(index):
    r = Redis('redis')
    keys = r.keys(f'*{index}*')
    r.delete(*keys)


@app.post("/v2/users", responses=responses, response_model=GetUser, status_code=status.HTTP_200_OK)
async def add_a_new_user(user: PostUser):
    with Session(engine) as session:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    try:
        delete_caches(db_user.id)
    except Exception as error:
        print(error)
    return db_user


@app.get("/v2/users/{id}", responses=responses, response_model=GetUser, status_code=status.HTTP_200_OK)
async def get_user_info(response: Response, id):
    with Session(engine) as session:
        if get_user_info_from_cache(id):
            encoded_user = get_user_info_from_cache(id)
        else:
            user = session.get(User, id)
            encoded_user = jsonable_encoder(user)
            create_cache_user_key(id, encoded_user)
    if not encoded_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")
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
    try:
        delete_caches(id)
    except Exception as error:
        print(error)
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
    try:
        delete_caches(id)
    except Exception as error:
        print(error)


@app.get("/v2/users", responses=responses, status_code=200)
async def search_and_filter_users(response: Response, ids: list[int] = Query(default=None), emails: str = Query(default=None),
                                  nicknames: str = Query(default=None)) -> list:
    with Session(engine) as session:
        query_list = [ids, emails, nicknames]
        sorted_query_list = [i for i in query_list if i is not None]
        if len(sorted_query_list) == 0:
            result, index = find_all_users_helper(session)
        elif len(sorted_query_list) == 1:
            if emails:
                result, index = find_user_by_email_helper(emails, session)
            if nicknames:
                result, index = find_user_by_nickname_helper(nicknames, session)
            if ids:
                result = find_user_by_id_helper(ids, session)
                index = ids
        elif len(sorted_query_list) > 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Request cannot be processed because parameters are mutually exclusive.")
    if get_user_info_from_cache(index):
        decoded_results = get_user_info_from_cache(index)
    else:
        decoded_results = jsonable_encoder(result)
        create_cache_user_key(index, decoded_results)
    if not decoded_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")
    else:
        return decoded_results


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
