import requests
import os
import tempfile
import ffmpeg
import json
import decode

def download_video(url, filename):
    print(f"开始下载视频：{url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"视频下载成功，保存为：{filename}")
        return filename
    except requests.exceptions.RequestException as e:
        print(f"视频下载失败：{e}")
        return None

def upload_to_test_env(video_bytes, suffix=".mp4"):
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"
    print(f"开始上传视频到测试环境：{upload_url}")
    
    tmp_file_path = ''
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
            tmp_file.write(video_bytes)
            tmp_file.flush()
        
        with open(tmp_file_path, "rb") as f:
            files = {"file": ("combined_video.mp4", f, "video/mp4")}
            response = requests.post(upload_url, files=files, verify=True)
            response.raise_for_status()
            result = response.json()
            print(f"视频上传成功，服务器返回：{json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
    except requests.exceptions.RequestException as e:
        print(f"视频上传失败：{e}")
        raise
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            print(f"临时上传文件已清理：{tmp_file_path}")

def concatenate_and_upload_videos_with_ffmpeg_python(video_url1, video_url2):
    print("--- 视频拼接任务开始 ---")
    video1_path = download_video(video_url1, "temp_video1.mp4")
    video2_path = download_video(video_url2, "temp_video2.mp4")

    if not video1_path or not video2_path:
        print("由于视频下载失败，无法进行拼接。")
        return None

    output_filename = "combined_video_ffmpeg.mp4"

    try:
        print("正在使用 ffmpeg-python 拼接视频...")
        
        input1 = ffmpeg.input(video1_path)
        input2 = ffmpeg.input(video2_path)
        
        # 尝试使用 concat 滤镜进行拼接
        concatenated_video = ffmpeg.concat(input1, input2, v=1, a=1)
        
        ffmpeg.output(concatenated_video, output_filename, acodec='copy', vcodec='copy').run(overwrite_output=True)
        
        print(f"视频拼接完成，文件已保存到：{output_filename}")
        
        with open(output_filename, "rb") as f:
            video_bytes = f.read()
            
        result = upload_to_test_env(video_bytes)
        video_url = result.get("data", {}).get("url")
        print(f"最终拼接视频的公共 URL：{video_url}")
        return video_url

    except ffmpeg.Error as e:
        print("ffmpeg-python 拼接失败。")
        print(f"stderr：{e.stderr.decode('utf8', 'ignore')}")
        print(f"stdout：{e.stdout.decode('utf8', 'ignore')}")
        return None
    except Exception as e:
        print(f"视频处理或上传失败：{e}")
        return None
    finally:        
        for p in [video1_path, video2_path, output_filename]:
            if p and os.path.exists(p):
                os.remove(p)
                print(f"临时文件已清理：{p}")
        print("--- 视频拼接任务结束 ---")

def main(video_url1, video_url2):
    print(f"调用主函数，传入视频 URL1：{video_url1}，URL2：{video_url2}")
    output_video_url = concatenate_and_upload_videos_with_ffmpeg_python(video_url1, video_url2)
    return output_video_url

if __name__ == "__main__":
    url1 = "xx"
    url2 = "xx"
    
    final_url = main(url1, url2)
    
    if final_url:
        print(f"最终结果：成功，URL为：{final_url}")
    else:
        print("最终结果：失败")