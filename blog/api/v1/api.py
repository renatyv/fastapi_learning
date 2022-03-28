from typing import Union, Optional, Any

from fastapi import FastAPI, Query, Path, Body, HTTPException, Depends, APIRouter
from sqlalchemy.engine import Connection
from blog.http_status_codes import HttpStatusCode

from blog import database
from blog.model import user
from blog.model import post
from loguru import logger

api_router = APIRouter()


@api_router.get("/users", status_code=HttpStatusCode.OK.value, response_model=list[user.User])
def users(skip: int = Query(0, ge=0.0, example=2),
          limit: int = 10,
          db_connection: Connection = Depends(database.get_database_connection)) -> Any:
    """get all users
    :param skip. skip >= 0. optional
    :param limit. default 10. optional
    """
    return user.get_all_users(db_connection, skip=skip, limit=limit)


@api_router.get("/users/{user_id}", status_code=HttpStatusCode.FOUND.value, response_model=Optional[user.User])
def get_user(user_id: int = Path(..., ge=0.0),
             db_connection: Connection = Depends(database.get_database_connection)) -> Optional[user.User]:
    """get specific user
    :param user_id is required, greater than 0
    """
    found_user = user.get_user_by_id(user_id, db_connection)
    if found_user:
        return found_user
    else:
        raise HTTPException(status_code=HttpStatusCode.NOT_FOUND.value)


@api_router.post("/users/",status_code=HttpStatusCode.OK.value)
def create_user(username: str = Body(..., # required, no default value. = None to make optional
                                     min_length=1,
                                     max_length=10,
                                     regex='\w'),
                surname: str = Body(..., min_length=1,
                                     max_length=10,
                                     regex='\w'),
                db_connection: Connection = Depends(database.get_database_connection)) -> user.User:
    """creates a new user, returning it as a result"""
    try:
        return user.create_user(username, surname,db_connection)
    except user.DuplicateUserCreationException as e:
        logger.info('Trying to create duplicate user:'+str(e))
        raise HTTPException(status_code=HttpStatusCode.CONFLICT.value,
                            detail=str(e))


@api_router.put("/users/{user_id}", status_code=HttpStatusCode.OK.value, response_model=user.User)
def update_user_info(user_id: int,
                     name: Optional[str] = Body(None,  # not required
                                              min_length=1,
                                              max_length=10,
                                              regex='\w'),
                     surname: Optional[str] = Body(None, # optional
                                             min_length=1,
                                             max_length=10,
                                             regex='\w'),
                     db_connection: Connection = Depends(database.get_database_connection)) -> user.User:
    """Update name or surname for specific user"""
    try:
        return user.update_user(user_id, name, surname, db_connection)
    except user.UserNotFoundException as e:
        logger.info(f'Trying to update non-existent user with user_id={user_id}:'+str(e))
        raise HTTPException(status_code=HttpStatusCode.NOT_FOUND.value,
                            detail=f'user with user_id={user_id} not found')


@api_router.delete("/users/{user_id}", status_code=HttpStatusCode.OK.value)
def delete_user(user_id: int,
                db_connection: Connection = Depends(database.get_database_connection)):
    """Delete user by id.
    :raises HTTPException if user is not found, nothing is deleted"""
    try:
        user.delete_user(user_id, db_connection)
    except user.UserNotFoundException as e:
        raise HTTPException(status_code=HttpStatusCode.NOT_FOUND.value,
                            detail=f'user with user_id={user_id} not found')


@api_router.get("/posts", status_code=HttpStatusCode.OK.value, response_model=list[post.Post])
def posts(skip: int = Query(0, ge=0.0, example=2),
          limit: int = 10,
          db_connection: Connection = Depends(database.get_database_connection)) -> list[post.Post]:
    """get all posts"""
    return post.get_all_posts(db_connection, skip=skip, limit=limit)


@api_router.get("/posts/{post_id}", status_code=HttpStatusCode.FOUND.value, response_model=post.Post)
def get_post(post_id: int = Path(..., ge=0.0),  # required, no default value. = None to make optional
             db_connection: Connection = Depends(database.get_database_connection)):
    """get specific post
    :param post_id path param. post_id >= 0. required.
    """
    found_post = post.get_post_by_id(post_id, db_connection)
    if found_post:
        return found_post
    else:
        raise HTTPException(status_code=HttpStatusCode.NOT_FOUND.value)


@api_router.post("/posts/", status_code=HttpStatusCode.CREATED.value, response_model=post.Post)
def create_post(user_id: int = Body(..., ge=0),  # required, no default value. = None to make optional
                title: str = Body(..., min_length=1,
                                     max_length=300),
                body: str = Body(..., min_length=0,
                                  max_length=10000),
                db_connection: Connection = Depends(database.get_database_connection)) -> post.Post:
    """create new post
    :param user_id: may exist in users. If it does not, no error is returned, post is created"""
    try:
        return post.create_post(user_id, title, body, db_connection)
    except post.NoSuchUseridException as e:
        logger.debug(str(e))
        raise HTTPException(status_code=HttpStatusCode.NOT_ACCEPTABLE.value, detail='No user with such user_id')
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=HttpStatusCode.CONFLICT.value, detail='Unknown error')


@api_router.put("/posts/{post_id}", status_code=HttpStatusCode.OK.value, response_model=post.Post)
def update_post_info(post_id: int,
                     title: str = Body(None, min_length=1, # ... means field is optional
                                       max_length=300),
                     body: str = Body(None, min_length=0, # ... means field is optional
                                      max_length=10000),
                     db_connection: Connection = Depends(database.get_database_connection)):
    """Update title or body for specific post"""
    try:
        return post.update_post(post_id, title, body, db_connection)
    except post.PostNotFoundException as e:
        logger.info(f'Trying to update non-existent post with post_id={post_id}:' + str(e))
        raise HTTPException(status_code=HttpStatusCode.NOT_FOUND.value,
                            detail=f'Post with post_id={post_id} not found')
