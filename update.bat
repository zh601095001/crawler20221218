cd ./crawlerinit
docker build -t zhlcy2022/crawlerinit .
cd ..

cd ./crawlercurrent
docker build -t zhlcy2022/crawlercurrent .
cd ..


cd ./email
docker build -t zhlcy2022/email .
cd ..

cd ./database
docker build -t zhlcy2022/database .
cd ..

docker push zhlcy2022/crawlerinit
docker push zhlcy2022/crawlercurrent
docker push zhlcy2022/email
docker push zhlcy2022/database


