# FastAPI blog API
### Goals
learn technologies:
* REST API
* Unit testing
* Relational database
* Database migrations
* Docker container creation and use

### General description
Blog backend API is implemented. Here one can read, create, update, and delete blog posts and users.
Each user has
* user_id
* name
* surname

Each post has:
* author_id
* title
* body (plain text)

Implemented:
* users: read, create. Postgres is used
* posts: read, create. Local in-memory data is used

Not implemented yet:
* users: update, delete
* posts: update, delete

## Start in debug mode
Use the following script to deplot database + webapi in debug mode: 

```./start_debug.sh```

Docker-compose can be used to start two containers: web api and database.

```docker-compose up -f docker-compose.yml -f docker-compose-debug.yml up -d```

The code is mapped to local directory.
If you change the code, the web server will reload that information on the fly.
After deployment open [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Production deployment

```docker-compose up -f docker-compose.yml -f docker-compose-prod.yml build```

```docker-compose up -f docker-compose.yml -f docker-compose-prod.yml up -d```

As a result, application is deployed at [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Tests
User and Post creation is tested using pytest.

Run ```pytest``` in the main directory to start all tests.

## Dependencies
1. Python, see ```requirements.txt```
2. yoyo migrations
3. Postgres SQL
4. Docker

## Database

* PostgresSQL 14, Built using docker, default port 5432
* Admin username: **blog_admin**.
* Root password is set using environment in ```env/database.env``` file (not commited): ```POSTGRES_PASSWORD=password``` 

### yoyo migrations
Basic commands:
* list migrations ```yoyo list```
* apply migrations ```yoyo apply```
* rollback migrations ```yoyo rollback```

SQL migration scripts (DDLs) are in ```db_migrations/```

Configuration file: ``yoyo.ini``

Username, password and database are configured through ```env/production/webapi.env```, which is not commited.
File ```env/template/webapi.env``` can be used as a template.

#### Database login
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
```CREATE ROLE blog_admin WITH LOGIN PASSWORD 'jw8s0F4' CREATEROLE;```
4. Put the password into ``yoyo_db_credentials.ini`` :  
<code>[DEFAULT]<br/>
database = postgresql://blog_admin:jw8s0F4@localhost/blog_db</code>
6. Let **blog_admin** create, update, delete tables   
```GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_admin;```

