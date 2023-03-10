import os, sys, getopt, json
import configparser, uuid
import openai

# 定義 OpenAI GPT 請求
def generate_response(messages, length):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=length,
        stop=None,
        temperature=0.7
    )

    for choice in response.choices:
        if "text" in choice:
            return choice.text
    return response.choices[0].message.content

def main(argv):
    # 從設定檔讀取資料
    cf = configparser.ConfigParser()
    cf.read("settings.config")

    # 嘗試建立相關儲存的目錄(預設在 chatbot_flow)
    filefolder = 'chatbot_flow'
    try:
        os.makedirs(filefolder)
    # 檔案已存在的例外處理
    except FileExistsError:
        pass

    # 嘗試取得輸入參數
    try:
        opts, args = getopt.getopt(argv,"hmf:l:",["message=","flow=","length="])
    except getopt.GetoptError:
        print('chatbot.py -m <message> -f <flow> -l <length>')
        sys.exit(2)

    # 定義預設值
    flowhash = None # 預設流程ID
    length = 200 # 預設回應長度

    for opt, arg in opts:
        if opt == '-h':
            print('chatbot.py -m <message> -f <flow> -l <length>')
            sys.exit(0)
        elif opt in ("-m", "--message"):
            inputmsg: str = arg
        elif opt in ("-f", "--flow"):
            flowhash: str = arg
        elif opt in ("-l", "--length"):
            length: int = int(arg)

    # 沒有流程, 則產生隨機ID, 並且不保存對話流程
    save_flow = True
    if flowhash == None:
        flowhash = str(uuid.uuid4())
        save_flow = False

    # 設定 OpenAI KEY
    openai.api_key = cf.get("openai", "OPENAI_API_KEY")
    openai.organization = cf.get("openai", "OPENAI_ORGANIZATION_ID")

    # 判斷是否需要保存對話流程
    if save_flow:
        # 判斷是否存在之前的對話流程
        if os.path.isfile(f'{filefolder}/{flowhash}.json'):
            with open(f'{filefolder}/{flowhash}.json', 'w') as f:
                message_log = json.load(f)
        else:
            # 建立新的對話流程
            message_log = [{"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible."}]
    else:
        # 建立新的對話流程
        message_log = [{"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible."}]

    # 定義文字輸入數據
    message_log.append({"role": "user", "content": inputmsg})

    # 取得請求結果
    response = ""
    try:
        response = generate_response(message_log, length)
    # 發生錯誤直接跳離程序
    except Exception:
        sys.exit(1)

    # 定義回應結果數據
    message_log.append({"role": "assistant", "content": response})

    # 判斷是否需要保存對話流程
    if save_flow:
        # 將對話結果存入
        with open(f'{filefolder}/{flowhash}.json', 'w') as f:
            print(json.dump(message_log), file=f, end='')

    # CLI 輸出對話結果
    print(response, end='')

if __name__ == "__main__":
   main(sys.argv[1:])