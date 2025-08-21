import requests
import base64

def main(url):
    response = requests.get(url)
    if response.status_code == 200:
        file_content = response.content
        magic_number = file_content[:4]
        # base64_data = base64.b64encode(response.content).decode('utf-8')
        # base64_with_prefix = f"data:{mime_type};base64,{base64_data}"
        if magic_number.startswith(b'\x89PNG'):
            return "image/png"
        elif magic_number.startswith(b'\xFF\xD8\xFF'):
            return "image/jpeg"
        elif magic_number.startswith(b'GIF8'):
            return "image/gif"
        elif magic_number.startswith(b'BM'):
            return "image/bmp"
        elif magic_number.startswith(b'RIFF') and file_content[8:12] == b'WEBP':
            return "image/webp"

if __name__=="__main__":
    url="https://static9.yingsaidata.com/2025/08/20/18-46-17/comprehensive_enhance_1755686776800689829_1755686777717142281.jpeg"
    print(main(url))