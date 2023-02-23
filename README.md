# 1.开发文档

## 1.1 各文件用途

- analysis: 数据分析模块
- chrome: selenium/node-chrome配置
- crawlercurrent: 爬虫，更新当前让分
- crawlerhistory: 爬虫，获取历史比赛记录
- crawlerhistory2: 爬虫，每天获取前前天的历史记录(持续获取)
- crawlerinit: 爬虫，获取初始让分
- crawlerrecords：爬虫，获取当前预触发比赛的当前让分记录
- database: 后端数据库对接 + 前端web
- emailcreator：邮件预触发
- emailsender：邮件触发
- build.sh: 容器构建
- docker-compose.yaml: 容器一键部署
- start.sh: 删除并重启所有容器
- update.sh: 更新容器至docker hub（弃用）




1. 列出前天发生比赛的联赛名称列表
2. 给出哪些联赛可以放到一起，作为一个数据源进行分析的组合建议（1.初始让分值近似，2.平均最大增量让分偏差，平均最大减量让分偏差）
3. 总结邮件，功能开发
4. 撰写开发文档和部署文档（建议在开发过程中穿插进行）


# 2.部署文档
https://docs.docker.com/desktop/install/ubuntu/
1. 检查KVM virtualization support
    Docker Desktop runs a VM that requires KVM support.
    
    The kvm module should load automatically if the host has virtualization support. To load the module manually, run:
    ```
     modprobe kvm
    ```
    Depending on the processor of the host machine, the corresponding module must be loaded:
    ```
     modprobe kvm_intel  
     modprobe kvm_amd  
    ```
    If the above commands fail, you can view the diagnostics by running:
    ```
     kvm-ok
    ```
    To check if the KVM modules are enabled, run:
    ```
    lsmod | grep kvm
    kvm_amd               167936  0
    ccp                   126976  1 kvm_amd
    kvm                  1089536  1 kvm_amd
    irqbypass              16384  1 kvm
    ```
2. 安装
   - 设置docker软件包仓库
     1. step01
        ```
        sudo apt-get update
        sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
        ```
     2. step02
        ```
        sudo mkdir -m 0755 -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        ```
     3. step03
        ```
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        ```
   - 下载最新的deb安装包：https://desktop.docker.com/linux/main/amd64/docker-desktop-4.16.2-amd64.deb?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-linux-amd64

   - 安装：
     ```
     sudo apt-get update
     sudo apt-get install ./docker-desktop-<version>-<arch>.deb
     ```
   - 下载并安装mongo compass(选择系统为ubuntu)
   
     https://www.mongodb.com/try/download/compass
     安装命令：`sudo apt install ./安装包名.deb`
3. 运行
   - 双击运行docker 
   - 配置docker：settings->resources->Memory 将内存调至大于8GB
   - 在项目根目录执行：`bash ./build.sh`下载并编译项目
   - 在项目根目录执行：`docker compose up -d`运行项目
4. 配置项目
在浏览器打开`http://localhost:8000`,在配置中设置相关参数
5. 若没有历史记录
手动使用mongo compass在defaultDb下的添加matches集合 然后导入本地的
或者使用代理 在配置页面设置抓取的天数 抓去指定天数的历史记录



给出哪些联赛可以放到一起，作为一个数据源进行分析的组合建议（1.初始让分值近似，2.平均最大增量让分偏差，平均最大减量让分偏差）