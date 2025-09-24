# 导入OpenCV库，用于视频处理和图像操作
import cv2
# 导入requests库，用于发送HTTP请求（下载视频、上传文件）
import requests
# 导入tempfile库，用于创建临时文件
import tempfile
# 导入os库，用于操作系统相关操作（文件删除、路径操作等）
import os
# 导入time库，用于时间相关操作（本代码中未实际使用）
import time
# 导入ssl库，用于SSL/TLS相关操作
import ssl
# 导入socket库，用于网络连接操作
import socket
# 从datetime模块导入datetime类，用于日期时间处理
from datetime import datetime
# 导入urllib3库，用于HTTP客户端操作
import urllib3

# 禁用urllib3库的SSL证书验证警告，避免控制台显示警告信息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 定义检查SSL证书是否过期的函数
def check_ssl_expiry(hostname, port=443):
    # 函数说明：检查指定主机的SSL证书是否过期
    """检查 SSL 证书是否过期"""
    # 使用try-except捕获可能的异常
    try:
        # 创建默认的SSL上下文
        context = ssl.create_default_context()
        # 创建到指定主机和端口的连接，超时时间5秒
        with socket.create_connection((hostname, port), timeout=5) as sock:
            # 使用SSL包装socket连接
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # 获取对等证书信息
                cert = ssock.getpeercert()
                # 解析证书的过期时间，格式化为datetime对象
                expire_date = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                # 获取当前UTC时间
                now = datetime.utcnow()
                # 返回证书是否有效（未过期）和过期时间
                return expire_date > now, expire_date
    # 如果出现任何异常
    except Exception as e:
        # 打印错误信息
        print(f"[SSL] 检查证书失败: {e}")
        # 返回False和None表示检查失败
        return False, None

# 定义上传图片到测试环境的函数
def upload_to_test_env(image_bytes, suffix=".jpg"):
    # 定义上传文件的API接口地址
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"
    
    # 创建一个临时文件，指定后缀名，delete=True表示使用完后自动删除
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp_file:
        # 将图片字节数据写入临时文件
        tmp_file.write(image_bytes)
        # 强制将缓冲区数据写入文件
        tmp_file.flush()
        
        # 以二进制读模式打开临时文件
        with open(tmp_file.name, "rb") as f:
            # 构造上传文件的表单数据，指定文件名和MIME类型
            files = {"file": ("screenshot.jpg", f, "image/jpeg")}
            # 发送POST请求上传文件，verify=True表示验证SSL证书
            response = requests.post(upload_url, files=files, verify=False)
            # 如果HTTP状态码表示错误，抛出异常
            response.raise_for_status()
            # 将响应内容解析为JSON格式
            result = response.json()
            # 注释掉的调试信息打印
            print("[DEBUG] 上传返回:", result)
            
            # 注释掉的从返回结果中提取图片URL的代码
            image_url = result.get("data", {}).get("url")
            print(image_url)
            
            # 返回完整的上传结果
            return result

# 定义主函数，接收视频URL作为参数
def main(video_url: str):
    # 发送GET请求下载视频，stream=True表示流式下载
    response = requests.get(video_url, stream=True)
    # 检查HTTP响应状态码，如果不是200（成功）
    if response.status_code != 200:
        # 打印错误信息
        print("视频下载失败")
        # 退出函数
        return

    # 创建临时文件保存视频，delete=False表示不自动删除，后缀名为.mp4
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    # 分块读取响应内容，每块1MB（1024*1024字节）
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        # 如果块不为空
        if chunk:
            # 将数据块写入临时文件
            tmp_file.write(chunk)
    # 关闭临时文件
    tmp_file.close()

    # 使用OpenCV打开视频文件
    cap = cv2.VideoCapture(tmp_file.name)
    # 检查视频是否成功打开
    if not cap.isOpened():
        # 如果打开失败，打印错误信息
        print("无法打开视频")
        # 退出函数
        return

    # 获取视频总帧数，转换为整数
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("视频帧数为:",frame_count)
    # 检查帧数是否有效
    if frame_count <= 0:
        # 如果帧数无效，打印错误信息
        print("视频帧数为 0")
        # 退出函数
        return

    # 选最后一帧
    last_frame = frame_count-1
    # 设置视频播放位置到选中的帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, last_frame)
    # 读取当前帧，ret表示是否读取成功，frame是图像数据
    ret, frame = cap.read()
    # 释放视频capture对象
    cap.release()
    # 删除临时视频文件
    os.remove(tmp_file.name)

    # 检查是否成功读取帧
    if not ret:
        # 如果读取失败，打印错误信息
        print("读取最后一帧失败")
        # 退出函数
        return

    # 创建临时文件路径用于保存截图，后缀名为.jpg
    screenshot_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
    # 使用OpenCV将帧保存为JPEG图片
    cv2.imwrite(screenshot_path, frame)

    # 以二进制读模式打开截图文件
    with open(screenshot_path, 'rb') as f:
        # 读取图片的字节数据
        img_bytes = f.read()
    
    
    # 调用上传函数，上传图片字节数据
    result = upload_to_test_env(img_bytes)
    # 从返回结果中提取图片URL，使用get方法避免KeyError
    image_url = result.get("data", {}).get("url")
    
    # 检查是否成功获取图片URL
    if image_url:
        # 如果成功，将URL赋值给结果变量
        result_url = image_url
        # 打印图片URL
        print(image_url)
    else:
        # 如果失败，设置错误信息
        result_url = "上传失败"
        # 打印失败信息
        print("上传失败")

    # 注释掉的显示截图代码
    cv2.imshow("Random Frame", frame)  # 在窗口中显示截图
    cv2.waitKey(0)  # 等待用户按键
    cv2.destroyAllWindows()  # 关闭所有OpenCV窗口

    # 检查截图文件是否存在
    if os.path.exists(screenshot_path):
        # 如果存在，删除临时截图文件
        os.remove(screenshot_path)
    
    # 返回包含结果URL的字典
    return {"result_url": result_url}

# 注释掉的主程序入口代码
if __name__ == "__main__":
    # 定义测试视频URL
    video_url = 'http://113.45.180.205//files/c4c027ac-b897-45c7-a241-bf99db06b5a5/file-preview?timestamp=1757902967&nonce=fa9a3f9d921c6bc3a4de8b6b51c03bca&sign=dK71nrk-5ucYv9FFW73qPUiFitEGkNW8DQin9gvm5s0='
    # 调用主函数
    main(video_url)