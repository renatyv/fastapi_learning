from typing import Union, Optional

from fastapi import FastAPI, Query, Path
from blog.model import user
from blog.model import post


app = FastAPI()


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
