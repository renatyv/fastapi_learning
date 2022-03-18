from typing import Optional

from pydantic import BaseModel

posts_data = [{"post_id": 0,
               "title": "Huyak Huyak",
               "user_id": 0,
               "text": "Deploy"},
              {"post_id": 1,
               "title": "Who is the the best?",
               "user_id": 0,
               "text": "Renat!"},
              {"post_id": 2,
               "user_id": 2,
               "title": "Why?",
               "text": "Because"}
              ]


class Post(BaseModel):
    post_id: int
    user_id: int
    title: str
    text: str


posts = [Post(**post) for post in posts_data]


def get_all_posts() -> list[Post]:
    return posts


def get_post_by_post_id(post_id: int) -> Optional[Post]:
    """filter posts by post_id"""
    found_posts = [post for post in posts if post.post_id == post_id]
    if found_posts:
        return found_posts[0]
    else:
        return None
