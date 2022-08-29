import uvicorn
from fastapi import FastAPI, Query, status, HTTPException
from schemas import User, UserWithoutId

app = FastAPI()

UsersList = []

responses = {
    400: {"description": "Invalid Parameter Received"},
    404: {"description": "User Not Found"},
    405: {"description": "Method Not Allowed"},
    500: {"description": "Internal Server Error"},
    503: {"description": "Service Unavailable"}
}


@app.post("/v1/users", responses=responses, response_model=User, status_code=status.HTTP_200_OK)
async def add_a_new_user(user: UserWithoutId) -> User:
    if len(UsersList) < 1:
        index = len(UsersList)
    else:
        index = UsersList[len(UsersList) - 1]['id']
    new_user = User(countryCode=user.countryCode, dateOfBirth=user.dateOfBirth,
                    firstName=user.firstName, lastName=user.lastName, nickname=user.nickname,
                    gender=user.gender, email=user.email, id=index + 1
                    )
    for value in user.dict().values():
        if type(value) is not str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid Parameter Received")

    UsersList.append(new_user.dict())
    return new_user


@app.get("/v1/users/{id}", responses=responses, status_code=status.HTTP_200_OK)
async def get_user_info(id: int) -> User:
    result = [user for user in UsersList if user['id'] == id]
    if type(id) is not int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Parameter Received")
    if len(result) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")
    return result[0]


@app.put("/v1/users/{id}", response_model=User, responses=responses, status_code=status.HTTP_200_OK)
async def update_user_info(id: int, updated_user_data: UserWithoutId) -> User:
    user_ids = []
    for user in UsersList:
        if user['id'] == id:
            user['firstName'] = updated_user_data.firstName
            user['lastName'] = updated_user_data.lastName
            user['gender'] = updated_user_data.gender
            user['countryCode'] = updated_user_data.countryCode
            user['email'] = updated_user_data.email
            user['nickname'] = updated_user_data.nickname
            user['dateOfBirth'] = updated_user_data.dateOfBirth
            user_ids.append(user)
            return user
    if type(id) is not int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Parameter Received")
    elif len(user_ids) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")


@app.delete("/v1/users/{id}", responses=responses, status_code=200)
async def delete_user(id: int) -> None:
    result = [user for user in UsersList if user['id'] == id]
    if result:
        user = result[0]
        UsersList.remove(user)
    elif type(id) is not int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid Parameter Received")
    elif len(result) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")


@app.get("/v1/users", responses=responses, status_code=200)
async def search_and_filter_users(ids: list[int] = Query(default=None), emails: str = Query(default=None),
                                  nicknames: str = Query(default=None)) -> list:
    admin_searches_list = []
    if not ids and not emails and not nicknames:
        for user in UsersList:
            admin_searches_list.append(user)
    elif ids and not emails and not nicknames:
        for id in ids:
            if type(id) is not int:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Invalid Parameter Received")
            for user in UsersList:
                if user['id'] == id:
                    admin_searches_list.append(user)
        if len(admin_searches_list) < 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")

    elif emails and not ids and not nicknames:
        if type(emails) is not str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid Parameter Received")
        for user in UsersList:
            if user['email'] == emails:
                admin_searches_list.append(user)
        if len(admin_searches_list) < 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
    elif nicknames and not ids and not emails:
        if type(nicknames) is not str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid Parameter Received")
        for user in UsersList:
            if user['nickname'] == nicknames:
                admin_searches_list.append(user)
        if len(admin_searches_list) < 1:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")
    elif (ids and emails and nicknames) or (ids and emails and not nicknames) \
            or (ids and nicknames and not emails) or (emails and nicknames and not ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Request cannot be processed because parameters are mutually exclusive.")
    elif len(admin_searches_list) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")
    return admin_searches_list


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
