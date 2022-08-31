import uvicorn
from fastapi import FastAPI, Query, status, HTTPException
from schemas import User, UserWithoutId

app = FastAPI()

UsersList = {}

id = 0

responses = {
    400: {"description": "Invalid Parameter Received"},
    404: {"description": "User Not Found"},
    405: {"description": "Method Not Allowed"},
    500: {"description": "Internal Server Error"},
    503: {"description": "Service Unavailable"}
}


@app.post("/v1/users", responses=responses, response_model=User, status_code=status.HTTP_200_OK)
async def add_a_new_user(user: UserWithoutId) -> User:
    global id

    for value in user.dict():
        if not isinstance(user.dict()[value], str):
            raise HTTPException(status_code=400,
                                detail="Invalid Parameter Received")
    id += 1
    new_user = User(countryCode=user.countryCode, dateOfBirth=user.dateOfBirth,
                    firstName=user.firstName, lastName=user.lastName, nickname=user.nickname,
                    gender=user.gender, email=user.email, id=id
                    )
    UsersList.update({id: new_user.dict()})
    return new_user


@app.get("/v1/users/{id}", responses=responses, status_code=status.HTTP_200_OK)
async def get_user_info(id: int) -> User:
    if id in UsersList.keys():
        return UsersList[id]
    elif id not in UsersList.keys():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")


@app.put("/v1/users/{id}", response_model=User, responses=responses, status_code=status.HTTP_200_OK)
async def update_user_info(id: int, updated_user_data: UserWithoutId) -> User:
    if id in UsersList.keys():
        UsersList[id]['firstName'] = updated_user_data.firstName
        UsersList[id]['lastName'] = updated_user_data.lastName
        UsersList[id]['gender'] = updated_user_data.gender
        UsersList[id]['countryCode'] = updated_user_data.countryCode
        UsersList[id]['email'] = updated_user_data.email
        UsersList[id]['nickname'] = updated_user_data.nickname
        UsersList[id]['dateOfBirth'] = updated_user_data.dateOfBirth
        return UsersList.get(id)
    elif id not in UsersList.keys():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")


@app.delete("/v1/users/{id}", responses=responses, status_code=200)
async def delete_user(id: int) -> None:
    if id in UsersList.keys():
        UsersList.pop(id)
    elif id not in UsersList.keys():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")


@app.get("/v1/users", responses=responses, status_code=200)
async def search_and_filter_users(ids: list[int] = Query(default=None), emails: str = Query(default=None),
                                  nicknames: str = Query(default=None)) -> list:
    query_list = [ids, emails, nicknames]
    sorted_query_list = [i for i in query_list if i is not None]
    admin_searches_list = []

    if len(sorted_query_list) == 0:
        return list(UsersList.values())
    elif len(sorted_query_list) == 1:
        if emails:
            for value in UsersList.values():
                if value['email'] == emails:
                    admin_searches_list.append(value)
            if len(admin_searches_list) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found")
        if nicknames:
            for value in UsersList.values():
                if value['nickname'] == nicknames:
                    admin_searches_list.append(value)
            if len(admin_searches_list) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found")
        if ids:
            for value in UsersList.values():
                for i in ids:
                    if value['id'] == i:
                        admin_searches_list.append(value)
            if len(admin_searches_list) != len(ids):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found")
    elif len(sorted_query_list) > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Request cannot be processed because parameters are mutually exclusive.")
    return admin_searches_list

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
