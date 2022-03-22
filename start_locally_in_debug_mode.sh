# set environment variables
echo 'reading env variables';
export $(cat env/debug/webapi.env | xargs)

echo 'starting database & web api in docker'
docker-compose up -d

echo 'applying migrations'
yoyo apply;

echo 'starting web api locally'
uvicorn blog.main:app --host 0.0.0.0 --port 8000 --reload;