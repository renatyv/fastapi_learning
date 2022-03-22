from typing import Union, Optional

from fastapi import FastAPI, Query, Path, Body, HTTPException
from blog.model import user
from blog.model import post
from loguru import logger
import blog.logger_config

app = FastAPI()

# Force uvicorn to emit logs using the same loguru configs
blog.logger_config.setup_logging()

@app.get("/users")
def users(skip: int = Query(0, ge=0.0, example=2), limit: int = 10) -> list[user.User]:
    """get all users
    :param skip. skip >= 0. optional
    :param limit. default 10. optional
    """
    return user.get_all_users(skip=skip, limit=limit)


@app.get("/users/{user_id}")
def get_user(user_id: int = Path(..., ge=0.0)) -> Optional[user.User]:
    """get specific user
    :param user_id is required, greater than 0
    """
    return user.get_user_by_id(user_id)


@app.post("/users/")
def create_user(username: str = Body(...,min_length=1,
                                     max_length=10,
                                     regex='\w'),
                surname: str = Body(..., min_length=1,
                                     max_length=10,
                                     regex='\w')):
    try:
        return user.create_user(username, surname)
    except user.DuplicateUserCreationException as e:
        logger.info('Trying to create duplicate user:'+str(e))
        raise HTTPException(status_code=409,
                            detail=str(e))



@app.get("/posts")
def posts():
    """get all posts"""
    return post.get_all_posts()


@app.get("/posts/{post_id}")
def get_post(post_id: int = Path(..., ge=0.0)):
    """get specific post
    :param post_id path param. post_id >= 0. required.
    """
    return post.get_post_by_post_id(post_id)


@app.post("/posts/")
def create_post(user_id: int = Body(..., ge=0),
                title: str = Body(..., min_length=1,
                                     max_length=300),
                body: str = Body(..., min_length=0,
                                  max_length=10000)) -> post.Post:
    """create new post
    :param user_id: may exist in users. If it does not, no error is returned, post is created"""
    try:
        return post.create_post(user_id,title,body)
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=409, detail=str(e))