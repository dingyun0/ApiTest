import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from text_to_video.dify.utils.ffmpeg_concat import concatenate_and_upload_videos_with_ffmpeg


class ConcatRequest(BaseModel):
    video_url1: HttpUrl
    video_url2: HttpUrl


class ConcatResponse(BaseModel):
    url: Optional[HttpUrl]
    message: str


app = FastAPI(title="Video Tools API", version="1.0.0")


@app.post("/video/concat", response_model=ConcatResponse)
def concat_videos(payload: ConcatRequest) -> ConcatResponse:
    if not os.environ.get("FFMPEG_PATH"):
        # 可选：允许用户通过环境变量指定 ffmpeg，可缺省使用系统路径
        pass

    url = concatenate_and_upload_videos_with_ffmpeg(str(payload.video_url1), str(payload.video_url2))
    if not url:
        raise HTTPException(status_code=500, detail="视频拼接失败或上传失败")
    return ConcatResponse(url=url, message="success")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


