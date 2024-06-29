import requests
import json
import pyttsx3
from aip import AipSpeech
import pyaudio
import wave

def text2speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speech2text(file_path):
    APP_ID = "79280882"
    API_KEY = "fgYSaZtkhsGNoX1Qmd3yeEcR"
    SECRET_KEY = "JExQ3RD4aM3safFlUxbefVB17ireZQKm"

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    with open(file_path, 'rb') as f:
        content = f.read()

    res = client.asr(content, 'wav', 16000, {
        'dev_pid': 1537,
    })

    #print(res)
    return res["result"][0]

#录制音频
def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "../wav/test.wav"
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def get_chat_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    API_Key = "gSHwOQ6DqW6ws8gBpIx3h6US"
    Secret_Key = "Wv32hkVbEJHI4laRNEQJ1dPEvQc5qZdo"
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + API_Key + "&client_secret=" + Secret_Key

    #url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=gSHwOQ6DqW6ws8gBpIx3h6US&client_secret=Wv32hkVbEJHI4laRNEQJ1dPEvQc5qZdo"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def get_speech2text_access_token():
    API_Key = "fgYSaZtkhsGNoX1Qmd3yeEcR"
    Secret_Key = "JExQ3RD4aM3safFlUxbefVB17ireZQKm"
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + API_Key + "&client_secret=" + Secret_Key

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def start_chat():
    chat_access_token = get_chat_access_token()
    #print(chat_access_token)
    chat_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-lite-8k?access_token=" + chat_access_token

    #speech2text_access_token = get_speech2text_access_token()
    #print(speech2text_access_token)
    #speech2text_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/speech2text/ernie-lite-8k?access_token=" + speech2text_access_token
    #循环20次的对话
    for i in range(3):
        #读取输入
        user_input = input("User: ")
        #构造请求
        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        #发送请求
        response = requests.request("POST", chat_url, headers=headers, data=payload)
        #解析返回的json
        response_json = response.json()
        #打印返回的回答
        print("Assistant: " + response_json["result"])
        #text2speech(response_json["result"])
        #将返回的回答写入payload
        payload = json.dumps({
            "messages": [
                {
                    "role": "assistant",
                    "content": response_json["result"]
                }
            ]
        })
        print(payload)
    print("对话结束")

def start_talk():
    chat_access_token = get_chat_access_token()
    #print(chat_access_token)
    chat_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-lite-8k?access_token=" + chat_access_token

    speech2text_access_token = get_speech2text_access_token()
    #print(speech2text_access_token)
    #speech2text_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/speech2text/ernie-lite-8k?access_token=" + speech2text_access_token
    #循环20次的对话
    for i in range(3):
        #录音
        record_audio()
        #语音转文字
        user_input = speech2text("../wav/test.wav")
        print("User: " + user_input)
        #构造请求
        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        #发送请求
        response = requests.request("POST", chat_url, headers=headers, data=payload)
        #解析返回的json
        response_json = response.json()
        #打印返回的回答
        print("Assistant: " + response_json["result"])
        text2speech(response_json["result"])
        #将返回的回答写入payload
        payload = json.dumps({
            "messages": [
                {
                    "role": "assistant",
                    "content": response_json["result"]
                }
            ]
        })
    print("对话结束")

if __name__ == '__main__':
    #你好
    #请问你能简单的介绍一种基于python的web框架吗？
    #谢谢
    # print(speech2text("../wav/test2.wav"))
    # start_talk()
    start_chat()
