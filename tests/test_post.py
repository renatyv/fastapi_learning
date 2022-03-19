from blog.model import post


def test_get_post_by_post_id():
    posts = [post.Post(post_id=0, user_id=0, title='Life is beautiful', text='Librum epsum')]
    first_post = post.get_post_by_post_id(0, posts)
    assert posts[0] == first_post


def test_create_new_post():
    posts = [post.Post(post_id=0, user_id=0, title='Life is beautiful', text='Librum epsum')]
    new_post = post.create_post(user_id=1, title='Life is going well', text='For me', posts=posts)
    assert posts[1] == new_post
