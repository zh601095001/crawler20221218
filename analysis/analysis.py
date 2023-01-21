import json
from os import getenv
from pathlib import Path
import requests as rq
import numpy as np
import pandas as pd
from pandas import read_json, DataFrame
from copy import deepcopy

"""
步骤一：数据准备
"""
BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def mergeFiles(fp):
    with open(f"{fp}/sum.json", "w+") as fd:
        fd.write("[")
        for i in Path(fp).iterdir():
            if not i.name.startswith("sum.json"):
                text = i.read_text()
                objs = text.strip("[").strip("]")
                fd.write(objs + ",")
        fd.seek(fd.tell() - 1)
        fd.write("]")
    return f"{fp}/sum.json"


def download(dateRange, limit=100):
    filename = f"{dateRange[0]}-{dateRange[1]}"
    if Path(filename).exists() and (Path(filename) / "sum.json").exists():
        return f"{filename}/sum.json"
    Path(filename).mkdir(exist_ok=True)
    datas = []
    skip = 0
    while True:
        data = rq.post(f"{BASE_URL}/db/s?collection=matches", json={
            "timeStamp": {"$gte": dateRange[0], "$lte": dateRange[1]},
            "skip": skip,
            "limit": limit
        }).json()
        datas.extend(data["data"])
        count = data["count"]
        if skip > count:
            break
        skip += limit
        with open(f"{filename}/{skip}", "w+") as fd:
            json.dump(data["data"], fd)
    return mergeFiles(filename)


def step01(dateRange):
    """数据格式转化"""
    fp = download(dateRange)
    df = read_json(fp)
    df = df[["ID", "sclassName", "hometeam", "guestteam", "homescore", "guestscore", "timeStamp", "records"]]

    # ['时间', '比分', '主', '盘', '客', '变化', '状']
    def filterNullRecords(data):
        return bool(data["records"])

    cond2 = df["records"].map(filterNullRecords)
    df = df[cond2]

    # 过滤没有初盘终盘的比赛
    def convertRecords(records: dict):
        records = deepcopy(records["records"])
        records.reverse()
        pans = []

        for time, score, zhu, pan, ke, change, state in records:
            if not time:
                if len(pans) < 3:
                    pans.append(pan)
                else:
                    pans[-1] = pan
        if len(pans) < 1 or len(records) < 10 or not records[-1][0]:
            return False
        else:
            return True

    cond3 = df["records"].map(convertRecords)
    df = df[cond3]

    # 过滤没有最终比分的比赛
    df = df.query("homescore != '' or guestscore != ''")

    # 获取初盘和终盘
    def getPan(records: dict):
        records = deepcopy(records["records"])
        records.reverse()
        pans = []
        for time, score, zhu, pan, ke, change, state in records:
            if not time:
                if len(pans) < 3:
                    pans.append(pan)
                else:
                    pans[-1] = pan
        return [pans[0], pans[-1]]

    df["pans"] = df["records"].map(getPan).copy()
    df["chupan"] = df["pans"].map(lambda i: float(i[0]))
    df["zhongpan"] = df["pans"].map(lambda i: float(i[1]))

    # 对数据类型进行转换
    def getName(arr):
        return arr[0]

    df["guestteam"] = df["guestteam"].map(getName).copy()
    df["hometeam"] = df["hometeam"].map(getName).copy()
    df["sclassName"] = df["sclassName"].map(getName).copy()
    df["homescore"] = df["homescore"].map(lambda s: int(s)).copy()
    df["guestscore"] = df["guestscore"].map(lambda s: int(s)).copy()
    df["finalScore"] = df["homescore"] - df["guestscore"]

    # 过滤实时历史记录中不需要统计的列
    def filterRecords(records):
        records = deepcopy(records["records"])
        records.reverse()
        filtered = []
        for time, score, zhu, pan, ke, change, state in records:
            if time and score and pan and "封" not in pan and "加时" not in time and "中场" not in time:
                filtered.append([time, score, pan])
        return filtered

    df["records"] = df["records"].map(filterRecords)

    return df.copy()


