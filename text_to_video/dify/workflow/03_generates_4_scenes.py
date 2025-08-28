# 视频生成四个场景的dify工作流调用

from dotenv import load_dotenv
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DifyApi import DifyApi
load_dotenv()

if __name__=="__main__":
    dify_api=DifyApi(api_key=os.getenv("FOUR_SCENES_API_KEY"))
    file_path="/Users/donson/Documents/素材/MVC素材/商品素材/挂脖风扇/商品主图-图片1.png"
    user="1234567890"
    file_id=dify_api.upload_file(file_path,user)
    if file_id:
        print(f"文件上传成功，文件ID: {file_id}")
        inputs={
            "creative_description":"动起来",
            "duration":5,
            "first_frame":{
                "transfer_method": "remote_url",
                "url": 'https://youke1.picui.cn/s1/2025/07/30/6889cbdbc1334.png',
                "type": "image"
            },
            "last_frame":{
                "transfer_method": "remote_url",
                "url": 'https://youke1.picui.cn/s1/2025/07/30/6889cbdbc1334.png',
                "type": "image"
            },
            "video_type":"手持商品展示视频"
        }
        response=dify_api.run_workflow(inputs,user)
    else:
        print("文件上传失败")







