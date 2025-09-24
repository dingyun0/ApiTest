# 图片类型的判断方式
import requests
import base64
import os
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv
load_dotenv()

def main(url):
    response = requests.get(url)
    if response.status_code == 200:
        print('111',response.headers)
        print('222',response.content[:100])
        file_content = response.content
        magic_number = file_content[:4]
        # print(magic_number)
        if magic_number.startswith(b'\x89PNG'):
            type="image/png"
        elif magic_number.startswith(b'\xFF\xD8\xFF'):
            type="image/jpeg"
        elif magic_number.startswith(b'GIF8'):
            type="image/gif"
        elif magic_number.startswith(b'BM'):
            type="image/bmp"
        elif magic_number.startswith(b'RIFF') and file_content[8:12] == b'WEBP':
            type="image/webp"
        # mime_type = response.headers['Content-Type']
        base64_data = base64.b64encode(response.content).decode('utf-8')
        base64_with_prefix = f"data:{type};base64,{base64_data}"
        print('333',base64_with_prefix[:100])
        return base64_with_prefix


if __name__=="__main__":
    url="https://youke1.picui.cn/s1/2025/08/21/68a700d86e62e.png"
    base64_with_prefix=main(url)
    # 从环境变量中获取API Key
    client = Ark(
        api_key=os.getenv('ARK_API_KEY'),
        )

    response = client.chat.completions.create(
        # 替换 <MODEL> 为模型的Model ID
        model="doubao-1-5-thinking-pro-m-250415",
        messages=[
            {
                "role": "user",
                "content": [                
                    {"type": "image_url","image_url": {
                        "url":base64_with_prefix
                        }}
                ],
            }
        ],
    )

    print(response.choices[0])