"""
步骤二： 数据分析
"""


def countPan(df):
    ### START 判断是初盘还是终盘，得到panName IN[df] OUT[df,panName]
    cond = (df["chupan"] - df["finalScore"]).abs() > (df["zhongpan"] - df["finalScore"]).abs()
    cond2 = (df["chupan"] - df["finalScore"]).abs() < (df["zhongpan"] - df["finalScore"]).abs()
    zhongCount = len(df[cond])
    chuCount = len(df[cond2])
    res = "zhongpan" if zhongCount > chuCount else "chupan"
    df[f"res_{res}"] = df[res]
    return res


def calc(df, thresholdRange=(6, 20), level=0, q=5, calc_type="增量"):
    """
    根据监控阈值计算有效性
    :param df: 输入的单一联赛
    :param thresholdRange: 阈值范围
    :param level: 当前分段
    :param q: 分段数
    :param calc_type: 触发类型(增量|减量)
    :return: validity, validity_count, reached, current_range,(actual_validity, actual_threshold): list[有效性],list[有效性比赛数],list[达到监控阈值数],当前分段初始让分范围,(实际监控阈值的有效性，实际监控阈值)
    """
    panName = countPan(df)
    ### START 根据获得的初始让分进行升序排列 IN[df,panName] OUT[df]
    df = df.sort_values(by=f"res_{panName}", ascending=True)
    ### END

    ### START 根据初始让分进行档位划分 IN[df,q,panName,level] OUT[current_range,selectLevel]
    df["initialLevels"] = pd.qcut(x=df[f"res_{panName}"], q=q, retbins=True, labels=list(range(q)), precision=0)[
        0]  # 返回初始让分段位以及对应分段数组
    current_range = pd.qcut(x=df[f"res_{panName}"], q=q, retbins=True, precision=0)[1][level:level + 2]
    selectLevel = df[df["initialLevels"] == level].copy()
    ### END

    ### START 有效性统计 IN[selectLevel,panName,thresholdRange,calc_type] OUT[]
    validity = []  # 有效性百分比列表
    validity_count = []  # 有效比赛计数
    reached_count = []  # 达到监控阈值比赛计数
    # 循环每一个监控阈值
    for i in range(thresholdRange[0], thresholdRange[1] + 1):
        # 分别计算增量和减量情况下的有效性
        if calc_type == "增量":
            cond = selectLevel[f"res_{panName}"] + i >= selectLevel["finalScore"]  # 初始让分 + 增量监控阈值 >= 最终比分
        else:
            cond = selectLevel[f"res_{panName}"] - i <= selectLevel["finalScore"]  # 初始让分值 - 减量监控阈值 <=  最终让分值
        selectLevel["isEffect"] = cond
        # 统计分析
        count_reach = 0  # 达到监控阈值的比赛数
        count_effect = 0  # 达到监控阈值且比赛有效的比赛数
        for _, (initial, records, isEffect) in selectLevel[
            [f"res_{panName}", "records", "isEffect"]].iterrows():  # 循环获得[初始让分 比赛历史记录 是否有效]
            # 查找每一条比赛历史记录，根据监控类型以及是否达到监控阈值，进行统计
            for record in records:
                if calc_type == "增量" and (float(record[2]) - initial) >= i:  # 实时让分值 - 初始让分值 >= 增量监控阈值
                    count_reach += 1  # 达到监控阈值 count_reach +1
                    if isEffect:
                        count_effect += 1  # 达到监控阈值而且比赛有效 count_effect +1
                    break  # 触发条件立即停止监控判断
                if calc_type == "减量" and (initial - float(record[2])) >= i:  # 初始让分值 - 实时让分值>=减量监控阈值
                    count_reach += 1  # 达到监控阈值 count_reach +1
                    if isEffect:
                        count_effect += 1  # 达到监控阈值而且比赛有效 count_effect +1
                    break  # 触发条件立即停止监控判断
        validity.append(count_effect / count_reach)
        validity_count.append(count_effect)
        reached_count.append(count_reach)
    ### END

    ### START 有效性最大的索引和值
    max_index = 0
    max_val = 0
    for i, v in enumerate(validity):
        if v >= max_val:
            max_val = v
            max_index = i
    ### END

    ### START 有效性最小的索引和值
    min_index = 0
    min_val = 99999
    for i, v in enumerate(validity):
        if v < min_val:
            min_val = v
            min_index = i
    ### END
    actual_validity = validity[max_index]
    actual_invalidity = 1 - validity[min_index]
    isEffect = actual_validity >= actual_invalidity  # 判断统计的是有效还是无效比赛
    actual_threshold = max_index + thresholdRange[0] if isEffect else min_index + thresholdRange[0]
    return validity, validity_count, reached_count, current_range, (actual_validity if isEffect else actual_invalidity, actual_threshold, isEffect), max_index, len(selectLevel)


