Video Tools API 使用说明

启动服务：

```bash
cd /Users/donson/Documents/projects/ApiTest_vivian/ApiTest
source ../venv/bin/activate
uvicorn api_server:app --host 0.0.0.0 --port 8080 --log-level info
```

可选环境变量：

```bash
export FFMPEG_PATH=$(which ffmpeg)
```

健康检查：

```bash
curl http://47.121.26.40:8080/health
```

视频拼接接口（POST /video/concat）：

请求体：

```json
{
  "video_url1": "https://example.com/a.mp4",
  "video_url2": "https://example.com/b.mp4"
}
```

成功响应：

```json
{
  "url": "https://.../combined_video.mp4",
  "message": "success"
}
```

注意：两个视频需编码参数一致以支持 `-c copy` 直接拼接，否则需转码再拼接。


