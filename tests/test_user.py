import pytest
import blog.model.user as user


def test_create_new_user():
    # keyword arguments are used for creation because of Pydantic
    users = [user.User(user_id=0, name='renat', surname='iuldashev')]
    created_user = user.create_user('marat', 'iuldashev', users=users)
    assert users[1] == created_user


def test_create_dublicate_user():
    users = [user.User(user_id=0, name='renat', surname='iuldashev')]
    user.create_user("Renat", "Yuldashev", users=users)
    with pytest.raises(user.DuplicateUserCreationException):
        assert user.create_user("Renat", "Yuldashev")

