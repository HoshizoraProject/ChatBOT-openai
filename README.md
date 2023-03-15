# ChatBOT
透過 OpenAI API 進行類自然語言對話, 使用模型 `gpt-3.5-turbo`

## Python 使用上的基礎範例
### 主要呼叫程序
`chatbot.py` 

```
import subprocess

# 定義輸入內容
input = "要詢問AI的文字"

# 執行子程序
proc = subprocess.run(['python3', 'chatbot.py', f'--message="{input}"'],
                          stdout=subprocess.PIPE)
if (proc.returncode != 0):
    print("執行 chatbot.py 發生異常!")
    return

response = proc.stdout.decode("utf-8")

print(response)
```

#### 可選參數
`--flow=` 維持對話流程的識別ID, 推薦使用`UUID`或`HASH`

### 檢查過期 flow 清單子程序
`check_flow_ttl.py`

## Required
[OpenAI](https://pypi.org/project/openai/)

## Reference
[OpenAI API GPT-3.5](https://platform.openai.com/docs/guides/chat)

## License
[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
