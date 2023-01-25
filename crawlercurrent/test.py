from datetime import datetime, timedelta
from time import mktime
tp = (datetime.now() - timedelta(5)).date().timetuple()

print(mktime(tp))