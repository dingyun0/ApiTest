import requests
import os
import tempfile
import subprocess

def download_video(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return filename
    except requests.exceptions.RequestException:
        return '4444'

def upload_to_test_env(video_bytes, suffix=".mp4"):
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        try:
            tmp_file.write(video_bytes)
            tmp_file.flush()
            with open(tmp_file.name, "rb") as f:
                files = {"file": ("combined_video.mp4", f, "video/mp4")}
                response = requests.post(upload_url, files=files, verify=True)
                response.raise_for_status()
                result = response.json()
                return result
        finally:
            os.remove(tmp_file.name)

def concatenate_and_upload_videos_with_ffmpeg(video_url1, video_url2,output_filename="combined_video.mp4"):
    """
    下载两个视频，使用 FFmpeg 拼接，然后上传并返回可播放的 URL。
    """
    # 下载视频
    video1_path = download_video(video_url1, "temp_video1.mp4")
    video2_path = download_video(video_url2, "temp_video2.mp4")

    if not video1_path or not video2_path:
        print("由于视频下载失败，无法进行拼接。")
        return '111'

    output_filename = "combined_video_ffmpeg.mp4"
    list_file = "filelist.txt"

    try:
        with open(list_file, "w") as f:
            f.write(f"file '{video1_path}'\n")
            f.write(f"file '{video2_path}'\n")

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
        
        with open(output_filename, "rb") as f:
            video_bytes = f.read()
        result = upload_to_test_env(video_bytes)
        
        video_url = result.get("data", {}).get("url")
        return video_url

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 拼接失败，请检查 FFmpeg 是否已安装并配置好环境变量。错误信息: {e.stderr.decode()}")
        return '222'
    except Exception as e:
        return f"视频处理或上传失败: {e}"
    finally:        
        for p in [video1_path, video2_path, output_filename]:
            if p and os.path.exists(p):
                os.remove(p)

if __name__ == "__main__":  # 判断当前模块是否为主程序入口
    # 请替换为你的视频公网 URL
    url1 = "xx"  # 示例 URL1
    url2 = "xx"  # 示例 URL2
    
    output_video_url = concatenate_and_upload_videos_with_ffmpeg(url1, url2, "my_combined_video_cv.mp4")  # 执行拼接并返回输出 URL
    
    if output_video_url:  # 若返回有效 URL
        print(f"成功创建拼接视频文件：{output_video_url}")  # 打印成功信息
    else:  # 否则视为失败
        print("视频拼接过程失败。")  # 打印失败信息
