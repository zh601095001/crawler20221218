import time
from datetime import datetime

import pytz

t = datetime.fromtimestamp(1671263737, pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
print(t)
