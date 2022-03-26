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
* users: read, create.
* posts: read, create.

Not implemented yet:
* users: update, delete
* posts: update, delete

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

Run ```pytest``` in the main directory to start all tests.

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

Basic commands:
* list migrations ```yoyo list```
* apply migrations ```yoyo apply```
* rollback migrations ```yoyo rollback```

SQL migration scripts (DDLs) are in ```db_migrations/```

Configuration file: ``yoyo.ini``

#### How to log into the database
using **blog_admin** credentials from container

```docker exec -it fastapi_blog_database_1 psql -U blog_admin -d blog_db```

using **blog_admin** credentials remotely

``psql -h 127.0.0.1 -p 5432 -U blog_admin -d blog_db``

#### Postgres DB initialization:
Database should be pre-configured before starting the app using the following steps

1. Login into docker user superuser **postgres** credentials  
```docker exec -it fastapi_blog_database_1 psql -U postgres```
2. Create database **blog_db**  
```create database blog_db;```<br/>
3. Create role **blog_admin** and with for password  
```CREATE ROLE blog_admin WITH LOGIN PASSWORD 'YOUR_PASSWORD' CREATEROLE;```
4. Let **blog_admin** create, update, delete tables   
```GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_admin;```
