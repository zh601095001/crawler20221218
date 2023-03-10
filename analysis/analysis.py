import json
from os import getenv
from pathlib import Path
import requests as rq
import pandas as pd
from pandas import read_json, DataFrame
from hashlib import md5

"""
步骤一：数据准备
"""
BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def mergeFiles(fp):
    with open(f"{fp}/sum.json", "w+") as fd:
        fd.write("[")
        for i in fp.iterdir():
            if (not i.name.startswith("sum.json")) and (not i.name.startswith("records")):
                text = i.read_text()
                if text != "[]":
                    objs = text.strip("[").strip("]")
                    fd.write(objs + ",")
        fd.seek(fd.tell() - 1)
        fd.write("]")
    return (fp / "sum.json").absolute()


def download(dateRange, matchNames, limit=100):
    rootPath = Path("download")
    rootPath.mkdir(exist_ok=True)
    if matchNames:
        matchNamesId = md5("".join(matchNames).encode("utf-8")).hexdigest()
        filename = rootPath / f"{dateRange[0]}-{dateRange[1]}.{matchNamesId}"
        filename.mkdir(exist_ok=True)
    else:
        filename = rootPath / f"{dateRange[0]}-{dateRange[1]}.all"
        filename.mkdir(exist_ok=True)
    recordsPath = rootPath / "records"
    recordsPath.mkdir(exist_ok=True)
    if filename.exists() and (filename / "sum.json").exists():
        return f"{filename}/sum.json"
    skip = 0
    while True:
        data = rq.post(f"{BASE_URL}/db/s?collection=matches", json={
            "timeStamp": {"$gte": dateRange[0], "$lte": dateRange[1]},
            "records.records": {"$not": {"$size": 0}},
            "skip": skip,
            "limit": limit,
            "sclassName": {"$in": matchNames}
        }).json()
        count = data["count"]
        if skip > count:
            break
        skip += limit
        for d in data["data"]:
            if "records" in d.keys():
                if not (recordsPath / d["ID"]).exists():
                    with open(recordsPath / d["ID"], "w+") as fd:
                        json.dump(d["records"], fd)
        datas = []
        for d in data["data"]:
            if "records" in d.keys():
                tmp = {}
                for k, v in d.items():
                    if k in ["ID", "sclassName", "hometeam", "guestteam", "homescore", "guestscore", "timeStamp"]:
                        tmp[k] = v
                datas.append(tmp)
        with open(f"{filename}/{skip}", "w+") as fd:
            json.dump(datas, fd)
    return mergeFiles(filename)


