import os
import tempfile
import subprocess
from typing import Optional

import requests


def download_video(url: str, filename: str) -> Optional[str]:
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        with open(filename, "wb") as file_handle:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                file_handle.write(chunk)
        return filename
    except requests.exceptions.RequestException:
        return None


def upload_to_test_env(video_bytes: bytes, suffix: str = ".mp4") -> Optional[str]:
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        try:
            tmp_file.write(video_bytes)
            tmp_file.flush()
            with open(tmp_file.name, "rb") as file_handle:
                files = {"file": ("combined_video.mp4", file_handle, "video/mp4")}
                response = requests.post(upload_url, files=files, timeout=120)
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("url")
        finally:
            os.remove(tmp_file.name)


def concatenate_and_upload_videos_with_ffmpeg(video_url1: str, video_url2: str, output_filename: str = "combined_video_ffmpeg.mp4") -> Optional[str]:
    video1_path = download_video(video_url1, "temp_video1.mp4")
    video2_path = download_video(video_url2, "temp_video2.mp4")

    if not video1_path or not video2_path:
        return None

    list_file = "filelist.txt"

    try:
        with open(list_file, "w") as file_handle:
            file_handle.write(f"file '{video1_path}'\n")
            file_handle.write(f"file '{video2_path}'\n")

        command = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file,
            "-c",
            "copy",
            output_filename,
        ]

        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(output_filename, "rb") as file_handle:
            video_bytes = file_handle.read()
        video_url = upload_to_test_env(video_bytes)
        return video_url
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None
    finally:
        for path in [video1_path, video2_path, output_filename, list_file]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


