import time
from hashlib import md5
import kdl
from api import getSettings, updateProxys, getAliveProxys


def getIps(num):
    settings = getSettings()
    if not settings:
        raise Exception("获取设置失败，请检查配置")
    secretId = settings["secretId"]
    secretKey = settings["secretKey"]
    auth = kdl.Auth(secretId, secretKey)
    client = kdl.Client(auth)
    ips = client.get_dps(num, format='json')
    valids = client.check_dps_valid(ips)
    valids = list(filter(lambda i: i, [k if v else None for k, v in valids.items()]))
    print(f"新获取到的代理ip:{valids}")
    return valids


def checkAlive(count=10):
    """
    当不足aliveCount时，添加newCount个代理
    """
    if len(getAliveProxys()) < count:
        print(f"当前代理ip数：{getAliveProxys()}，已经不足，补充中...")
        urls = getIps(count)
        urls = list(map(lambda url: {"_id": md5(f"http://{url}".encode("utf-8")).hexdigest(), "http": f"{url}", "created": int(time.time()), "isAlive": True,
                                     "lastModify": int(time.time())}, urls))
        return updateProxys(urls)


if __name__ == '__main__':
    # with open("logging_config.yml", "r", encoding="utf8") as f:
    #     logging_config = yaml.safe_load(f)
    # loggingConfig.dictConfig(logging_config)
    # logger = getLogger()
    while True:
        try:
            time.sleep(1)
            settings = getSettings()
            count = settings["proxyNumber"]
            print(f"当前代理设置数：{count}")
            logs = checkAlive(count=count)
            print(logs)
        except Exception as e:
            time.sleep(1)
            print(e)
