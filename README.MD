# FastAPI blog API
### Goals
Project goal is to learn technologies:
* REST API
* Unit testing
* Relational database
* Database migrations
* Docker container creation and use

### General description
Blog backend API is implemented.
User can read, create, update, and delete blog posts and users.

Each user has user_id, name, and surname.

Each post has author_id, title, and body (plain text).

Implemented:
* users: read, create, update, delete
* posts: read, create, update, delete
* Authentication (using the [official tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
and [tutorial from christophergs.com](https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-10-auth-jwt/)):
  * fastapi's OAuth2 + JWT token
* Basic authorization:
  * user can not update or delete another user
  * user can not update or delete another user's post

## Start in debug mode
Use the following script to deploy database and web server in two separate containers in debug mode: 

```./start_debug.sh```

Dismantle containers:

```./stop_debug.sh```

Start web api and database container manually:

```docker-compose up -f docker-compose.yml -f docker-compose-debug.yml up -d```

In debug mode the code inside container is mapped to local directory.
If you change the code, the web server will reload it on the fly.
After deployment open [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Production deployment
Build docker images

```docker-compose up -f docker-compose.yml -f docker-compose-prod.yml build```

Start docker containers using docker-compose

```docker-compose up -f docker-compose.yml -f docker-compose-prod.yml up -d```

As a result, application is deployed at [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Tests
User and Post read/create is tested using pytest.

Run unit tests:

```python3 -m pytest --no-header --tb=no tests/```

Run api (integration) tests:

```python3 -m pytest --no-header --tb=no tests_api/```

Comments:
* ```python3 -m``` is used instead of 'pytest tests_unit/' to include source directory into python path
* ```--tb=no```  (to traceback) allows to hide long stack traces if exception raised when running test

## Dependencies
1. Python, see ```requirements.txt```
2. yoyo migrations
3. Postgres SQL
4. Docker, docker-compose

## Database

* PostgresSQL 14, Built using docker, default port 5432
* Admin username: **blog_admin**, database: **blog_db** 
* Password is set using environment variables in ```env/debug/database.env``` and ```env/production/database.env``` for debug and production correspondingly.
See template with all necessary env variables in ```env/template/database.env```. 

### yoyo migrations
Before running migrations, you should provide username, password and database names through environment variables, see template at ```env/template/webapi.env```.

set environment:

```export $(cat env/debug/webapi.env | xargs)```

Basic commands:
* list migrations ```yoyo list```
* apply migrations ```yoyo apply```
* rollback last migration ```yoyo rollback```
* rollback all migrations ```yoyo rollback --all```

SQL migration scripts (DDLs) are in ```db_migrations/```

Configuration file: ``yoyo.ini``

#### How to log into the database
using **blog_admin** credentials from container

```docker exec -it fastapi_blog_database_1 psql -U blog_admin -d blog_db```

using **blog_admin** credentials remotely

``psql -h 127.0.0.1 -p 5432 -U blog_admin -d blog_db``

#### Postgres DB initialization:
Database should be pre-configured before starting the app:
1. Login into docker using superuser **postgres** credentials  
```docker exec -it fastapi_blog_database_1 psql -U postgres```
2. Create database **blog_db**  
```create database blog_db;```<br/>
3. Create role **blog_admin** and with for password  
```CREATE ROLE blog_admin WITH LOGIN PASSWORD 'YOUR_PASSWORD' CREATEROLE;```
4. Let **blog_admin** create, update, delete tables   
```GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_admin;```
5. Enable PGCRYPO extension
```CREATE EXTENSION pgcrypto;```
