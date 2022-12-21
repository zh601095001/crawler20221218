from extract import extract
from utils import updateLastModifyTime, checkStartTime
from parse import parseTables
from os import getenv

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"

while True:
    try:
        checkStartTime()
        tables = extract()
        if tables:
            updateLastModifyTime()
        parseTables(tables)

    except Exception as e:
        with open("log.txt", "a+") as fd:
            fd.write(str(e))
            print(e)
