import os, sys, getopt, json
import configparser, uuid
import openai

# 定義 OpenAI GPT 請求
def generate_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # 使用 stderr 顯示回應內容
    print(json.dumps(response), file=sys.stderr)

    for choice in response.choices:
        if "text" in choice:
            return choice.text
    return response.choices[0].message.content

# 判斷 問題是否違反原則
def moderation_response(messages):
    response = openai.Moderation.create(
        input=messages
    )

    # 使用 stderr 顯示回應內容
    print(json.dumps(response), file=sys.stderr)

    return response.results[0].flagged

def main(argv):
    # 從設定檔讀取資料
    cf = configparser.ConfigParser()
    cf.read("settings.config")

    # 設定 OpenAI 參數
    openai.api_key = cf.get("openai", "OPENAI_API_KEY")
    openai.organization = cf.get("openai", "OPENAI_ORGANIZATION_ID")
    system_content = cf.get("openai", "OPENAI_SYSTEM_CONTENT")
    keep_count = int(cf.get("openai", "OPENAI_KEEP_COUNT"))

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
        print('chatbot.py -m <message> -f <flow>')
        sys.exit(2)

    # 定義預設值
    flowuuid = None # 預設流程ID

    # 取得參數資料
    for opt, arg in opts:
        if opt == '-h':
            print('chatbot.py -m <message> -f <flow>')
            sys.exit(0)
        elif opt in ("-m", "--message"):
            inputmsg: str = arg
        elif opt in ("-f", "--flow"):
            flowuuid: str = arg

    # 判斷提問是否違反原則
    try:
        if moderation_response(inputmsg):
            sys.exit(-1)
    # 發生錯誤直接跳離程序
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    # 沒有流程, 則產生隨機ID, 並且不保存對話流程
    save_flow = True
    if flowuuid == None:
        flowuuid = str(uuid.uuid4())
        save_flow = False

    # 判斷是否需要保存對話流程
    if save_flow:
        # 判斷是否存在之前的對話流程
        if os.path.isfile(f'{filefolder}/{flowuuid}.json'):
            with open(f'{filefolder}/{flowuuid}.json', 'w') as f:
                message_log = json.load(f)

                # 判斷對話流程是否過長
                count_content = 0
                for role, content in message_log:
                    count_content += len(content)
                
                if count_content > 4080:
                    message_log.pop(1)
                    message_log.pop(1)
        else:
            # 建立新的對話流程
            message_log = [{"role": "system", "content": system_content}]
    else:
        # 建立新的對話流程
        message_log = [{"role": "system", "content": system_content}]

    # 定義文字輸入數據
    message_log.append({"role": "user", "content": inputmsg})

    # 取得請求結果
    response = ""
    try:
        response = generate_response(message_log)
    # 發生錯誤直接跳離程序
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    # 定義回應結果數據
    message_log.append({"role": "assistant", "content": response})

    # 判斷是否需要保存對話流程
    if save_flow:
        # 拋棄過多的對話
        if len(message_log) > (keep_count * 2 + 1):
            message_log.pop(1)
            message_log.pop(1)

        # 將對話結果存入
        with open(f'{filefolder}/{flowuuid}.json', 'w') as f:
            json.dump(message_log, f)

    # CLI 輸出對話結果
    print(response, end='')

if __name__ == "__main__":
   main(sys.argv[1:])