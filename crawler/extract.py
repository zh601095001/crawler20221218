import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class Extarct:
    def __init__(self):
        # 定义配置对象
        options = webdriver.ChromeOptions()
        # 无头模式
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.body = ""  # 点击操作后原始待处理html


    def step01(self):
        self.driver.get(f"http://live.nowscore.com/basketball.htm?date={datetime.now().date()}")
        # 点击操作
        elem = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[1]/div[2]/ul[1]/li[1]/a')
        elem.click()
        elem2 = self.driver.find_element(By.XPATH, '//*[@id="rb1"]')
        elem2.click()
        elem3 = self.driver.find_element(By.XPATH, '//*[@id="DivLeague"]/div[1]/span/a')
        elem3.click()
        # 文本解析
        body = self.driver.find_element(By.XPATH, "/html").get_attribute("innerHTML")
        self.body = f"<html>\n{body}\n</html>"

    def step02(self):
        soup = BeautifulSoup(self.body, features="html.parser")
        data = soup.select("#live")
        # write(data[0].prettify(encoding="gbk"))
        tables = data[0].select("table", limit=10000)

        # 筛选不显示的
        def filterDisplay(data):
            data = str(data)
            return not re.search("display: none;", data)

        res = [i for i in filter(filterDisplay, tables)]

        # 筛选出目标table
        def filterTable(data):
            data = str(data)
            return re.search("align=\"center\"", data)

        targetTables = [i for i in filter(filterTable, res)]

        def getTable(_targetTables):
            li = []
            for targetTable in _targetTables:
                rows = targetTable.findAll("tr")
                # 获取第一行表头数据
                cols = rows[0].findAll("td")
                # 单独处理第一列的第一行
                first = cols[0]
                firstCol = "".join(re.match(r'^.*?</a>(.*?)<span(?:.*?)>(.*?)</span>.*?$', str(first)).groups()).replace("\xa0", "")
                cols1 = cols[1:]

                def convert(data):
                    data = str(data)
                    return re.match("^<td.*?>(.*?)</td>", data).group(1)

                titles = list(map(convert, cols1))

                titles.insert(0, firstCol)

                dataRows = rows[1:]
                # 处理第一行数据
                line1 = list(map(convert, dataRows[0].findAll("td")[1:]))
                line2 = list(map(convert, dataRows[1].findAll("td")))
                li.append([
                    titles, line1, line2
                ])
            return li

        return getTable(targetTables)

    def run(self):
        self.step01()
        return self.step02()


if __name__ == '__main__':
    tables = Extarct().run()
