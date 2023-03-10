import os, sys, getopt, json
import configparser
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
    
    for opt, arg in opts:
        if opt == '-h':
            print('chatbot.py -m <message> -u <user>')
            sys.exit(0)
        elif opt in ("-m", "--message"):
            message: str = arg
        elif opt in ("-u", "--user"):
            userhash: str = arg

    # 設定 OpenAI KEY
    openai.api_key = cf.get("openai", "OPENAI_API_KEY")
    openai.organization = cf.get("openai", "OPENAI_ORGANIZATION_ID")

    # 設定要傳送的訊息
    context = message

    # 創建 OpenGPT 3.5 的模型
    model_engine = "gpt-3.5-turbo"
    #model_engine = "text-davinci-003"
    
    # 獲取模型回應
    response = openai.Completion.create(
        engine=model_engine,
        user=userhash, # 設置使用者 ID
        prompt=context,
        temperature=0.7,
        max_tokens=4080,
        stop=None,
    )

    # 獲取模型生成的內文
    result = response.choices[0].text.strip()

    # CLI 列印回應結果
    print(result)

    # TODO: 處理上下文關係表

if __name__ == "__main__":
   main(sys.argv[1:])