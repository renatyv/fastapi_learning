## TODO
## 1. Authentification
Follow the [official tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
or [tutorial from christophergs.com](https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-10-auth-jwt/)
   1. add columns to *blog_user* table
      1. *hashed_password*
      2. *email*
   3. apply yoyo migrations
   4. Define model *user.UserPublicInfo* with fields: *name*, *surname*, *email*
   5. update *user.User* model to include *UserPublicInfo* and *hashed_password* 
   6. update model's create_user() method
      1. required fields: *name*, *email*, *password*
      2. optional fields: *surname*
      3. hashes the password and saves new user to database. Returns token?
   7. tests
   8. create signup endpoint
   9. create login endpoint

[review of authorization methods](https://blog.restcase.com/4-most-used-rest-api-authentication-methods/)

## 2. Authorization

Three roles should exist: **anonymous**, **user**,  **admin**. 

*anonymous* can:
* see every user and post.
* register as new user

*user* can:
* see every user and post. 
* create, delete, and update only his own posts and his own name, surname.
* delete his own account.
* create new account.

*admin* can:
* read, change, delete, and create any user or post

2. Try using asynchronous database requests using **asyncpg** postgres driver.  
Will get us some performance, but may complicate debugging a lot.
* [sqlalchemy documentation on async qureios](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
* [asyncpg documentation](https://magicstack.github.io/asyncpg/current/usage.html)  
* [using aiosqlite for testing](https://github.com/omnilib/aiosqlite)