import cv2
import requests
import os
import tempfile
import subprocess




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

def upload_to_test_env(video_bytes, suffix=".mp4"):
    """上传视频到指定的测试服务器。"""
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(video_bytes)
        tmp_file.flush()
        with open(tmp_file.name, "rb") as f:
            files = {"file": ("combined_video.mp4", f, "video/mp4")}
            response = requests.post(upload_url, files=files, verify=True)
            response.raise_for_status()
            result = response.json()
            return result



def concatenate_and_upload_videos_with_ffmpeg(video_url1, video_url2,output_filename="combined_video.mp4"):
    """
    下载两个视频，使用 FFmpeg 拼接，然后上传并返回可播放的 URL。
    """
    # 下载视频
    video1_path = download_video(video_url1, "temp_video1.mp4")
    video2_path = download_video(video_url2, "temp_video2.mp4")

    if not video1_path or not video2_path:
        print("由于视频下载失败，无法进行拼接。")
        return None

    output_filename = "combined_video_ffmpeg.mp4"
    list_file = "filelist.txt"

    try:
        # 创建 FFmpeg 拼接所需的列表文件
        with open(list_file, "w") as f:
            f.write(f"file '{video1_path}'\n")
            f.write(f"file '{video2_path}'\n")

        # 使用 subprocess 调用 FFmpeg 命令行进行拼接
        # `-f concat` 表示使用连接器，`-safe 0` 允许读取列表文件中的相对路径
        # `-c copy` 表示复制视频和音频流，不做重新编码，速度最快
        command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            output_filename
        ]
        
        print("正在使用 FFmpeg 拼接视频...")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFmpeg 拼接完成。")
        
        # 将拼接后的视频文件读取为字节流并上传
        with open(output_filename, "rb") as f:
            video_bytes = f.read()
        result = upload_to_test_env(video_bytes)
        
        # 从上传结果中获取可播放的 URL
        video_url = result.get("data", {}).get("url")
        return video_url

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 拼接失败，请检查 FFmpeg 是否已安装并配置好环境变量。错误信息: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"视频处理或上传失败: {e}")
        return None
    finally:
        # 清理所有临时文件
        if os.path.exists(video1_path):
            os.remove(video1_path)
        if os.path.exists(video2_path):
            os.remove(video2_path)
        if os.path.exists(list_file):
            os.remove(list_file)
        if os.path.exists(output_filename):
            os.remove(output_filename)
        print("临时文件已清理。")
# --- 示例用法 ---  # 仅当作为脚本直接运行时执行以下示例
if __name__ == "__main__":  # 判断当前模块是否为主程序入口
    # 请替换为你的视频公网 URL
    url1='xxx'
    url2='xxx'
    output_video_url = concatenate_and_upload_videos_with_ffmpeg(url1, url2, "my_combined_video_cv.mp4")  # 执行拼接并返回输出 URL
    
    if output_video_url:  # 若返回有效 URL
        print(f"成功创建拼接视频文件：{output_video_url}")  # 打印成功信息
    else:  # 否则视为失败
        print("视频拼接过程失败。")  # 打印失败信息
