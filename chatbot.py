import os, sys, getopt, json
import configparser, uuid
import openai

def main(argv):
    # 從設定檔讀取資料
    cf = configparser.ConfigParser()
    cf.read("settings.config")

    # 嘗試取得輸入參數
    try:
        opts, args = getopt.getopt(argv,"hmu:",["message=","user="])
    except getopt.GetoptError:
        print('chatbot.py -m <message> -u <user>')
        sys.exit(2)
    
    userhash = None

    for opt, arg in opts:
        if opt == '-h':
            print('chatbot.py -m <message> -u <user>')
            sys.exit(0)
        elif opt in ("-m", "--message"):
            inputmsg: str = arg
        elif opt in ("-u", "--user"):
            userhash: str = arg

    # 沒有使用者, 則產生隨機
    if userhash == None:
        userhash = str(uuid.uuid4())

    # 設定 OpenAI KEY
    openai.api_key = cf.get("openai", "OPENAI_API_KEY")
    openai.organization = cf.get("openai", "OPENAI_ORGANIZATION_ID")
    
    # 創建 OpenGPT 3.5 的模型
    model_engine = "gpt-3.5-turbo"
    #model_engine = "text-davinci-003"

    # 定義 OpenAI GPT 請求
    def generate_response(prompt, user):
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
            presence_penalty=0,
            frequency_penalty=0,
            user=user  # 區別使用者
        )
        message = response.choices[0].text
        return message.strip()

    # 取得請求結果
    message = generate_response(inputmsg, userhash)

    # CLI 請求結果
    print(message)

    # TODO: 處理上下文關係表

if __name__ == "__main__":
   main(sys.argv[1:])