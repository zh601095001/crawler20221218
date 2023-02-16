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