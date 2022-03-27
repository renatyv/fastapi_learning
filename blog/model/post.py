from typing import Optional

import sqlalchemy
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import Connection


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
            logger.debug(f'Query successful, {rows}')
            for post_id, user_id, title, body in rows:
                return Post(post_id=post_id, user_id=user_id, title=title, body=body)


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


def update_post(post_id: int, title: Optional[str], body: Optional[str], db_connection: Connection) -> Post:
    """updates title or body for the post in db.
    title and body are optional. If they are not set, title and body are not updated
    :returns Post object if update was successful
    :raises PostNotFoundException if post_id is invalied"""
    with db_connection.begin(): # start transaction
        try:
            if title and body:
                statement = text("""UPDATE blog_post 
                                    SET title = :title, body = :body 
                                    WHERE post_id = :post_id
                                    RETURNING user_id, title, body """)
            elif body and not title:
                statement = text("""UPDATE blog_post 
                                    SET body = :body 
                                    WHERE post_id = :post_id
                                    RETURNING user_id, title, body """)
            elif title and not body:
                statement = text("""UPDATE blog_post 
                                    SET title = :title 
                                    WHERE post_id = :post_id
                                    RETURNING user_id, title, body """)
            else:
                statement = text("""SELECT user_id, title, body 
                                    FROM blog_post 
                                    WHERE post_id = :post_id""")
            params = {'title': title, 'body': body, 'post_id': post_id}
            row = db_connection.execute(statement, params).fetchone()
        except Exception as e:
            logger.error('unknown error: {e}')
            raise UnknownException
        else:
            if row is None:
                raise PostNotFoundException()
            else:
                user_id, title, body = row
                return Post(post_id=post_id, user_id=user_id, title=title, body=body)
