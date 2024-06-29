const recordBtn = document.querySelector(".record-btn");
const player = document.querySelector(".audio-player");
if (navigator.mediaDevices.getUserMedia) {
  var chunks = [];
  const constraints = { audio: true };
  navigator.mediaDevices.getUserMedia(constraints).then(
    stream => {
      console.log("授权成功！");
        let sample_rate = 16000;

        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.audioBitsPerSecond = 16000;
        channelCount = mediaRecorder.stream.getAudioTracks()[0].getSettings().channelCount;
        console.log("channelCount: ", channelCount);
        example = mediaRecorder.stream.getAudioTracks()[0].getSettings()
        console.log("example: ", example);


      var draw_id = 0;
      recordBtn.onclick = () => {
        if (mediaRecorder.state === "recording") {
          mediaRecorder.stop();
          recordBtn.textContent = "开始录音";
          console.log("录音结束");
          cancelAnimationFrame(draw_id);
          draw_logo();
          console.log("动画结束");

        } else {
          mediaRecorder.start();
          console.log("录音中...");
          recordBtn.textContent = "录音中...";

          let n = 0;
          let canvas = document.getElementById('visualizer');
          let ctx = canvas.getContext('2d');
          let y_list = [35, 20, 20, 0, 25];
          let width = 5;
          let gap = 3;
          let height_list = [10, 30, 20, 35, 10];
          let y_now = [35, 20, 20, 0, 25];
          let flag = [1, 1, 1, 1, 1];
          let draw = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let i = 0; i < y_list.length; i++) {
                if (y_now[i] === y_list[i] + height_list[i] || y_now[i] === 0) {
                    flag[i] = -flag[i];
                }
                y_now[i] -= 0.5*flag[i];
                ctx.fillStyle = 'rgb(0, 0, 0)';
                ctx.fillRect(i * (width + gap), y_now[i], width, y_list[i] + height_list[i] - y_now[i]);
            }
            draw_id = requestAnimationFrame(draw);
          }
            draw();

        }
        console.log("录音器状态：", mediaRecorder.state);
      };

      mediaRecorder.ondataavailable = e => {
        chunks.push(e.data);
      };

      mediaRecorder.onstop = e => {
        var blob = new Blob(chunks, { type: "audio/wav; codecs=opus" });
        chunks = [];

          let chat_list = read_chat_list();
          let chat_json = {};
            for (let i = 0; i < chat_list.length; i++) {
                chat_json[i] = chat_list[i];
            }
          console.log("chat_json: ", chat_json);
            //json转字符串
            chat_json = JSON.stringify(chat_json);

        let reader = new FileReader();
        reader.onloadend = () =>{
            let base64data = reader.result;
            console.log("base64data: ", base64data);
            fetch("/upload_wav/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: 'audio=' + encodeURIComponent(base64data) + '&chat_list=' + chat_json + '&sample_rate=' + sample_rate
            }).then(function (response) {
                if (response.ok) {
                    console.log("上传成功！");
                    console.log(response);
                    response.json().then(function (data) {
                        console.log(data);
                        add_chat_element(data['user'], 'right', 'user');
                        add_chat_element(data['ai'], 'left', 'jarvis');
                        fetch("/download_wav/",{
                            method: "get",
                            headers: {
                                "Content-Type": "application/x-www-form-urlencoded",
                            },
                        }).then(function (response) {
                            if (response.ok) {
                                console.log("下载成功！");
                                response.blob().then(function (blob) {
                                    let url = window.URL.createObjectURL(blob);
                                    player.src = url;
                                    player.play();
                                    console.log("url: ", url);
                                })
                            } else {
                                console.log("下载失败！");
                            }
                        })
                    })
                } else {
                    console.log("上传失败！");
                }
            })
                .catch(function (error) {
                    console.error("Error: ", error);
                });
        }
        reader.readAsDataURL(blob);
      };
    },
    () => {
      console.error("授权失败！");
    }
  );
} else {
  console.error("浏览器不支持 getUserMedia");
}

function draw_logo() {
    let y_list = [35, 20, 20, 0, 25];
    let width = 5;
    let gap = 3;
    let height_list = [10, 30, 20, 35, 10];
    let canvas = document.getElementById('visualizer');
    let ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < y_list.length; i++) {
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(i * (width + gap), y_list[i], width, height_list[i]);
    }
}

function read_chat_list() {
    console.log("read_chat_list");
    let chat_list_html = document.getElementById('chat_list');
    let chat_list = [];
    for (let i = 0; i < chat_list_html.children.length; i++) {
        console.log(chat_list_html.children[i]);
        // if (chat_list_html.children[i].className === 'chat_left') {
        //     chat_list.
        // }
        chat_list.push(chat_list_html.children[i].children[1].innerText);
    }
    console.log("chat_list: ", chat_list);
    return chat_list;
}

//
function logo_animation() {
}

function add_chat_element(last_chat_info, location, name) {
    // <div className="chat_right">
    //     <div className="chat_right_item_1 ">jarvis</div>
    //     <div className="chat_right_item_2 ">
    //         <div className="chat_right_content">
    //             你好
    //         </div>
    //     </div>
    // </div>
    let chat_list_html = document.getElementById('chat_list');
    //在chat_list_html的最后添加一个新的div
    let new_chat_content = document.createElement('div');
    new_chat_content.className = 'chat_' + location + '_content';
    new_chat_content.innerText = last_chat_info;
    let new_chat_item_2 = document.createElement('div');
    new_chat_item_2.className = 'chat_' + location + '_item_2';
    new_chat_item_2.appendChild(new_chat_content);
    let new_chat_item_1 = document.createElement('div');
    new_chat_item_1.className = 'chat_' + location + '_item_1';
    new_chat_item_1.innerText = name;
    let new_chat = document.createElement('div');
    new_chat.className = 'chat_' + location;
    new_chat.appendChild(new_chat_item_1);
    new_chat.appendChild(new_chat_item_2);
    console.log(new_chat);
    chat_list_html.appendChild(new_chat);
}

// 查看当前可用的媒体设备
function getMediaDevices() {
    try {
        navigator.mediaDevices.enumerateDevices().then(function (devices) {
            devices.forEach(function (device) {
                switch (device?.kind) {
                    case 'audioinput':
                        console.log('音频输入设备(麦克风|话筒)：', device);
                        break;
                    case 'audiooutput':
                        console.log('音频输出设备(扬声器|音响)：', device);
                        break;
                    case 'videoinput':
                        console.log('视频输入设备(摄像头|相机)：', device);
                        break;
                    default:
                        console.log('当前可用的媒体设备: ', device);
                        break;
                }
            });
        }).catch(function (err) {
            console.error(err);
        });
    } catch (err) {
        console.error(err);
    } finally {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
            console.log("不支持mediaDevices.enumerateDevices(), 未识别到多媒体设备！");
        }
    }
};
getMediaDevices();
