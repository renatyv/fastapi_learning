import sqlite3

posts = [{"post_id": 0,
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


def get_all_posts():
    return posts


def get_post_by_user_id(user_id: int):
    """filter posts by user_id"""
    return [post for post in posts if post["user_id"] == user_id]


def get_post_by_post_id(post_id: int):
    """filter posts by post_id"""
    return [post for post in posts if post["post_id"] == post_id]
