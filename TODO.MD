## TODO
1. Test API directly using requests package.
### Implement Authentication & authorization using JWT.
Using the
[official tutotial](https://fastapi.tiangolo.com/tutorial/security/)
or
[tutorial from christophergs.com](https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-10-auth-jwt/)

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