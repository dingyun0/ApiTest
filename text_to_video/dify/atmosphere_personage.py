# 氛围感空镜和人物情景空镜的dify工作流调用

from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

api_key=os.getenv("ATM_PER_API_KEY")
base_url=os.getenv("ATM_PER_BASE_URL")

def run_workflow(inputs,user,response_mode="blocking",):
    workflow_url =f"{base_url}/workflows/run"
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type':'application/json'
    }
    
    data = {
        "inputs": inputs,
        "response_mode": response_mode,
        "user": user
    }

    try:
        print("运行工作流...")
        response = requests.post(workflow_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("工作流执行成功")
            return response.json()
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")
            return {"status": "error", "message": f"Failed to execute workflow, status code: {response.status_code}"}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__=="__main__":
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
    response=run_workflow(inputs,user)
    print(response)







