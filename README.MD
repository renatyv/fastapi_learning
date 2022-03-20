# FastAPI blog API
Project goals:
* learn technologies:
  * REST API
  * Unit testing
  * Relational database
  * Database migrations
  * Docker container creation and use

Implements a blog backend API.

Functionality:
* users
  * read
  * add
* posts
  * read
  * add

Database access is configured through environment:

```env/webapi.env```
## REST API
Run web server in development mode

```uvicorn blog.main:app --reload```

Server is loaded at  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


## Database

* PostgresSQL 14, Built using docker, default port 5432
* Admin username: **blog_admin**.
* Root password is set using environment in ```env/database.env``` file (not commited): ```POSTGRES_PASSWORD=password``` 
<code>[DEFAULT]<br/>
database = postgresql://blog_admin:jw8s0F4@localhost/blog_db
</code>
### yoyo migrations
SQL migration scripts (DDL) are in ```db_migrations/```

Configuration file: ``yoyo.ini``

Database connection url with password is in ``yoyo_db_credentials.ini``

Basic commands:
* list migrations ```yoyo list```
* apply migrations ```yoyo apply```
* rollback migrations ```yoyo rollback```

#### Database login
using **blog_admin** credentials from container

```docker exec -it fastapi_blog_database_1 psql -U blog_admin -d blog_db```

using **blog_admin** credentials remotely

``psql -h 127.0.0.1 -p 5432 -U blog_admin -d blog_db``

### Postgres DB initialization:
Database should be pre-configured before starting the app using the following steps

1. Login into docker user superuser **postgres** credentials  
```docker exec -it fastapi_blog_database_1 psql -U postgres```
2. Create database **blog_db**  
```create database blog_db;```<br/>
3. Create role **blog_admin** and with for password  
```CREATE ROLE blog_admin WITH LOGIN PASSWORD 'jw8s0F4' CREATEROLE;```
4. Let **blog_admin** create, update, delete tables   
```GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_admin;```

## Docker deployment
Docker-compose is used to build two containers: web api and databas.  
```docker-compose up -d```

As a result, application is deployed at [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Dependencies
1. Python, see ```requirements.txt```
2. Postgres SQL, see ```docker-compose.yml```, ```Dockerfile``` 
  
## Tests
User and Post creation is tested using pytest.

Run ```pytest``` in the main directory to start all tests.