def step01(dateRange, matcheNames):
    """数据格式转化"""
    fp = download(dateRange, matcheNames)
    df = read_json(fp)

    # ['时间', '比分', '主', '盘', '客', '变化', '状']
    def filterNullRecords(ID):
        ID = str(ID)
        recordsPath = Path("download") / "records"
        dataPath = (recordsPath / ID)
        if not dataPath.exists():
            return False
        data = json.load(dataPath.open())
        if not data:
            return False
        if not data["records"]:
            return False
        return True

    cond2 = df["ID"].map(filterNullRecords)
    df = df[cond2]

    # 过滤没有初盘终盘的比赛
    def convertRecords(ID):
        ID = str(ID)
        recordsPath = Path("download") / "records"
        dataPath = (recordsPath / ID)
        data = json.load(dataPath.open())
        records = data["records"]
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

    cond3 = df["ID"].map(convertRecords)
    df = df[cond3]

    # 过滤没有最终比分的比赛
    df = df.query("homescore != '' or guestscore != ''")

    # 获取初盘和终盘
    def getPan(ID):
        ID = str(ID)
        recordsPath = Path("download") / "records"
        dataPath = (recordsPath / ID)
        data = json.load(dataPath.open())
        records = data["records"]
        records.reverse()
        pans = []
        for time, score, zhu, pan, ke, change, state in records:
            if not time:
                if len(pans) < 3:
                    pans.append(pan)
                else:
                    pans[-1] = pan
        return [pans[0], pans[-1]]

    df["pans"] = df["ID"].map(getPan).copy()
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
    def filterRecords(ID):
        ID = str(ID)
        recordsPath = Path("download") / "records"
        dataPath = (recordsPath / ID)
        data = json.load(dataPath.open())
        records = data["records"]
        records.reverse()
        filtered = []
        for time, score, zhu, pan, ke, change, state in records:
            if time and score and pan and "封" not in pan and "加时" not in time and "中场" not in time:
                filtered.append([time, score, pan])
        return filtered

    def filterRecords_ji(ID):
        ID = str(ID)
        recordsPath = Path("download") / "records"
        dataPath = (recordsPath / ID)
        data = json.load(dataPath.open())
        records = data["records"]
        records.reverse()
        filtered = []
        for time, score, zhu, pan, ke, change, state in records:
            if not time and "即" in state:
                filtered.append(pan)
        return filtered

    df["records_ji"] = df["ID"].map(filterRecords_ji)
    df["records"] = df["ID"].map(filterRecords)

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
    df["initialLevels"] = pd.qcut(x=df[f"res_{panName}"], q=q, retbins=True, labels=list(range(q)), precision=0)[0]  # 返回初始让分段位以及对应分段数组
    current_range = pd.qcut(x=df[f"res_{panName}"], q=q, retbins=True, precision=0)[1][level:level + 2]
    selectLevel = df[df["initialLevels"] == level].copy()
    ### END

    ### START 有效性统计 IN[selectLevel,panName,thresholdRange,calc_type] OUT[]
    validity = []  # 有效性百分比列表
    validity_count = []  # 有效比赛计数
    reached_count = []  # 达到监控阈值比赛计数
    all_download_records = []
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
        download_records = {
            "valid_records": [],  # 达到监控阈值且有效的比赛
            "invalid_records": []  # 达到监控阈值且无效的比赛
        }
        for _, (initial, records, isEffect, records_ji) in selectLevel[
            [f"res_{panName}", "records", "isEffect", "records_ji"]].iterrows():  # 循环获得[初始让分 比赛历史记录 是否有效]
            # 查找每一条比赛历史记录，根据监控类型以及是否达到监控阈值，进行统计
            isReach = False  # 该场比赛是否达到阈值
            isValid_records = False  # 该场比赛是否有效
            filter_records = {"records": [], "records_ji": records_ji}
            for record in records:
                filter_records["records"].append(record)
                if calc_type == "增量" and (float(record[2]) - initial) >= i:  # 实时让分值 - 初始让分值 >= 增量监控阈值
                    count_reach += 1  # 达到监控阈值 count_reach +1
                    isReach = True
                    if isEffect:
                        count_effect += 1  # 达到监控阈值而且比赛有效 count_effect +1
                        isValid_records = True
                    break  # 触发条件立即停止监控判断
                if calc_type == "减量" and (initial - float(record[2])) >= i:  # 初始让分值 - 实时让分值>=减量监控阈值
                    count_reach += 1  # 达到监控阈值 count_reach +1
                    isReach = True
                    if isEffect:
                        count_effect += 1  # 达到监控阈值而且比赛有效 count_effect +1
                        isValid_records = True
                    break  # 触发条件立即停止监控判断
            if isReach:
                if isValid_records:
                    download_records["valid_records"].append(filter_records)
                else:
                    download_records["invalid_records"].append(filter_records)
        validity.append(count_effect / count_reach)
        validity_count.append(count_effect)
        reached_count.append(count_reach)
        all_download_records.append(download_records)
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
    isEffect = int(actual_validity >= actual_invalidity)  # 判断统计的是有效还是无效比赛
    actual_threshold = max_index + thresholdRange[0] if isEffect else min_index + thresholdRange[0]
    return {
        "validity": validity,
        "validity_count": validity_count,
        "reached_count": reached_count,
        "current_range": current_range,
        "actual_validity": actual_validity if isEffect else actual_invalidity,
        "actual_threshold": actual_threshold,
        "isEffect": isEffect,
        "max_index": max_index,
        "min_index": min_index,
        "total": len(selectLevel),
        "download_records": [all_download_records, max_index if isEffect else min_index],
        "currentReachedCount": reached_count[max_index if isEffect else min_index]
    }


