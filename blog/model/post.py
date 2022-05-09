from typing import Optional

import sqlalchemy
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import LegacyCursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from retry import retry


class Post(BaseModel):
    post_id: int
    user_id: int
    title: str
    body: str


@retry(tries=2, logger=logger)
async def get_all_posts_async(db_connection: AsyncConnection,
                              skip: int = 0, limit: int = 10 ** 6) -> list[Post]:
    """Returns all posts from database asynchronously.
    params skip and limit work the same way as for lists"""
    posts = []
    statement = text("""SELECT
                            post_id, user_id, title, body
                        FROM blog_post
                        LIMIT :limit OFFSET :skip""")
    params = {'skip': skip, 'limit': limit}
    async with db_connection.begin():  # within transaction
        result = await db_connection.execute(statement, parameters=params)
        rows = result.fetchall()
        for post_id, user_id, title, body in rows:
            posts.append(Post(user_id=user_id,
                              post_id=post_id,
                              title=title,
                              body=body))
    return posts


async def get_post_by_id_async(post_id: int, db_connection: AsyncConnection) -> Optional[Post]:
    """filter posts by post_id"""
    logger.debug(f'Looking for post {post_id}')
    try:
        statement = text("""SELECT post_id, user_id, title, body
        FROM blog_post
        WHERE post_id = :post_id""")
        params = {'post_id': post_id}
        result = await db_connection.execute(statement, parameters=params)
        rows = result.fetchall()
    except Exception:
        logger.exception('Unknown DB exception')
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
            statement = text(
                """INSERT INTO blog_post(user_id, title, body)
                VALUES (:user_id, :title, :body)
                RETURNING post_id""")
            params = {'user_id': user_id, 'title': title, 'body': body}
            row: sqlalchemy.engine.Row = db_connection.execute(statement, params).fetchone()
            post_id = row[0]
        # except (UniqueViolation, sqlite3.IntegrityError) as uve:
        except IntegrityError:
            logger.debug('No user with id={user_id} ', user_id)
            raise NoSuchUseridException()
        else:
            logger.debug('post_id={} for user_id={} is created', post_id, user_id)
            return Post(post_id=post_id, user_id=user_id, title=title, body=body)


class PostNotFoundException(Exception):
    pass


class NotYourPostException(Exception):
    pass


@retry(exceptions=IntegrityError)
async def update_post(caller_user_id: int, post_id: int, title: Optional[str], body: Optional[str],
                      db_connection: AsyncConnection) -> Post:
    """updates title or body for the post in db.
    title and body are optional. If they are not set, title and body are not updated
    :param caller_user_id who requested to update post
    :returns Post object if update was successful
    :raises PostNotFoundException if post_id is invalid
    :raises NotYourPostException if user_id is wrong"""
    async with db_connection.begin():  # start transaction
        to_update_post = await get_post_by_id_async(post_id, db_connection)
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
                                    RETURNING user_id, title, body""")
            params = {'title': to_update_post.title,
                      'body': to_update_post.body,
                      'post_id': to_update_post.post_id}
            result = await db_connection.execute(statement, parameters=params)
            row = result.fetchone()
        except IntegrityError as ie:
            logger.exception('Should I retry?')
            raise ie
        except Exception:
            logger.exception('Unknown DB query error')
            raise UnknownException
        else:
            if row is None:
                raise PostNotFoundException()
            else:
                caller_user_id, title, body = row
                return Post(post_id=post_id,
                            user_id=caller_user_id,
                            title=title,
                            body=body)


async def delete_post_async(caller_user_id: int, post_id: int, db_connection: AsyncConnection):
    """Delete post by post_id. Note, that all post posts will be deleted with CASCADE,
    :raises PostNotFoundException if nothing is deleted from database
    :raises NotYourPostException if user_id is wrong"""
    to_delete_post = await get_post_by_id_async(post_id, db_connection)
    if not to_delete_post:
        raise PostNotFoundException()
    if to_delete_post.user_id != caller_user_id:
        raise NotYourPostException()
    try:
        statement = text("""DELETE FROM
            blog_post
            WHERE post_id = :post_id""")
        params = {'post_id': post_id}
        result: LegacyCursorResult = await db_connection.execute(statement, params)
        deleted_rows: int = result.rowcount
    except Exception as e:
        logger.exception('Deleting post_id={} failed. Probably should retry.', post_id)
        raise UnknownException(e)
    else:
        if deleted_rows == 0:
            raise PostNotFoundException()
        if deleted_rows > 1:
            logger.error(f'Many posts with post_id={post_id} were deleted')
