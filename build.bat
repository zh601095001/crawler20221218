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