import os
from datetime import datetime
import configparser

# 從設定檔讀取資料
cf = configparser.ConfigParser()
cf.read("settings.config")

# 取得超時時間 (秒)
OPENAI_FLOW_TTL = int(cf.get("openai", "OPENAI_FLOW_TTL"))

# 定義流程處理用的目錄
filefolder = 'chatbot_flow'

# 定義超時檔案清單
over_ttl_uid = []

# 取得所有檔案最後修改時間, 並列出超時檔案名稱
for f in os.listdir(filefolder):
    mtime = os.path.getmtime(f'{filefolder}/{f}')
    diff_second = (datetime.now() - datetime.fromtimestamp(mtime)).seconds
    if diff_second > OPENAI_FLOW_TTL:
        index = f.index('.')
        over_ttl_uid.append(f[:index])

# std 送出所有超時的檔案名稱
print(",".join(over_ttl_uid), end='')