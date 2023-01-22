import logging


def getLogger():
    logger = logging.getLogger()

    fh = logging.FileHandler('test.log')  # 可以向文件发送日志

    ch = logging.StreamHandler()  # 可以向屏幕发送日志

    fm = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s")  # 打印格式

    fh.setFormatter(fm)
    ch.setFormatter(fm)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.setLevel('INFO')  # 设置级别
    return logger
