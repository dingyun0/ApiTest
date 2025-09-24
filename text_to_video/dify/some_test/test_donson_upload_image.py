import requests
import json

def main(files):
    first_file = files[0]  # 取第一个文件（tool_file 对象）
    download_url = first_file.get('url')  # 从字典中取 url
    # filename = first_file.get('filename', 'frame.jpg')
    # mime_type = first_file.get('mime_type', 'image/jpeg')
    # tenant_id = first_file.get('tenant_id')  # 用于 user_id

    # 下载临时文件
    response = requests.get(url=download_url)
    if response.status_code != 200:
        print(f"Error: Download failed with status {response.status_code}")
        return {"files": [], "error": "Download failed111"}

    file_content = response.content
    filename = first_file.get('filename', 'frame.jpg')
    mime_type = first_file.get('mime_type', 'image/jpeg')
    tenant_id = first_file.get('tenant_id')  # 用于 user_id
    headers = {
        "Authorization": "Bearer app-SDLO0PzdJ6TE9IQFPLDugyj3"
    }
    # 重新上传到 Dify 文件系统，指定 local_file
    upload_url = "http://113.45.180.205/v1/files/upload"  # 你的 API 地址；确认端口（默认 8000？测试 curl）
    upload_files = {'file': (filename, file_content, mime_type)}  # 注意：变量名避免与输入 files 冲突
    data = {
        'user_id': tenant_id,  # 或固定值如 'default_user'
        'transfer_method': 'local_file'  # 转换为 local_file
    }
    upload_response = requests.post(url=upload_url, files=upload_files, data=data, headers=headers)
    if not upload_response.ok:
        print(f"Error: Upload failed with status {upload_response.status_code}: {upload_response.text}")
        return {"files": [], "error": "Upload failed"}

    new_file = upload_response.json().get('data')
    print('new_file',new_file)
    if not new_file:
        print("Error: No data in upload response")
        return {"files": [], "error": "Invalid upload response"}

    print(f"Success: Converted to local_file with remote_url: {new_file.get('remote_url')}")
    return {"files": [new_file]}  # 输出标准 Array[files] 格式
# if __name__ == "__main__":
#     files=[
#     {
#       "dify_model_identity": "__dify__file__",
#       "id": None,
#       "tenant_id": "6fea20c8-2343-4bf2-801f-dfa400d3a101",
#       "type": "image",
#       "transfer_method": "tool_file",
#       "remote_url": None,
#       "related_id": "b7bae0b7-2765-4bd5-8146-44db617d2714",
#       "filename": "0e6d211afb9e44fb9a7e847d4176fa3f.jpg",
#       "extension": ".jpg",
#       "mime_type": "image/jpeg",
#       "size": 328109,
#       "url": "http://113.45.180.205//files/tools/b7bae0b7-2765-4bd5-8146-44db617d2714.jpg?timestamp=1757909213&nonce=d7225b0c0ecd05adeef82e98379f89e2&sign=ef8Svvaz3_iYbOHFUIMtOUOVQP2QAsQZYV8eN0OAxhs="
#     }
#   ]
#     print(main(files))

if __name__ == "__main__":
    files=[
    {
      "dify_model_identity": "__dify__file__",
      "id": None,
      "tenant_id": "6fea20c8-2343-4bf2-801f-dfa400d3a101",
      "type": "image",
      "transfer_method": "tool_file",
      "remote_url": None,
      "related_id": "09cd9128-a59c-45ae-bf63-07781e9ea83d",
      "filename": "0ead3fb926bb482daf69b5f008b1d669.jpg",
      "extension": ".jpg",
      "mime_type": "image/jpeg",
      "size": 402727,
      "url": "http://113.45.180.205//files/tools/09cd9128-a59c-45ae-bf63-07781e9ea83d.jpg?timestamp=1757910188&nonce=8ebb9975bd557fe234b3d9a598086125&sign=3C9vH-nRsiIDuG8rAdhYGBpDo-f2XFPrK3FGgdbi8MU="
    }
  ]
    print(main(files))
