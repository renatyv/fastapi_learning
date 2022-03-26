from typing import Union, Optional, Any

from fastapi import FastAPI, Query, Path, Body, HTTPException, Depends
from sqlalchemy.engine import Connection
from blog.http_status_codes import HttpStatusCode

from blog import database
from blog.model import user
from blog.model import post
from loguru import logger
import blog.logger_config

app = FastAPI()

# Force uvicorn to emit logs using the same loguru configs
blog.logger_config.setup_logging()

@app.get("/users", status_code=HttpStatusCode.OK.value, response_model=list[user.User])
def users(skip: int = Query(0, ge=0.0, example=2),
          limit: int = 10,
          db_connection: Connection = Depends(database.get_database_connection)) -> Any:
    """get all users
    :param skip. skip >= 0. optional
    :param limit. default 10. optional
    """
    return user.get_all_users(db_connection, skip=skip, limit=limit)


@app.get("/users/{user_id}", status_code=HttpStatusCode.FOUND.value, response_model=Optional[user.User])
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


@app.post("/users/",status_code=HttpStatusCode.OK.value)
def create_user(username: str = Body(...,min_length=1,
                                     max_length=10,
                                     regex='\w'),
                surname: str = Body(..., min_length=1,
                                     max_length=10,
                                     regex='\w'),
                db_connection: Connection = Depends(database.get_database_connection)):
    try:
        return user.create_user(username, surname,db_connection)
    except user.DuplicateUserCreationException as e:
        logger.info('Trying to create duplicate user:'+str(e))
        raise HTTPException(status_code=HttpStatusCode.CONFLICT.value,
                            detail=str(e))



@app.get("/posts", status_code=HttpStatusCode.OK.value, response_model=list[post.Post])
def posts(db_connection: Connection = Depends(database.get_database_connection)):
    """get all posts"""
    return post.get_all_posts(db_connection)


@app.get("/posts/{post_id}", status_code=HttpStatusCode.FOUND.value, response_model=post.Post)
def get_post(post_id: int = Path(..., ge=0.0),
             db_connection: Connection = Depends(database.get_database_connection)):
    """get specific post
    :param post_id path param. post_id >= 0. required.
    """
    found_post = post.get_post_by_post_id(post_id,db_connection)
    if found_post:
        return found_post
    else:
        raise HTTPException(status_code=HttpStatusCode.NOT_FOUND.value)


@app.post("/posts/", status_code=HttpStatusCode.CREATED.value, response_model=post.Post)
def create_post(user_id: int = Body(..., ge=0),
                title: str = Body(..., min_length=1,
                                     max_length=300),
                body: str = Body(..., min_length=0,
                                  max_length=10000),
                db_connection: Connection = Depends(database.get_database_connection)) -> post.Post:
    """create new post
    :param user_id: may exist in users. If it does not, no error is returned, post is created"""
    try:
        return post.create_post(user_id, title, body, db_connection)
    except post.NoSuchUserid as e:
        logger.debug(str(e))
        raise HTTPException(status_code=HttpStatusCode.NOT_ACCEPTABLE.value, detail='No user with such user_id')
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=HttpStatusCode.CONFLICT.value, detail='Unknown error')