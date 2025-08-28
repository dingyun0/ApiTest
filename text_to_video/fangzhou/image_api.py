import os
from typing import Optional

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark


def generate_image_url(prompt: str, model: str = "doubao-seedream-3-0-t2i-250415") -> str:

    if not prompt or not prompt.strip():
        raise ValueError("提示词不能为空。")

    load_dotenv()
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise ValueError("环境变量 ARK_API_KEY 未设置。")

    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )

    try:
        response = client.images.generate(model=model, prompt=prompt,response_format="url",size="1024x1024",seed=12,guidance_scale=2.5,watermark=False)
    except Exception as e:
        raise RuntimeError(f"生成失败: {e}") from e

    if not hasattr(response, "data") or not response.data:
        raise RuntimeError("生成失败：无返回数据。")

    first_item = response.data[0]
    url: Optional[str] = getattr(first_item, "url", None)
    if not url:
        raise RuntimeError("生成失败：未返回图片 URL。")

    return url


