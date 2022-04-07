import blog.model.auth.user_password as user_password


def test_hash_password():
    assert user_password.verify_password('password', user_password.hash_password('password'))
    assert not user_password.verify_password('password', user_password.hash_password('huyassword'))
