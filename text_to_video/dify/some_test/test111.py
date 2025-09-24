import cv2  # 导入 OpenCV 库，用于视频读写与图像处理
import requests  # 导入 requests 库，用于下载网络资源
import os  # 导入 os 库，用于文件路径和文件操作
import mimetypes  # 导入 mimetypes 库，用于获取文件 MIME 类型
import tempfile
import requests
import os
import socket
import urllib3

def download_video(url, filename):  # 定义函数：下载指定 URL 的视频到本地文件
    """
    从给定的 URL 下载视频文件。
    
    参数:
    url (str): 视频的公共 URL。
    filename (str): 保存视频的文件名。
    
    返回:
    str: 下载后的本地文件路径，如果失败则返回 None。
    """
    print(f"正在下载视频: {url}...")  # 打印下载开始信息
    try:  # 使用 try 捕获网络请求可能出现的异常
        response = requests.get(url, stream=True)  # 发起 HTTP GET 请求，启用流式下载以节省内存
        response.raise_for_status()  # 若状态码非 2xx 则抛出异常
        
        with open(filename, 'wb') as f:  # 以二进制写模式打开目标文件
            for chunk in response.iter_content(chunk_size=8192):  # 分块读取响应内容，避免一次性加载过大数据
                if chunk:  # 确保当前分块非空
                    f.write(chunk)  # 将数据块写入文件
        print(f"视频下载完成，保存为: {filename}")  # 下载成功提示
        return filename  # 返回本地文件路径
    except requests.exceptions.RequestException as e:  # 捕获 requests 相关异常
        print(f"下载失败: {e}")  # 打印错误信息
        return None  # 返回 None 表示失败

def upload_to_test_env(video_bytes,suffix=".mp4"):
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(video_bytes)
        tmp_file.flush()
        with open(tmp_file.name, "rb") as f:
            files = {"file": ("screenshot.mp4", f, "video/mp4")}
            response = requests.post(upload_url, files=files, verify=True)
            response.raise_for_status()
            result = response.json()
            #print("[DEBUG] 上传返回:", result)
            # 根据返回 JSON 解析图片 URL
            # image_url = result.get("data", {}).get("url")
            # print(image_url)
            return result


def concatenate_videos_with_opencv( video_url2, output_filename="combined_video.mp4"):  # 定义函数：下载两个视频并顺序拼接保存

    video2_path = download_video(video_url2, "temp_video2.mp4")  # 下载第二个视频到临时文件并返回路径

    with open(video2_path,"rb") as f:
        video_bytes=f.read()
    result=upload_to_test_env(video_bytes)
    
    # 上传视频到服务器并返回 URL
    video_url = result.get("data", {}).get("url")
    return video_url  # 返回上传后的视频 URL


        
   
# --- 示例用法 ---  # 仅当作为脚本直接运行时执行以下示例
if __name__ == "__main__":  # 判断当前模块是否为主程序入口
    # 请替换为你的视频公网 URL
     url1='xxx'
    url2='xxx'
    output_video_url = concatenate_videos_with_opencv(url2, "my_combined_video_cv.mp4")  # 执行拼接并返回输出 URL
    
    if output_video_url:  # 若返回有效 URL
        print(f"成功创建拼接视频文件：{output_video_url}")  # 打印成功信息
    else:  # 否则视为失败
        print("视频拼接过程失败。")  # 打印失败信息
