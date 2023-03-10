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
        user=user  # 區別使用者
    )

    for choice in response.choices:
        if "text" in choice:
            return choice.text
    return response.choices[0].message.content

def main(argv):
    # 從設定檔讀取資料
    cf = configparser.ConfigParser()
    cf.read("settings.config")

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

    # 沒有使用者, 則產生隨機
    if userhash == None:
        userhash = str(uuid.uuid4())

    # 設定 OpenAI KEY
    openai.api_key = cf.get("openai", "OPENAI_API_KEY")
    openai.organization = cf.get("openai", "OPENAI_ORGANIZATION_ID")

    # 嘗試取得原先對話數據
    message_log = []

    # 定義文字輸入數據
    message_log.append({"role": "user", "content": inputmsg})

    # 取得請求結果
    response = generate_response(message_log, userhash, length)

    # 定義回應結果數據
    message_log.append({"role": "assistant", "content": response})

    # CLI 請求結果
    print(response)

if __name__ == "__main__":
   main(sys.argv[1:])