import requests
import json
import pyttsx3
from aip import AipSpeech
import pyaudio
import wave
from openai import OpenAI
import os
from django.http import JsonResponse
import base64


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
    print(res)
    return res["result"][0]


def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "myapp/wav/test.wav"
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


def start_chat(user_input):
    chat_access_token = get_chat_access_token()
    chat_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-lite-8k?access_token={chat_access_token}"

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

    response = requests.request("POST", chat_url, headers=headers, data=payload)

    return response.json()['result']


def start_talk():
    record_audio()
    user_input = speech2text("myapp/wav/test.wav")
    response = start_chat(user_input)
    text2speech(response)
    return response


def get_chat_access_token():
    api_key = "fgYSaZtkhsGNoX1Qmd3yeEcR"
    secret_key = "JExQ3RD4aM3safFlUxbefVB17ireZQKm"
    auth_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"

    response = requests.get(auth_url)
    access_token = response.json()['access_token']
    return access_token


def multimodal_talk(request):
    if request.method == 'POST':
        api_base = "https://api.lingyiwanwu.com/v1"
        api_key = "fc93c80b1a774dcc9cf1072edce045a7"
        model = "yi-vision"

        def init_client(api_base, api_key):
            return OpenAI(api_key=api_key, base_url=api_base)

        def encode_image(image_file):
            with open(image_file, 'rb') as image:
                base64_image = base64.b64encode(image.read()).decode('utf-8')
            return base64_image

        def send_message(client, model, messages):
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            response = ""
            for part in stream:
                response += part.choices[0].delta.content or ""
            return response

        client = init_client(api_base, api_key)
        messages = []

        user_input = request.POST.get('user_input')

        image_path = None

        if 'image' in request.FILES:
            image = request.FILES['image']
            os.makedirs('uploads', exist_ok=True)  # 创建uploads目录，如果它不存在的话
            image_path = os.path.join('uploads', image.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

        if image_path is not None:
            base64_image = encode_image(image_path)
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            })
        else:
            messages.append({"role": "user", "content": user_input})

        response = send_message(client, model, messages)
        messages.append({"role": "assistant", "content": response})

        return response

    return JsonResponse({'error': 'Invalid request method'}, status=400)
