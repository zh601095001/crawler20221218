cd ./crawlerinit || exit
docker build -t zhlcy2022/crawlerinit .
cd ..

cd ./crawlercurrent || exit
docker build -t zhlcy2022/crawlercurrent .
cd ..


cd ./email || exit
docker build -t zhlcy2022/email .
cd ..

cd ./database || exit
docker build -t zhlcy2022/database .
cd ..

sudo docker push zhlcy2022/crawlerinit
sudo docker push zhlcy2022/crawlercurrent
sudo docker push zhlcy2022/email
sudo docker push zhlcy2022/database


