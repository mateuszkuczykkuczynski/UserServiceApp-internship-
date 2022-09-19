import uvicorn
from fastapi import FastAPI, Query, status, HTTPException
from sqlmodel import Session, SQLModel, select
from models import User, GetUser, PostUser
from database import engine


app = FastAPI()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


responses = {
    400: {"description": "Invalid Parameter Received"},
    404: {"description": "User Not Found"},
    405: {"description": "Method Not Allowed"},
    500: {"description": "Internal Server Error"},
    503: {"description": "Service Unavailable"}
}


@app.post("/v2/users", responses=responses, response_model=GetUser, status_code=status.HTTP_200_OK)
async def add_a_new_user(user: PostUser):
    with Session(engine) as session:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.get("/v2/users/{id}", responses=responses, response_model=GetUser,  status_code=status.HTTP_200_OK)
async def get_user_info(id):
    with Session(engine) as session:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
        return user


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


@app.get("/v2/users", responses=responses, status_code=200)
async def search_and_filter_users(ids: list[int] = Query(default=None), emails: str = Query(default=None),
                                  nicknames: str = Query(default=None)) -> list:
    with Session(engine) as session:
        query_list = [ids, emails, nicknames]
        sorted_query_list = [i for i in query_list if i is not None]
        admin_searches_list = []

        all_users = session.exec(select(User)).all()
        if len(sorted_query_list) == 0:
            return all_users
        elif len(sorted_query_list) == 1:
            if emails:
                statement = select(User).where(User.email == emails)
                results = session.exec(statement).all()
                if results:
                    return results
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found")
            if nicknames:
                statement = select(User).where(User.nickname == nicknames)
                results = session.exec(statement).all()
                if results:
                    return results
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found")
            if ids:
                for i in ids:
                    statement = session.get(User, i)
                    admin_searches_list.append(statement)
                if statement:
                    return admin_searches_list
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found")
        elif len(sorted_query_list) > 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Request cannot be processed because parameters are mutually exclusive.")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)


