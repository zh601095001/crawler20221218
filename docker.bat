cd crawler
docker build -t zhlcy2022/crawler .
cd ..

cd email
docker build -t zhlcy2022/email .
cd ..

cd database
docker build -t zhlcy2022/database .
cd ..

docker push zhlcy2022/crawler
docker push zhlcy2022/email
docker push zhlcy2022/database

pause
