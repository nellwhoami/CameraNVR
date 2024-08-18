import os
import time
import schedule
import subprocess
import requests
from datetime import datetime
from bypy import ByPy

bp = ByPy()
BARK_API_URL = 'https://api.day.app/'  # Bark推送的API地址
BARK_API_KEY = ["token"]  # Bark的API Key列表
ENCRYPTION_PASSWORD = 'password'  # 用于加密的密码


def send_bark_notification(title, body):
    try:
        for KEY in BARK_API_KEY:
            response = requests.get(BARK_API_URL + KEY + '/' + title + '/' + body)
            if response.status_code == 200:
                print("Bark推送成功: " + title + '------' + body)
            else:
                print("Bark推送失败:", response.text)
    except Exception as e:
        print("Bark推送失败:", e)

def encrypt_tar(tar_file):
    encrypted_tar_file = tar_file + '.enc'
    # 使用 openssl 命令加密 tar 包
    command = f'openssl enc -aes-256-cbc -salt -in {tar_file} -out {encrypted_tar_file} -k {ENCRYPTION_PASSWORD}'
    subprocess.run(command, shell=True)
    print(f"{tar_file} 已加密为 {encrypted_tar_file}.")
    return encrypted_tar_file

def upload_to_baidu(file, path, i, deletevd):
    if i >= 3:
        print(file + " 上传错误，请检查网络、网盘账户和路径。")
        return
    time.sleep(10)
    print(file + " 正在上传到百度网盘......")
    code = bp.upload(file, '/' + path + '/', ondup='overwrite')  # 使用覆盖上传方式
    if code == 0:
        if deletevd:
            try:
                os.remove(file)  # 上传成功后删除本地的加密 tar 文件
                print(file + " 已删除.")
            except FileNotFoundError:
                print(f"文件 {file} 未找到，无法删除.")
        print(file + " 上传成功！")
        send_bark_notification('vaultwardenweb文件备份成功', '已上传到百度网盘:  ' + file.split('/')[-1])
    else:
        i += 1
        print(file + " 重试次数: " + str(i))
        upload_to_baidu(file, path, i, deletevd)

def backup_and_upload():
    # 获取当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 定义要备份的目录和带有日期的临时打包文件
    source_dir = '/vw-data'
    temp_tar = f'/tmp/vw_data_backup_{current_date}.tar'

    # 打包目录
    command = f'tar -cvf {temp_tar} -C {source_dir} .'
    subprocess.run(command, shell=True)
    print("目录已打包: " + temp_tar)

    # 加密打包文件
    encrypted_tar = encrypt_tar(temp_tar)

    # 删除未加密的 tar 文件
    try:
        os.remove(temp_tar)
        print(temp_tar + " 已删除.")
    except FileNotFoundError:
        print(f"文件 {temp_tar} 未找到，无法删除.")

    # 上传到百度网盘并删除本地加密 tar 文件
    upload_to_baidu(encrypted_tar, 'vw_backup', 0, True)  # 'vw_backup' 是百度网盘中的上传路径

schedule.every().day.at("09:00").do(backup_and_upload)

while True:
    schedule.run_pending()
    time.sleep(1)
