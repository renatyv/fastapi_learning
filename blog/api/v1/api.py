from datetime import timedelta
from typing import Union, Optional, Any

from fastapi import Query, Path, Body, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.engine import Connection
from starlette import status

from blog import database
from blog.model import user
from blog.model import post
from loguru import logger
import blog.api.v1.auth as auth
from blog.model.user import VisibleUserInfo

api_router = APIRouter()


@api_router.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db_connection: Connection = Depends(database.get_database_connection)) -> dict:
    """login form is redirected here
    :returns {"access_token": encoded_JWT_access_token, "token_type": "bearer"}
    :raises HTTPException if authentification failed"""
    try:
        logger.debug(f'username:{form_data.username}, pass:{form_data.password}')
        encoded_JWT_access_token = auth.authenticate_user(form_data.username, form_data.password, db_connection)
        return {"access_token": encoded_JWT_access_token, "token_type": "bearer"}
    except (user.UserNotFoundException, auth.PasswordDoesNotMatchException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.get("/my_user_id", status_code=status.HTTP_200_OK, response_model=int)
async def get_current_authenticated_user_id(user_id: int = Depends(auth.get_current_authenticated_user_id)):
    """authentification test. You need to be authenticated to see its result
    :returns """
    return user_id


@api_router.get("/users", status_code=status.HTTP_200_OK, response_model=list[user.VisibleUserInfo])
def get_all_users(skip: int = Query(0, ge=0.0, example=0),
                  limit: int = 10,
                  db_connection: Connection = Depends(database.get_database_connection)) -> Any:
    """get all users
    :param skip. skip >= 0. optional
    :param limit. default 10. optional
    :param auth_token OAuth2 token
    """
    return [u.user_info for u in user.get_all_users(db_connection, skip=skip, limit=limit)]


@api_router.get("/users/{user_id}", status_code=status.HTTP_302_FOUND, response_model=Optional[user.VisibleUserInfo])
def get_user(user_id: int = Path(..., ge=0.0),
             db_connection: Connection = Depends(database.get_database_connection)) -> Optional[user.User]:
    """get specific user
    :param user_id is required, greater than 0
    """
    found_user = user.get_user_by_id(user_id, db_connection)
    if found_user:
        return found_user.user_info
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.post("/users/", status_code=status.HTTP_200_OK, response_model=user.VisibleUserInfo)
def create_user(username: str = Body(..., # required, no default value. = None to make optional
                                     min_length=1,
                                     max_length=250),
                password: str = Body(..., min_length=1,
                                     max_length=300),
                email: Optional[EmailStr] = Body(None),
                name: Optional[str] = Body(None, max_length=100),
                surname: Optional[str] = Body(None, max_length=100),
                db_connection: Connection = Depends(database.get_database_connection)) -> user.VisibleUserInfo:
    """creates a new user, returning it as a result"""
    try:
        return user.create_user(username=username,
                                password_hash=auth.hash_password(password),
                                email=email,
                                name=name,
                                surname=surname,
                                db_connection=db_connection).user_info
    except user.DuplicateUserCreationException as e:
        logger.info('Trying to create duplicate user:'+str(e))
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED,
                            detail=str(e))


@api_router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=user.VisibleUserInfo)
def update_user_info(user_id: int = Depends(auth.get_current_authenticated_user_id),
                     username: Optional[str] = Body(None,  # optional, set '...' to make optional
                                                    min_length=1, max_length=250),
                     password: Optional[str] = Body(None, # optional, set '...' to make optional
                                                    min_length=1, max_length=300),
                     email: Optional[EmailStr] = Body(None),
                     name: Optional[str] = Body(None, max_length=100),
                     surname: Optional[str] = Body(None, max_length=100),
                     db_connection: Connection = Depends(database.get_database_connection)) -> VisibleUserInfo:
    """Update name or surname for specific user"""
    try:
        return user.update_user(user_id=user_id,
                                username=username,
                                password_hash=auth.hash_password(password),
                                email=email,
                                name=name,
                                surname=surname,
                                db_connection=db_connection).user_info
    except user.UserNotFoundException as e:
        logger.info(f'Trying to update non-existent user with user_id={user_id}:'+str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with user_id={user_id} not found')


@api_router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int = Depends(auth.get_current_authenticated_user_id),
                db_connection: Connection = Depends(database.get_database_connection)):
    """Delete user by id.
    :raises HTTPException if user is not found, nothing is deleted"""
    try:
        user.delete_user(user_id, db_connection)
    except user.UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with user_id={user_id} not found')


@api_router.get("/posts", status_code=status.HTTP_200_OK, response_model=list[post.Post])
def get_all_posts(skip: int = Query(0, ge=0.0, example=0),
                  limit: int = 10,
                  db_connection: Connection = Depends(database.get_database_connection)) -> list[post.Post]:
    """get all posts"""
    return post.get_all_posts(db_connection, skip=skip, limit=limit)


@api_router.get("/posts/{post_id}", status_code=status.HTTP_302_FOUND, response_model=post.Post)
def get_post(post_id: int = Path(..., ge=0.0),  # required, no default value. = None to make optional
             db_connection: Connection = Depends(database.get_database_connection)):
    """get specific post
    :param post_id path param. post_id >= 0. required.
    """
    found_post = post.get_post_by_id(post_id, db_connection)
    if found_post:
        return found_post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.post("/posts/", status_code=status.HTTP_201_CREATED, response_model=post.Post)
def create_post(user_id: int = Depends(auth.get_current_authenticated_user_id),  # required, no default value. = None to make optional
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user with such user_id')
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail='Unknown error')


@api_router.put("/posts/{post_id}", status_code=status.HTTP_200_OK, response_model=post.Post)
def update_post_info(post_id: int,
                     user_id: int = Depends(auth.get_current_authenticated_user_id),
                     title: str = Body(None, min_length=1, # ... means field is optional
                                       max_length=300),
                     body: str = Body(None, min_length=0, # ... means field is optional
                                      max_length=10000),
                     db_connection: Connection = Depends(database.get_database_connection)):
    """Update title or body for specific post"""
    try:
        return post.update_post(user_id, post_id, title, body, db_connection)
    except post.NotYourPostException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='not your post_id')
    except post.PostNotFoundException as e:
        logger.info(f'Trying to update non-existent post with post_id={post_id}:' + str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with post_id={post_id} not found')


@api_router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(post_id: int,
                user_id: int = Depends(auth.get_current_authenticated_user_id),
                db_connection: Connection = Depends(database.get_database_connection)):
    """Delete user by id.
    :raises HTTPException if user is not found, nothing is deleted"""
    try:
        post.delete_post(user_id,post_id, db_connection)
    except post.NotYourPostException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='not your post_id')
    except post.PostNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with post_id={post_id} not found')


