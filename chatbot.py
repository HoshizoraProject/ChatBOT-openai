import os, sys, getopt, json
import configparser, uuid
import openai

# 定義 OpenAI GPT 請求
def generate_response(messages, user, length):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=length,
        stop=None,
        temperature=0.7,
        user=user # 區別使用者
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
        opts, args = getopt.getopt(argv,"hmu:l:",["message=","user=","length="])
    except getopt.GetoptError:
        print('chatbot.py -m <message> -u <user> -l <length>')
        sys.exit(2)

    # 定義預設值
    userhash = None # 預設使用者
    length = 200 # 預設回應長度

    for opt, arg in opts:
        if opt == '-h':
            print('chatbot.py -m <message> -u <user> -l <length>')
            sys.exit(0)
        elif opt in ("-m", "--message"):
            inputmsg: str = arg
        elif opt in ("-u", "--user"):
            userhash: str = arg
        elif opt in ("-l", "--length"):
            length: int = arg

    # 沒有使用者, 則產生隨機ID, 並且不保存對話流程
    save_flow = True
    if userhash == None:
        userhash = str(uuid.uuid4())
        save_flow = False

    # 設定 OpenAI KEY
    openai.api_key = cf.get("openai", "OPENAI_API_KEY")
    openai.organization = cf.get("openai", "OPENAI_ORGANIZATION_ID")

    # 判斷是否需要保存對話流程
    if save_flow:
        # 判斷是否存在之前的對話流程
        if os.path.isfile(f'{filefolder}/{userhash}.json'):
            with open(f'{filefolder}/{userhash}.json', 'w') as f:
                message_log = json.load(f)
        else:
            # 建立新的對話流程
            message_log = []
    else:
        # 建立新的對話流程
        message_log = []

    # 定義文字輸入數據
    message_log.append({"role": "user", "content": inputmsg})

    # 取得請求結果
    response = generate_response(message_log, userhash, length)

    # 定義回應結果數據
    message_log.append({"role": "assistant", "content": response})

    # 判斷是否需要保存對話流程
    if save_flow:
        # 將對話結果存入
        with open(f'{filefolder}/{userhash}.json', 'w') as f:
            print(json.dump(message_log), file=f, end='')

    # CLI 輸出對話結果
    print(response)

if __name__ == "__main__":
   main(sys.argv[1:])