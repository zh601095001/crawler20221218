from os import getenv
from pprint import pprint

import requests as rq

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def getMatchSettings(matchName):
    settings = rq.get(f"{BASE_URL}/db", params={
        "collection": "settings"
    }).json()["data"]
    for setting in settings:
        if "matchName" in setting.keys() and matchName in setting["matchName"]:
            return setting
    return None


def updateMatchSetting(matchName, level: str, data: dict, matchType="inc_table"):
    """
    修改阈值api
    :param matchName: 联赛名称
    :param level: 联赛初始让分等级 "0" ~ "xxx"
    :param data: 修改的数据字段 dict
                {'Validity': '57.62%',
                  'initialLetGoal': [-31, -2.5],
                  'isEffect': 1,
                  'level': 0,
                  'threshold': 10,
                  'totalMatch': 635,
                  'totalReach': 210}
    :param matchType: inc_table | des_table   增量还是减量比赛
    :return: 修改是否成功提示
    """
    matchSetting = getMatchSettings(matchName)
    matchSetting["data"][matchType][level].update(data)
    res = rq.put(f"{BASE_URL}/db", params={
        "collection": "settings"
    }, json=matchSetting).json()
    pprint(res)


if __name__ == '__main__':
    pprint(getMatchSettings("NCAA"))
    updateMatchSetting("NCAA", "0", {
        "threshold": 11
    }, matchType="des_table")
