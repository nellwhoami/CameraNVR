import os
import cv2
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from bypy import ByPy
import numpy as np
import requests


# 初始化ByPy
bp = ByPy()

# 设置参数
Cameraname = 'videos'  # 摄像头名称
videopath = './Camera/'  # 本地文件路径
NVRurl = 'rtsp://admin:password@192.168.1.22:554/stream1'  # 视频流URL
videotime = 1  # 录制视频时长（分钟）
Updisk = True  # 是否上传到网盘？（True 表示上传；False 表示不上传）
deletevd = True  # 上传后是否删除视频文件？（True 表示删除；False 表示保留）
BARK_API_URL = 'https://api.day.app/' # Bark推送的API地址
BARK_API_KEY = ["key111","key222"]# Bark推送的KEY ,一个手机就填一个就好了

# 发送Bark推送消息
def send_bark_notification(title, body):
    try:
        for KEY in BARK_API_KEY:
            response = requests.get(BARK_API_URL + KEY + '/' + title + '/' + body)
            if response.status_code == 200:
                print("Bark推送成功！")
            else:
                print("Bark推送失败:", response.text)
    except Exception as e:
        print("Bark推送失败:", e)

# 上传视频到百度网盘
def upload_to_baidu(file, path, i, deletevd):
    if i >= 3:
        print(file + " 上传错误，请检查网络、网盘账户和路径。")
        return
    time.sleep(10)
    print(file + " 正在上传到百度网盘......")
    code = bp.upload(file, '/' + path + '/', ondup='overwrite')  # 使用覆盖上传方式
    if code == 0:
        if deletevd:
            os.remove(file)
        print(file + " 上传成功！")
        send_bark_notification('警告! 检测到门口摄像头下有人经过', '视频已上传到百度网盘:  ' + file.split('/')[-1])
    else:
        i += 1
        print(file + " 重试次数: " + str(i))
        upload_to_baidu(file, path, i, deletevd)

# 使用YOLOv3进行行人检测
def detect_pedestrians_yolo(frame, net, ln, confidence_threshold=0.5):
    (H, W) = frame.shape[:2]

    # 将帧转换为blob格式
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(ln)

    boxes = []
    confidences = []
    classIDs = []

    # 循环遍历每个输出层
    for output in layer_outputs:
        # 循环遍历每个检测
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # 只保留置信度大于阈值的检测结果
            if confidence > confidence_threshold and classID == 0:  # 0 表示行人类别
                # 计算边界框坐标
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # 使用非最大抑制筛选最终的边界框
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.3)

    pedestrians = []
    if len(indices) > 0:
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            pedestrians.append((x, y, x + w, y + h))

    return pedestrians

# 视频录制函数
def record_video_yolo(cap, net, ln, videopath, Cameraname, fps, size):
    frame_counter = 0
    recording = False
    start_recording_time = None
    video_path = None
    upload_tasks = []
    print("检测是否有人经过......")
    with ThreadPoolExecutor() as executor:
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_counter += 1
                if frame_counter % 3 != 0:
                    continue
                pedestrians = detect_pedestrians_yolo(frame, net, ln)
                if len(pedestrians) > 0:
                    if not recording:
                        print("检测到行人，开始录制视频...")
                        send_bark_notification('警告! 检测到门口摄像头下有人经过', '正在录制视频......')
                        recording = True
                        start_recording_time = time.time()
                        filename = str(time.strftime("%Y年%m月%d日--%H时%M分%S秒", time.localtime()))+ '.avi'
                        video_path = os.path.join(videopath, filename)
                        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), fps / 2.5, size)

                if recording:
                    out.write(frame)
                    if time.time() - start_recording_time >= videotime * 60:
                        print("未检测到行人或录制时间到达，停止录制视频...")
                        out.release()
                        recording = False
                        if Updisk:
                            upload_task = executor.submit(upload_to_baidu, video_path, Cameraname, 0, deletevd)
                            upload_tasks.append(upload_task)
                            send_bark_notification('警告! 检测到门口摄像头下有人经过', '视频正在上传到百度网盘:  ' + filename)
        finally:
            # 显式关闭线程池，确保所有线程都已终止
            executor.shutdown()

    # 等待所有上传任务完成
    wait(upload_tasks, return_when=ALL_COMPLETED)

    cap.release()

if __name__ == '__main__':
    # 加载YOLO模型和权重文件
    weights_path = 'yolov3.weights'
    config_path = 'yolov3.cfg'
    names_path = 'coco.names'

    print("开始加载模型...")
    net = cv2.dnn.readNet(weights_path, config_path)
    print("模型加载完成。")
    unconnected_layers = net.getUnconnectedOutLayers()
    #print("未连接输出层获取完成：", unconnected_layers)
    #print("未连接输出层索引：", [layer - 1 for layer in unconnected_layers])

    ln = net.getLayerNames()
    ln = [ln[layer - 1] for layer in unconnected_layers]

    # 从网络摄像头获取视频流
    cap = cv2.VideoCapture(NVRurl)  # 使用 NVRurl 中指定的网络摄像头
    if not cap.isOpened():
        print("无法打开视频流，请检查网络摄像头连接或者 URL 设置。")
        exit()

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps >= 30:
        fps = 30
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    videopath = os.path.join(videopath, Cameraname)
    if not os.path.exists(videopath):
        try:
            os.makedirs(videopath)
        except:
            print("请手动创建文件夹")
            exit()

    record_video_yolo(cap, net, ln, videopath, Cameraname, fps, size)
