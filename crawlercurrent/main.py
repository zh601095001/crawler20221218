import yaml
from extract import getCurrent
from utils import updateLastModifyTime
from logging import config as loggingConfig, getLogger
from api import get_match_by_id, set_match_current

if __name__ == '__main__':
    with open("logging_config.yml", "r", encoding="utf8") as f:
        logging_config = yaml.safe_load(f)
    loggingConfig.dictConfig(logging_config)
    logger = getLogger()
    while True:
        logger.info("执行中...")
        try:
            currentGames = getCurrent()
            logger.info(f"当前比赛：{currentGames}")
            if currentGames:
                updateLastModifyTime()
            for currentGame in currentGames:
                currentGame["_id"] = currentGame["ID"]
                if not get_match_by_id(currentGame["ID"]):
                    logger.info(f"比赛初始信息未找到,跳过...ID:{currentGame['ID']}")
                else:
                    logger.info(f"更新比赛：{currentGame['ID']}")
                    set_match_current(currentGame)
        except Exception as e:
            logger.error(f"全局错误:{e}")
