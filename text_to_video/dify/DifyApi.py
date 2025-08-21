import requests
import os
import json
import mimetypes
from dotenv import load_dotenv

load_dotenv()

class DifyApi:
    def __init__(self,api_key=None,base_url=None):
        self.api_key=api_key
        self.base_url=os.getenv("BASE_URL")
        if not self.api_key or not self.base_url:
            raise ValueError("API_KEY或BASE_URL缺失")
    
    def upload_file(self,file_path,user):
        upload_url=f"{self.base_url}/files/upload"
        headers={
            "Authorization":f"Bearer {self.api_key}",
        }
        mime_type,_=mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type="application/octet-stream"
        try:
            with open(file_path,"rb") as f:
                file={
                    "file":(os.path.basename(file_path),f,mime_type)
                }
                data={
                    "user":user
                }
                response=requests.post(upload_url,headers=headers,files=file,data=data)
                if response.status_code in [200, 201]:
                    file_info=response.json()
                    return file_info.get("id")
                else:
                    print(f"文件上传失败，状态码: {response.status_code}")
                    return None
        except FileNotFoundError:
            print(f"文件不存在: {file_path}")
            return None
        except Exception as e:
            print(f"上传文件时发生错误: {str(e)}")
            return None


    def run_workflow(self,inputs,user,response_mode="blocking",):
        workflow_url =f"{self.base_url}/workflows/run"
        headers={
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type':'application/json'
        }
        
        data = {
            "inputs": inputs,
            "response_mode": response_mode,
            "user": user
        }

        try:
            print("运行工作流...")
            print(f"发送的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            response = requests.post(workflow_url, headers=headers, data=json.dumps(data))
            
            if response.status_code in [200, 201]:
                print("工作流执行成功")
                return response.json()
            else:
                print(f"工作流执行失败，状态码: {response.status_code}")
                print(f"错误响应: {response.text}")
                return {"status": "error", "message": f"Failed to execute workflow, status code: {response.status_code}", "response": response.text}
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return {"status": "error", "message": str(e)}

            

