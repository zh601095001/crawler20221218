import time

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from analysis import step01, analysis_matches_by_name
import uvicorn
import json

app = FastAPI()


def getDateTimeStampFromDatetime(dt: datetime):
    """
    获取当前日期的时间撮，不包括时分秒
    """
    return int(time.mktime(dt.date().timetuple()))


class Range(BaseModel):
    min: int
    max: int


class Analysis(BaseModel):  # 构造
    matchName: list
    range: Range
    q: int


def convertDateRange(dateRange: str):
    return list(map(lambda x: getDateTimeStampFromDatetime(datetime.fromtimestamp(int(x[:-3]))), dateRange.split(",")))


@app.get("/matches")  # 获取所有联赛名
async def get_all_matches_name(dateRange: str):
    dateRange = convertDateRange(dateRange)
    print(dateRange, "get")
    df = step01(dateRange)
    return json.loads(df.groupby("sclassName")["ID"].count().to_json())


@app.post("/matches")
async def analysis_matches(dateRange: str, obj: Analysis):
    dateRange = convertDateRange(dateRange)
    print(dateRange, "post")
    return analysis_matches_by_name(obj.matchName, dateRange, obj.q, (obj.range.min, obj.range.max))


if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=5000, log_level="info", host="0.0.0.0")
    server = uvicorn.Server(config)
    server.run()
