import os
import json, requests
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .functions import start_chat, start_talk, multimodal_talk
import base64
from .models import User
import wave
import numpy as np
from scipy.io.wavfile import write
from scipy.io import wavfile
import scipy.io
import pyttsx3
from aip import AipSpeech
import subprocess
import ffmpeg
from openai import OpenAI
from django.conf import settings


# Create your views here.

def get_chat_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    API_Key = ""
    Secret_Key = ""
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + API_Key + "&client_secret=" + Secret_Key

    #url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=gSHwOQ6DqW6ws8gBpIx3h6US&client_secret=Wv32hkVbEJHI4laRNEQJ1dPEvQc5qZdo"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def text2speech(text):
    engine = pyttsx3.init()
    # 调节语速
    engine.setProperty('rate', 200)
    # 调节音量
    engine.setProperty('volume', 1)
    print('开始合成...')
    engine.save_to_file(text, 'output/test.wav')
    print('合成完成！')
    engine.runAndWait()


def speech2text(file_path):
    APP_ID = ""
    API_KEY = ""
    SECRET_KEY = ""

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    with open(file_path, 'rb') as f:
        content = f.read()

    res = client.asr(content, 'wav', 16000, {
        'dev_pid': 1537,
    })

    print(res)
    return res["result"][0]


def make_json_request(chat_list):
    chat_access_token = get_chat_access_token()
    chat_url = "" + chat_access_token
    headers = {
        'Content-Type': 'application/json'
    }

    # print(chat_list)

    data = []
    for i in range(len(chat_list)):
        if i % 2 == 0:
            data.append({
                "role": "user",
                "content": chat_list[str(i)]
            })
        else:
            data.append({
                "role": "assistant",
                "content": chat_list[str(i)]
            })
        # print(data)
    payload = json.dumps({
        "messages": data,
        "system": "你是一个叫做jarvis的人工智能助手，对话中请自称jarvis"
    })
    print(payload)
    response = requests.request("POST", chat_url, headers=headers, data=payload)
    response_json = response.json()
    print(response_json)
    return response_json["result"]


# def multimodal_talk(request):
#     if request.method == 'POST':
#         api_base = "https://api.lingyiwanwu.com/v1"
#         api_key = "fc93c80b1a774dcc9cf1072edce045a7"
#         model = "yi-vision"
#
#         def init_client(api_base, api_key):
#             return OpenAI(api_key=api_key, base_url=api_base)
#
#         def encode_image(image_file):
#             with open(image_file, 'rb') as image:
#                 base64_image = base64.b64encode(image.read()).decode('utf-8')
#             return base64_image
#
#         def send_message(client, model, messages):
#             stream = client.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 stream=True
#             )
#             response = ""
#             for part in stream:
#                 response += part.choices[0].delta.content or ""
#             return response
#
#         client = init_client(api_base, api_key)
#         messages = []
#
#         user_input = request.POST.get('user_input')
#
#         image_path = None
#
#         if 'image' in request.FILES:
#             image = request.FILES['image']
#             os.makedirs('uploads', exist_ok=True)  # 创建uploads目录，如果它不存在的话
#             image_path = os.path.join('uploads', image.name)
#             with open(image_path, 'wb+') as destination:
#                 for chunk in image.chunks():
#                     destination.write(chunk)
#
#         if image_path is not None:
#             base64_image = encode_image(image_path)
#             messages.append({
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": user_input
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             })
#         else:
#             messages.append({"role": "user", "content": user_input})
#
#         response = send_message(client, model, messages)
#         messages.append({"role": "assistant", "content": response})
#
#         return response
#
#     return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def multimodal(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        response = start_chat(user_input)
        return JsonResponse({'response': response})
    return render(request, 'multimodal.html')


@csrf_exempt
def motion(request):
    if request.method == 'POST':
        response = start_talk()
        return JsonResponse({'response': response})
    return render(request, 'motion.html')


@csrf_exempt
def about(request):
    name = '赵志远'
    role = ['摸鱼', '打游戏', '写代码']

    return render(request, 'about.html', {'name': name, 'role': role})


@csrf_exempt
def login(request):
    print(request.method)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(email, password)
        print(request)

        # 如果返回值为空
        if not email:
            return render(request, 'login.html', {'error_msg': '请填写邮箱'})
        if not password:
            return render(request, 'login.html', {'error_msg': '请填写密码'})

        # if email == 'zhaozhiyuanzzd@163.com' and password == '123456':
        #     return render(request, 'index.html')
        # else:
        #     return render(request, 'login.html', {'error_msg': '用户名或密码错误'})

        #判断返回是否为空
        if User.objects.filter(email=email, password=password).exists():
            return render(request, 'index.html')
        else:
            return render(request, 'login.html', {'error_msg': '用户名或密码错误'})

    else:
        return render(request, 'login.html')


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username, password, email)
        print(request)

        # 如果返回值为空
        if not email:
            return render(request, 'signup.html', {'error_msg': '请填写邮箱'})
        if not username:
            return render(request, 'signup.html', {'error_msg': '请填写用户名'})
        if not password:
            return render(request, 'signup.html', {'error_msg': '请填写密码'})

        #判断返回是否为空
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_msg': '邮箱已被注册'})
        else:
            User.objects.create(email=email, username=username, password=password)

        return render(request, 'index.html')
    else:
        return render(request, 'signup.html')


