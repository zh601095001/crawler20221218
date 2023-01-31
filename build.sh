# 数据分析
cd ./analysis || exit
docker build -t zhlcy2022/analysis .
cd ..

# 爬虫
cd ./crawlerhistory || exit
docker build -t zhlcy2022/crawlerhistory .
cd ..

cd ./crawlercurrent || exit
docker build -t zhlcy2022/crawlercurrent .
cd ..

cd ./crawlerinit || exit
docker build -t zhlcy2022/crawlerinit .
cd ..

# 前后端
cd ./database || exit
docker build -t zhlcy2022/database .
cd ..

# 邮件
cd ./email || exit
docker build -t zhlcy2022/email .
cd ..

# 代理
cd ./proxys || exit
docker build -t zhlcy2022/proxys .
cd ..
