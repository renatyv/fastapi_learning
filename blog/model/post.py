from typing import Optional

import sqlalchemy
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import LegacyCursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import Connection

from blog import threadpool_executor


class Post(BaseModel):
    post_id: int
    user_id: int
    title: str
    body: str


def get_all_posts(db_connection: Connection, skip: int = 0, limit: int = 10**6) -> list[Post]:
    """Returns all posts from database. params skip and limit work the same way as for lists"""
    posts = []
    with db_connection.begin():  # within transaction
        statement = text("""SELECT
                                post_id, user_id, title, body
                            FROM blog_post
                            LIMIT :limit OFFSET :skip""")
        params = {'skip': skip, 'limit': limit}
        rows = db_connection.execute(statement,**params).fetchall()
        for post_id, user_id, title, body in rows:
            posts.append(Post(user_id=user_id, post_id=post_id, title=title, body=body))
    return posts


async def get_all_posts_async(db_connection: Connection,
                              skip: int = 0, limit: int = 10**6) -> list[Post]:
    """Returns all posts from database asynchrnously.
    params skip and limit work the same way as for lists"""
    posts = await threadpool_executor.run_asynchonously(get_all_posts, db_connection, skip=skip, limit=limit)
    return posts


def get_post_by_id(post_id: int, db_connection: Connection) -> Optional[Post]:
    """filter posts by post_id"""
    logger.debug(f'Looking for post {post_id}')
    with db_connection.begin():  # within transaction
        try:
            statement = text("""SELECT post_id, user_id, title, body FROM blog_post WHERE post_id = :post_id""")
            params = {'post_id': post_id}
            rows = db_connection.execute(statement, **params).fetchall()
        except Exception as e:
            logger.error(e)
            return None
        else:
            for post_id, user_id, title, body in rows:
                return Post(post_id=post_id, user_id=user_id, title=title, body=body)
            return None


class UnknownException(Exception):
    pass


class NoSuchUseridException(Exception):
    pass


def create_post(user_id: int, title: str, body: str, db_connection: Connection) -> Post:
    """creates new post and saves it
    :raises NoSuchUseridException if user_id is not found in system"""
    with db_connection.begin():  # within transaction
        try:
            statement = text("""INSERT INTO blog_post(user_id, title, body) VALUES (:user_id, :title, :body) RETURNING post_id""")
            params = {'user_id': user_id, 'title': title, 'body':body}
            row: sqlalchemy.engine.Row = db_connection.execute(statement, params).fetchone()
            post_id = row[0]
        # except (UniqueViolation, sqlite3.IntegrityError) as uve:
        except IntegrityError as ie:
            logger.debug(f'No user with id={user_id} '+str(ie))
            raise NoSuchUseridException()
        else:
            logger.debug(f'post with id {(post_id,user_id,title,body)} created')
            return Post(post_id=post_id, user_id=user_id, title=title, body=body)


class PostNotFoundException(Exception):
    pass


class NotYourPostException(Exception):
    pass


def update_post(caller_user_id: int, post_id: int, title: Optional[str], body: Optional[str], db_connection: Connection) -> Post:
    """updates title or body for the post in db.
    title and body are optional. If they are not set, title and body are not updated
    :param caller_user_id who requested to update post
    :returns Post object if update was successful
    :raises PostNotFoundException if post_id is invalied
    :raises NotYourPostException if user_id is wrong"""
    with db_connection.begin(): # start transaction
        to_update_post = get_post_by_id(post_id, db_connection)
        if not to_update_post:
            raise PostNotFoundException
        if to_update_post.user_id != caller_user_id:
            raise NotYourPostException()
        if title:
            to_update_post.title = title
        if body:
            to_update_post.body = body
        try:
            statement = text("""UPDATE blog_post 
                                    SET title = :title, body = :body 
                                    WHERE post_id = :post_id
                                    RETURNING user_id, title, body """)
            params = {'title': to_update_post.title,
                      'body': to_update_post.body,
                      'post_id': to_update_post.post_id}
            row = db_connection.execute(statement, params).fetchone()
        except Exception as e:
            logger.error('unknown error: {e}')
            raise UnknownException
        else:
            if row is None:
                raise PostNotFoundException()
            else:
                caller_user_id, title, body = row
                return Post(post_id=post_id, user_id=caller_user_id, title=title, body=body)


def delete_post(caller_user_id:int, post_id: int, db_connection: Connection):
    """Delete post by post_id. Note, that all post posts will be deleted with CASCADE,
    :raises PostNotFoundException if nothing is deleted from database
    :raises NotYourPostException if user_id is wrong"""
    to_delete_post = get_post_by_id(post_id, db_connection)
    if not to_delete_post:
        raise PostNotFoundException()
    if to_delete_post.user_id != caller_user_id:
        raise NotYourPostException()
    with db_connection.begin():  # within transaction
        try:
            statement = text("""DELETE FROM blog_post WHERE post_id = :post_id""")
            params = {'post_id': post_id}
            result: LegacyCursorResult = db_connection.execute(statement, params)
            deleted_rows = result.rowcount
        except Exception as e:
            logger.error(e)
            raise UnknownException(e)
        else:
            if deleted_rows == 0:
                raise PostNotFoundException()
            if deleted_rows > 1:
                logger.error(f'Many posts with post_id={post_id} were deleted')