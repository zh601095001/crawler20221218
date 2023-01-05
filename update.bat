cd ./crawler
docker build -t zhlcy2022/crawler .
cd ..


cd ./email
docker build -t zhlcy2022/email .
cd ..

docker push zhlcy2022/crawler
docker push zhlcy2022/email

