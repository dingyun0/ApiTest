# 氛围感空镜和人物情景空镜的dify工作流调用

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DifyApi import DifyApi
import json
from dotenv import load_dotenv
load_dotenv()

if __name__=="__main__":
    dify_api=DifyApi(api_key=os.getenv("ATM_PER_API_KEY"))
    inputs={
        "creative_description":"小猫眨眼",
        "expressive_style":"写实",
        "framing":"特写",
        "camera_movement":"拉镜头",
        "duration":3,
        "ratio":"16:9",
        "empty_mirror_type":"氛围感空镜"
    }
    user="1234567890"
    response=dify_api.run_workflow(inputs,user)







