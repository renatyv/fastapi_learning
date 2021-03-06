from typing import Optional, Any

from fastapi import Query, Path, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette import status

from blog.dependicies import auth, database
from blog.dependicies.auth import generate_JWT_token_from_login_pass
from blog.model import user
from blog.model import post
from loguru import logger
import blog.model.auth.user_token as user_token
from blog.model.auth.user_password import NullInPusswordException
from blog.model.user import UserInfo

api_router = APIRouter()


@api_router.post("/token", status_code=status.HTTP_200_OK, response_model=auth.Token)
async def access_token_from_login_pass(
        encoded_JWT_access_token: auth.Token = Depends(generate_JWT_token_from_login_pass)) -> auth.Token:
    """login form is redirected here
    :returns {"access_token": encoded_JWT_access_token, "token_type": "bearer"}
    :raises HTTPException if authentication failed"""
    try:
        return encoded_JWT_access_token
    except (user.UserNotFoundException, user_token.PasswordDoesNotMatchException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.get("/users", status_code=status.HTTP_200_OK, response_model=list[user.UserInfo])
async def get_all_users(skip: int = Query(0, ge=0.0, example=0),
                        limit: int = 10,
                        async_db_connection: AsyncConnection = Depends(database.get_async_db_connection)) -> Any:
    """get list of all users
    :param async_db_connection:
    :param skip. skip >= 0. optional
    :param limit. default 10. optional
    """
    try:
        users = await user.get_all_users_async(async_db_connection, skip, limit)
        return [u.user_info for u in users]
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.get("/users/{user_id}",
                status_code=status.HTTP_302_FOUND,
                response_model=Optional[user.UserInfo])
def get_user(user_id: int = Path(..., ge=0.0),
             db_connection: Connection = Depends(database.get_database_connection)) -> Optional[user.UserInfo]:
    """get specific user
    :param db_connection:
    :param user_id is required, greater than 0
    """
    try:
        found_user = user.get_user_by_id(user_id, db_connection)
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if found_user:
        return found_user.user_info
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


class ReturnedUserInfo(BaseModel):
    user_id: int
    user_info: user.UserInfo


@api_router.post("/users/", status_code=status.HTTP_200_OK, response_model=ReturnedUserInfo)
def create_user(user_create_data: user.UserCreationData,
                db_connection: Connection = Depends(database.get_database_connection)) -> ReturnedUserInfo:
    """creates a new user, returning it as a result"""
    try:
        created_user: user.User = user.create_user(db_connection, user_create_data)
        return ReturnedUserInfo(user_id=created_user.user_id, user_info=created_user.user_info)
    except user.DuplicateUserCreationException as e:
        logger.info('Trying to create duplicate username:{}', user_create_data.user_info.username)
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED,
                            detail=str(e))
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.put("/users", status_code=status.HTTP_200_OK, response_model=user.UserInfo)
def update_user_info(user_info: user.UserInfo,
                     user_id: int = Depends(auth.get_current_authenticated_user_id),
                     db_connection: Connection = Depends(database.get_database_connection)) -> UserInfo:
    """Update name or surname for user"""
    try:
        return user.update_user_info(user_id=user_id,
                                     user_info=user_info,
                                     db_connection=db_connection)
    except NullInPusswordException:
        logger.warning('Someone trying to use null byte in password')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Null bytes are prohibited in password")
    except user.UserNotFoundException:
        logger.info('Trying to update non-existent user with user_id={user_id}:', user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with user_id={user_id} not found')
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.delete("/users", status_code=status.HTTP_200_OK)
def delete_user(user_id: int = Depends(auth.get_current_authenticated_user_id),
                db_connection: Connection = Depends(database.get_database_connection)):
    """Delete user by id.
    :raises HTTPException if user is not found, nothing is deleted"""
    try:
        user.delete_user(user_id, db_connection)
    except user.UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user with user_id={user_id} not found')
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.get("/posts", status_code=status.HTTP_200_OK, response_model=list[post.Post])
async def get_all_posts(skip: int = Query(0, ge=0.0, example=0),
                        limit: int = 10,
                        db_connection: AsyncConnection = Depends(database.get_async_db_connection)) -> list[post.Post]:
    """get all posts"""
    # return post.get_all_posts(db_connection, skip=skip, limit=limit)
    try:
        # note, that this only works for IO-bound tasks, because of GIL. Use subprocesses for CPU-bound
        posts = await post.get_all_posts_async(db_connection, skip=skip, limit=limit)
        return posts
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.get("/posts/{post_id}", status_code=status.HTTP_302_FOUND, response_model=post.Post)
async def get_post(post_id: int = Path(..., ge=0.0),  # required, no default value. = None to make optional
                   db_connection: AsyncConnection = Depends(database.get_async_db_connection)):
    """get specific post
    :param db_connection:
    :param post_id path param. post_id >= 0. required.
    """
    try:
        found_post = await post.get_post_by_id_async(post_id, db_connection)
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if found_post:
        return found_post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.post("/posts/", status_code=status.HTTP_201_CREATED, response_model=post.Post)
async def create_post(post_info: post.PostInfo,
                      user_id: int = Depends(auth.get_current_authenticated_user_id),
                      db_connection: AsyncConnection = Depends(database.get_async_db_connection)) -> post.Post:
    """create new post"""
    try:
        created_post = await post.create_post(user_id, post_info, db_connection)
        return created_post
    except post.NoSuchUseridException:
        logger.debug('User not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No user with such user_id')
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.put("/posts/{post_id}", status_code=status.HTTP_200_OK, response_model=post.Post)
async def update_post_info(post_info: post.PostInfo,
                           post_id: int = Path(...),
                           user_id: int = Depends(auth.get_current_authenticated_user_id),
                           db_connection: AsyncConnection = Depends(database.get_async_db_connection)):
    """Update title or body for specific post"""
    try:
        return await post.update_post(user_id, post_id, post_info, db_connection)
    except post.NotYourPostException:
        logger.info('Trying to update post {} by non-owner {}', post_id, user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='not your post_id')
    except post.PostNotFoundException:
        logger.info('Trying to update non-existent post with post_id={}', post_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with post_id={post_id} not found')
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int,
                      user_id: int = Depends(auth.get_current_authenticated_user_id),
                      db_connection: AsyncConnection = Depends(database.get_async_db_connection)):
    """Delete user by id.
    :raises HTTPException if user is not found, nothing is deleted"""
    try:
        await post.delete_post_async(user_id, post_id, db_connection)
    except post.NotYourPostException:
        logger.info('Trying to delete post {} by non-owner {}', post_id, user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='not your post_id')
    except post.PostNotFoundException:
        logger.warning('Deleting non-existent post {}', post_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with post_id={post_id} not found')
    except Exception:
        logger.exception('Unknown exception')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
