# 氛围感空镜和人物情景空镜的dify工作流调用

from dotenv import load_dotenv
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DifyApi import DifyApi
load_dotenv()

if __name__=="__main__":
    dify_api=DifyApi(api_key=os.getenv("PRO_MATE_API_KEY"))
    file_path="/Users/donson/Documents/素材/MVC素材/商品素材/挂脖风扇/商品主图-图片1.png"
    user="1234567890"
    file_id=dify_api.upload_file(file_path,user)
    if file_id:
        print(f"文件上传成功，文件ID: {file_id}")
        inputs={
            "creative_description":"动起来",
            "expressive_style":"实拍",
            "framing":"近景",
            "camera_movement":"移镜头",
            "duration":5,
            "ratio":"9:16",
            "image":[
                {
                    "type": "image",
                    "transfer_method": "local_file",
                    "upload_file_id": file_id,
                    # "url": 'https://youke1.picui.cn/s1/2025/07/30/6889cd97a5443.jpg'
                }
            ]
        }
        response=dify_api.run_workflow(inputs,user)
    else:
        print("文件上传失败")







