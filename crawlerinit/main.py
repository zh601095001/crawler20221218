from logging import config as loggingConfig, getLogger
import time
import yaml
from extract import getInit
from utils import checkStartTime
from api import get_match_by_id, add_new_match, update_match

if __name__ == '__main__':
    with open("logging_config.yml", "r", encoding="utf8") as f:
        logging_config = yaml.safe_load(f)
    loggingConfig.dictConfig(logging_config)
    logger = getLogger()
    while True:
        time.sleep(5)
        logger.info("执行中...")
        try:
            checkStartTime()
            initGames = getInit()
            logger.info(f"初始比赛：{initGames}")
            for initGame in initGames:
                initGame["_id"] = initGame["ID"]
                if not get_match_by_id(initGame["ID"]):
                    initGame["createTime"] = int(time.time())
                    initGame["isSendEmail"] = False
                    add_new_match(initGame)
        except Exception as e:
            logger.error(f"初始让分全局错误:{e},请检查代理是否配置成功")