def step02(df, matchNames, q=5, thresholdRange=(6, 20), downloadRecordsFlag=True):
    panName = countPan(df)
    calcDatas = {
        "inc": [],
        "des": [],
        "plotData1": [],
        "plotData2": []
    }
    for i in range(q):
        incData = calc(df, thresholdRange=thresholdRange, level=i, q=q, calc_type="增量")
        calcDatas["inc"].append(
            [i, incData["current_range"], incData["actual_threshold"], f"{incData['actual_validity']:.2%}", incData["isEffect"],
             incData["currentReachedCount"], incData["total"], incData["download_records"] if downloadRecordsFlag else None])
        calcDatas["plotData1"].append([incData["validity"], incData["validity_count"], incData["reached_count"]])

        desData = calc(df, thresholdRange=thresholdRange, level=i, q=q, calc_type="减量")
        calcDatas["des"].append(
            [i, desData["current_range"], desData["actual_threshold"], f"{desData['actual_validity']:.2%}", desData["isEffect"],
             desData["currentReachedCount"], desData["total"], desData["download_records"] if downloadRecordsFlag else None])
        calcDatas["plotData2"].append([desData["validity"], desData["validity_count"], desData["reached_count"]])
    columnNames = ["level", "initialLetGoal", "threshold", "Validity", "isEffect", "totalReach", "totalMatch", "download_records"]
    inc_table = DataFrame(calcDatas["inc"], columns=columnNames)
    des_table = DataFrame(calcDatas["des"], columns=columnNames)

    return {
        "panName": "初盘" if panName == "chupan" else "终盘",
        "totalCount": len(df),
        "reachRate": (inc_table["totalReach"].sum() + des_table["totalReach"].sum()) / len(df),  # 达到监控阈值的总场次 / 统计总场次
        "inc_table": json.loads(inc_table.T.to_json()),
        "des_table": json.loads(des_table.T.to_json()),
        "plotData1": calcDatas["plotData1"],
        "plotData2": calcDatas["plotData2"],
        "thresholdRange": thresholdRange,
        "matchNames": matchNames
    }


def analysis_matches_by_name(matchNames, dateRange, q=5, thresholdRange=(6, 20), downloadRecordsFlag=True):
    inputMd5 = md5(json.dumps({
        "matchNames": matchNames,
        "dateRange": dateRange,
        "q": q,
        "thresholdRange": thresholdRange,
        "downloadRecordsFlag": downloadRecordsFlag
    }).encode("utf-8")).hexdigest()
    resultPath = Path("result")
    resultPath.mkdir(exist_ok=True)
    resultFilePath = resultPath / inputMd5
    if resultFilePath.exists():
        try:
            return json.loads(resultFilePath.read_text())
        except Exception as e:
            df = step01(dateRange, matchNames)
            results = step02(df, q=q, thresholdRange=thresholdRange, matchNames=matchNames,
                             downloadRecordsFlag=downloadRecordsFlag)
            resultFilePath.write_text(json.dumps(results))
            return results
    else:
        df = step01(dateRange, matchNames)
        results = step02(df, q=q, thresholdRange=thresholdRange, matchNames=matchNames,
                         downloadRecordsFlag=downloadRecordsFlag)
        resultFilePath.write_text(json.dumps(results))
        return results


if __name__ == '__main__':
    download([1672502400, 1677513600], )
