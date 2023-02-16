# 数据分析
cd ./analysis || exit
docker build -t zhlcy2022/analysis .
cd ..

# 爬虫
cd ./crawlerhistory || exit
docker build -t zhlcy2022/crawlerhistory .
cd ..

cd ./crawlerhistory2 || exit
docker build -t zhlcy2022/crawlerhistory2 .
cd ..

cd ./crawlercurrent || exit
docker build -t zhlcy2022/crawlercurrent .
cd ..

cd ./crawlerinit || exit
docker build -t zhlcy2022/crawlerinit .
cd ..

cd ./crawlerrecords || exit
docker build -t zhlcy2022/crawlerrecords .
cd ..


cd ./emailvalid || exit
docker build -t zhlcy2022/emailvalid .
cd ..

# 前后端
cd ./database || exit
docker build -t zhlcy2022/database .
cd ..


# 邮件
cd ./emailcreator || exit
docker build -t zhlcy2022/emailcreator .
cd ..

cd ./emailsender || exit
docker build -t zhlcy2022/emailsender .
cd ..

# 代理
cd ./proxys || exit
docker build -t zhlcy2022/proxys .
cd ..