@csrf_exempt
def upload_wav(request):
    if request.method == 'POST':

        print(request.POST)
        # 聊天记录处理
        chat_list = request.POST.get('chat_list')
        print(type(chat_list))
        print(str(chat_list))
        chat_list = json.loads(chat_list)
        print(chat_list)
        # 按行读取
        # chat_list = chat_list.split('\n')
        # 去除第奇数行
        # chat_list = chat_list[1::2]
        # print(chat_list)

        # 音频处理
        audio_data = request.POST.get('audio')
        audio_data = audio_data.replace("data:audio/wav; codecs=opus;base64,", "")
        audio_data += "=" * (4 - len(audio_data) % 4)
        print(audio_data)

        sample_rate = int(request.POST.get('sample_rate'))
        print(sample_rate)

        binary_audio = base64.b64decode(audio_data)
        print(binary_audio)

        wav_file = open("wav/test1.wav", "wb")
        wav_file.write(binary_audio)
        wav_file.close()

        os.system("ffmpeg -i wav/test1.wav -y -ar 16000 wav/test2.wav")

        # 语音转文字
        # text = 'test'
        text = speech2text("wav/test2.wav")

        # 文字放入chat_list中并构造json请求
        chat_list[str(len(chat_list))] = text
        json_request = make_json_request(chat_list)

        # 文字转语音
        text2speech(json_request)

        #用户信息
        # user_name = 'user'

        return JsonResponse({'ai': json_request, 'user': text})


@csrf_protect
def download_wav(request):
    if request.method == 'GET':
        with open("output/test.wav", "rb") as f:
            response = HttpResponse(f.read(), content_type="audio/wav")
            response['Content-Disposition'] = 'attachment; filename=test.wav'
            return response
    return render(request, 'index.html')


@csrf_protect
def multimodal(request):
    if request.method == 'POST':
        response = multimodal_talk(request)
         # 返回JSON响应
        return JsonResponse({'response': response})
    return render(request, 'multimodal.html')


@csrf_protect
def motion(request):
    if request.method == 'POST':
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            save_path = os.path.join(settings.STATICFILES_DIRS[0], 'photo', "photo.jpg")

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)

            user_input = request.POST.get('user_input', '')

            # 将图片和用户输入传递给 multimodal 视图
            with open(save_path, 'rb') as img:
                files = {'image': img}
                data = {'user_input': user_input}
                response = request.post('http://127.0.0.1:8000/multimodal/', files=files, data=data)

            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'No photo uploaded'}, status=400)

    return render(request, 'motion.html')


@csrf_protect
def motion(request):
    if request.method == 'POST':
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            save_path = os.path.join(settings.STATICFILES_DIRS[0], 'photo', "photo.jpg")

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)

            user_input = request.POST.get('user_input', '')

            # 将图片和用户输入传递给 multimodal 视图
            with open(save_path, 'rb') as img:
                files = {'image': img}
                data = {'user_input': user_input}
                response = request.post('http://127.0.0.1:8000/multimodal/', files=files, data=data)

            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'No photo uploaded'}, status=400)

    return render(request, 'motion.html')


@csrf_exempt
def upload_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        save_path = os.path.join(settings.STATICFILES_DIRS[0], 'photo', "photo.jpg")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)

        return JsonResponse({'status': 'success', 'message': 'Photo uploaded successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Photo upload failed.'})


@csrf_exempt
def synthesize_and_play(request):
    # 从请求中获取参数
    text = request.POST.get('text')
    voice = request.POST.get('voice', 'zh-CN-XiaoyiNeural')
    file_name = request.POST.get('file_path', 'hello.mp3')

    # 将文件保存到静态文件目录
    file_path = os.path.join(settings.STATICFILES_DIRS[0], file_name)

    # 在命令中使用变量
    command = ["edge-tts", "--voice", voice, "--text", text, "--write-media", file_path, "--write-subtitles",
               "hello.vtt"]
    subprocess.run(command)

    # 返回一个可以通过 HTTP 访问的 URL
    audio_url = settings.STATIC_URL + file_name

    return JsonResponse({'audio_url': audio_url})
