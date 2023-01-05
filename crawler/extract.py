import hashlib
import timeit
from datetime import datetime
from os import getenv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from utils import loadJs, parseJSON

SELENIUM = getenv("SELENIUM") or "http://127.0.0.1:4444"


def convertMd5(s):
    return hashlib.md5(s.encode(encoding='utf-8')).hexdigest()


def getCurrent(env="dev"):
    """
    获取比赛当前信息
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    if env == "dev":
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument('--headless')
        driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    try:
        driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
        driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/div[2]/ul[1]/li[1]/a').click()  # 点击赛事选择
        driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[1]/div[2]/input[4]').click()  # 点击进行中
        driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[1]/div[1]/span/a').click()  # 关闭赛事选择弹窗
        tables = driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div[2]').find_elements(By.TAG_NAME, "table")  # 获取所有tables节点
        datas = []
        for table in tables:
            style = table.get_attribute("style")
            _id = table.get_attribute("id")
            if not ("display" in style) and _id.startswith("table"):
                table_id = _id.split("_")[1]
                js_result = parseJSON(driver.execute_script(loadJs("./parser.js", table_id)))
                game_time = js_result["game_time"]
                team_name = js_result["team_name"]
                team_name2 = js_result["team_name2"]
                leave_time = js_result["leave_time"]
                total_score_1 = int(js_result["total_score_1"]) if js_result["total_score_1"] else None
                total_score_2 = int(js_result["total_score_2"]) if js_result["total_score_2"] else None
                game_session = js_result["game_session"]
                current_score = float(js_result["current_score"]) if js_result["current_score"] else None
                datas.append({
                    "_id": convertMd5(f'{game_time} {team_name} | {team_name2}'),
                    "current_score": current_score,
                    "game_session": game_session,
                    "total_score_1": total_score_1,
                    "total_score_2": total_score_2,
                    "leave_time": leave_time
                })
    finally:
        driver.quit()
    return datas


def getInit(env="dev"):
    """
    获取比赛初始信息
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-application-cache")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    if env == "dev":
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument('--headless')
        driver = webdriver.Remote(options=options, command_executor=SELENIUM)
    try:
        driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
        main_window_handle = driver.current_window_handle
        driver.find_element(By.XPATH, '//*[@id="main"]/div[1]/div[2]/ul[1]/li[1]/a').click()  # 点击赛事选择
        driver.find_element(value='rb1').click()  # 点击进行中
        driver.find_element(By.XPATH, '//*[@id="DivLeague"]/div[1]/span/a').click()  # 关闭赛事选择弹窗
        tables = driver.find_element(value='live').find_elements(By.TAG_NAME, "table")  # 获取所有tables节点
        datas = []
        for table in tables:
            style = table.get_attribute("style")
            _id = table.get_attribute("id")
            if not ("display" in style) and _id.startswith("table"):
                table_id = _id.split("_")[1]
                js_result = parseJSON(driver.execute_script(loadJs("./parser.js", table_id)))
                game_time = js_result["game_time"]
                team_name = js_result["team_name"]
                team_name2 = js_result["team_name2"]
                game_session = js_result["game_session"]
                leave_time = js_result["leave_time"]
                total_score_1 = int(js_result["total_score_1"]) if js_result["total_score_1"] else None
                total_score_2 = int(js_result["total_score_2"]) if js_result["total_score_2"] else None
                current_score = float(js_result["current_score"]) if js_result["current_score"] else None
                # 新打开页获取初始让分
                hl = driver.find_element(value=f'hl_{table_id}')
                driver.execute_script("arguments[0].click();", hl)
                newHandler = driver.window_handles[1]  # 获取新打开页
                driver.switch_to.window(newHandler)
                elem = driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/table/tbody').find_elements(By.TAG_NAME, "tr")[-1]  # 获取最后一列
                start_score = elem.find_elements(By.TAG_NAME, "td")[3].text  # 获取初始让分值
                try:
                    start_score = float(start_score)
                except Exception as e:
                    start_score = None
                datas.append({
                    "_id": convertMd5(f'{game_time} {team_name} | {team_name2}'),
                    "start_score": start_score,
                    "team_name1": team_name,
                    "team_name2": team_name2,
                    "game_time": game_time,
                    "game_session": game_session,
                    "createTime": int(time.time()),
                    "current_score": current_score,
                    "total_score_1": total_score_1,
                    "total_score_2": total_score_2,
                    "leave_time": leave_time
                })
                driver.close()
                driver.switch_to.window(main_window_handle)
    finally:
        if env == "dev":
            time.sleep(120)
            driver.quit()
        else:
            driver.quit()
    return datas


if __name__ == '__main__':
    # print(getInit(env=""))
    print(getCurrent(env=""))
    print(timeit.timeit(setup='from __main__ import getCurrent', stmt="getCurrent(env='')", number=1))