def step02(df, q=5, thresholdRange=(6, 20)):
    panName = countPan(df)
    li = []  # 增量
    li2 = []  # 减量
    plotData1 = []
    plotData2 = []
    for i in range(q):
        validity, validity_count, reached, current_range, (actual_validity, actual_threshold, isEffect), max_index, total = calc(df, thresholdRange=thresholdRange, level=i, q=q, calc_type="增量")
        li.append([i, current_range, actual_threshold, f"{actual_validity:.2%}", isEffect, reached[max_index], total])
        plotData1.append([validity, validity_count, reached])
    for i in range(q):
        validity, validity_count, reached, current_range, (actual_validity, actual_threshold, isEffect), max_index, total = calc(df, thresholdRange=thresholdRange, level=i, q=q, calc_type="减量")
        li2.append([i, current_range, actual_threshold, f"{actual_validity:.2%}", isEffect, reached[max_index], total])
        plotData2.append([validity, validity_count, reached])
    inc_table = DataFrame(li, columns=["档位", "初始让分", "监控阈值", "有(无)效性", "是否有效", "达到监控阈值的比赛场数", "统计比赛场数"])
    des_table = DataFrame(li2, columns=["档位", "初始让分", "监控阈值", "有(无)效性", "是否有效", "达到监控阈值的比赛场数", "统计比赛场数"])
    total_count = len(df)
    reach_rate = (inc_table["达到监控阈值的比赛场数"].sum() + des_table["达到监控阈值的比赛场数"].sum()) / len(df)  # 达到监控阈值的总场次 / 统计总场次

    inc_table_data = json.loads(DataFrame(li, columns=["level", "initialLetGoal", "threshold", "Validity", "isEffect", "totalReach", "totalMatch"]).T.to_json())
    des_table_data = json.loads(DataFrame(li2, columns=["level", "initialLetGoal", "threshold", "Validity", "isEffect", "totalReach", "totalMatch"]).T.to_json())
    return {
        "panName": "初盘" if panName == "chupan" else "终盘",
        "totalCount": total_count,
        "reachRate": reach_rate,
        "inc_table": inc_table_data,
        "des_table": des_table_data,
        "plotData1": plotData1,
        "plotData2": plotData2,
        "thresholdRange": thresholdRange
    }


def analysis_matches_by_name(matchNames, dateRange, q=5, thresholdRange=(6, 20)):
    df = step01(dateRange)
    sclasss = df.groupby("sclassName").groups
    indexs = []
    for matchName in matchNames:
        indexs.append(sclasss[matchName])
    stack_index = np.hstack(indexs)
    df_input = df.loc[stack_index]
    return step02(df_input, q=q, thresholdRange=thresholdRange)


if __name__ == '__main__':
    df = step01()
    sclasss = df.groupby("sclassName").groups
    cba_index = sclasss["CBA"]
    nba_index = sclasss["NBA"]
    stack_index = np.hstack([cba_index, nba_index])
    df_input = df.loc[stack_index]
    step02(df_input)
