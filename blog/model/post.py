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


local_posts = [Post(**post) for post in posts_data]


def get_all_posts() -> list[Post]:
    return local_posts


def get_post_by_post_id(post_id: int, posts=None) -> Optional[Post]:
    """filter posts by post_id"""
    if not posts:
        posts = local_posts

    found_posts = [post for post in posts if post.post_id == post_id]
    if found_posts:
        return found_posts[0]
    else:
        return None


def create_post(user_id: int, title: str, text: str, posts=None) -> Post:
    """creates new post and saves it"""
    if not posts:
        posts = local_posts

    new_post = Post(post_id=len(local_posts), user_id=user_id, title=title, text=text)
    posts.append(new_post)
    return new_post
