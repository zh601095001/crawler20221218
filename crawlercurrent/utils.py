import json
import time
from datetime import datetime
from os import getenv
from api import updateLastModify

BASE_URL = getenv("BASE_URL") or "http://localhost:8000"


def updateLastModifyTime():
    lastModifyTime = int(time.time())
    updateLastModify(lastModifyTime, datetime.now())


def justifyArgs(arg):
    if type(arg) in [int, float]:
        return f"{arg}"
    else:
        return f"'{arg}'"


def loadJs(path, *args):
    with open(path) as fd:
        lines = fd.readlines()[0:-1]
        postArgs = map(justifyArgs, args)
        script_args = f"({','.join(postArgs)})"
        lines.append(script_args)
        return "return" + "\n".join(lines)


def parseJSON(s: str):
    return json.loads(s)
