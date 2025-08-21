import time
import jwt
import os
from dotenv import load_dotenv
import requests


load_dotenv()

ak=os.getenv("KL_AK")
sk=os.getenv("KL_SK")
base_url=os.getenv("KL_BASE_URL")

url=f"{base_url}/v1/videos/text2video"

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # 有效时间，此处示例代表当前时间+1800s(30min)
        "nbf": int(time.time()) - 5 # 开始生效的时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

api_token = encode_jwt_token(ak, sk)
print(api_token) # 打印生成的API_TOKEN

headers={
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

data = {
    "model_name": 'kling-v1',
    "prompt": '一只小兔子在草地上跑',
    "negative_prompt": '',
    "cfg_scale": 0.5,
    "mode": 'std',
    # "camera_control": {},
    "aspect_ratio": '16:9',
    "duration": 5
    # "callback_url": '',
    # "external_task_id": ''
}
response = requests.post(url, headers=headers, json=data)
print(response.json())