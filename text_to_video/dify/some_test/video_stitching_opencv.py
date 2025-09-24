import cv2  # 导入 OpenCV 库，用于视频读写与图像处理
import requests  # 导入 requests 库，用于下载网络资源
import os  # 导入 os 库，用于文件路径和文件操作
import mimetypes  # 导入 mimetypes 库，用于获取文件 MIME 类型
import tempfile
import requests
import os
import socket
import urllib3

def download_video(url, filename):  # 定义函数：下载指定 URL 的视频到本地文件
    """
    从给定的 URL 下载视频文件。
    
    参数:
    url (str): 视频的公共 URL。
    filename (str): 保存视频的文件名。
    
    返回:
    str: 下载后的本地文件路径，如果失败则返回 None。
    """
    print(f"正在下载视频: {url}...")  # 打印下载开始信息
    try:  # 使用 try 捕获网络请求可能出现的异常
        response = requests.get(url, stream=True)  # 发起 HTTP GET 请求，启用流式下载以节省内存
        response.raise_for_status()  # 若状态码非 2xx 则抛出异常
        
        with open(filename, 'wb') as f:  # 以二进制写模式打开目标文件
            for chunk in response.iter_content(chunk_size=8192):  # 分块读取响应内容，避免一次性加载过大数据
                if chunk:  # 确保当前分块非空
                    f.write(chunk)  # 将数据块写入文件
        print(f"视频下载完成，保存为: {filename}")  # 下载成功提示
        return filename  # 返回本地文件路径
    except requests.exceptions.RequestException as e:  # 捕获 requests 相关异常
        print(f"下载失败: {e}")  # 打印错误信息
        return None  # 返回 None 表示失败

def upload_to_test_env(video_bytes,suffix=".mp4"):
    upload_url = "https://testwiseapi.yingsaidata.com/v1/common/uploadFile"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(video_bytes)
        tmp_file.flush()
        with open(tmp_file.name, "rb") as f:
            files = {"file": ("screenshot.mp4", f, "video/mp4")}
            response = requests.post(upload_url, files=files, verify=False)
            response.raise_for_status()
            result = response.json()
            #print("[DEBUG] 上传返回:", result)
            # 根据返回 JSON 解析图片 URL
            # image_url = result.get("data", {}).get("url")
            # print(image_url)
            return result


def concatenate_videos_with_opencv(video_url1, video_url2, output_filename="combined_video.mp4"):  # 定义函数：下载两个视频并顺序拼接保存
    """
    下载两个视频，并使用 OpenCV 将它们逐帧拼接在一起。
    
    参数:
    video_url1 (str): 第一个视频的公共 URL。
    video_url2 (str): 第二个视频的公共 URL。
    output_filename (str): 拼接后视频的输出文件名。
    
    返回:
    str: 拼接后的视频 URL，如果失败则返回 None。
    """
    # 下载视频
    video1_path = download_video(video_url1, "temp_video1.mp4")  # 下载第一个视频到临时文件并返回路径
    video2_path = download_video(video_url2, "temp_video2.mp4")  # 下载第二个视频到临时文件并返回路径

    if not video1_path or not video2_path:  # 若任一下载失败则提前返回
        print("由于视频下载失败，无法进行拼接。")  # 输出错误提示
        return None  # 返回 None 表示失败

    cap1 = None  # 初始化视频捕获对象1占位
    cap2 = None  # 初始化视频捕获对象2占位
    out = None  # 初始化视频输出对象占位

    try:  # 使用 try/finally 确保资源释放
        # 打开视频文件
        cap1 = cv2.VideoCapture(video1_path)  # 基于第一个视频路径创建视频捕获对象
        cap2 = cv2.VideoCapture(video2_path)  # 基于第二个视频路径创建视频捕获对象
        
        # 检查文件是否成功打开
        if not cap1.isOpened():  # 若第一个视频未成功打开
            raise IOError(f"无法打开视频文件: {video1_path}")  # 抛出 I/O 错误
        if not cap2.isOpened():  # 若第二个视频未成功打开
            raise IOError(f"无法打开视频文件: {video2_path}")  # 抛出 I/O 错误

        # 获取第一个视频的属性
        width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取帧宽并转为整数
        height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取帧高并转为整数
        fps = cap1.get(cv2.CAP_PROP_FPS)  # 获取帧率（fps）
        
        # 确定视频编码器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # 根据需要选择编码器，如 'mp4v', 'XVID', 'avc1'  # 选择 mp4v 编码器
        
        # 创建 VideoWriter 对象
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))  # 创建输出视频写入器
        
        # 拼接视频
        print("正在拼接视频...")  # 打印处理进度
        
        # 写入第一个视频
        while True:  # 循环读取第一个视频的所有帧
            ret, frame = cap1.read()  # 读取一帧，ret 表示是否成功，frame 为图像
            if not ret:  # 若读取失败或结束
                break  # 退出循环
            out.write(frame)  # 将该帧写入输出视频
            
        # 调整第二个视频帧的尺寸以匹配第一个视频
        print("正在处理第二个视频并写入...")  # 打印处理第二个视频提示
        while True:  # 循环读取第二个视频的所有帧
            ret, frame = cap2.read()  # 读取一帧
            if not ret:  # 若读取失败或结束
                break  # 退出循环
            # 缩放帧以匹配第一个视频的尺寸
            if frame.shape[1] != width or frame.shape[0] != height:  # 若当前帧尺寸与目标尺寸不一致
                frame = cv2.resize(frame, (width, height))  # 调整帧大小以匹配
            out.write(frame)  # 写入调整（或原始）后的帧
            
        print(f"视频拼接完成，文件已保存到: {output_filename}")  # 输出完成提示
        with open(output_filename,"rb") as f:
            video_bytes=f.read()
        result=upload_to_test_env(video_bytes)
        
        # 上传视频到服务器并返回 URL
        video_url = result.get("data", {}).get("url")
        return video_url  # 返回上传后的视频 URL

    except Exception as e:  # 捕获任意异常
        print(f"视频拼接失败: {e}")  # 打印错误信息
        return None  # 返回 None 表示失败
        
    finally:  # 无论成功或失败都执行资源释放与清理
        # 释放资源
        if cap1:  # 若 cap1 已创建
            cap1.release()  # 释放视频捕获对象1
        if cap2:  # 若 cap2 已创建
            cap2.release()  # 释放视频捕获对象2
        if out:  # 若 out 已创建
            out.release()  # 释放视频写入器
            
        # 清理临时文件
        if os.path.exists(video1_path):  # 若临时文件1存在
            os.remove(video1_path)  # 删除临时文件1
        if os.path.exists(video2_path):  # 若临时文件2存在
            os.remove(video2_path)  # 删除临时文件2
        print("临时文件已清理。")  # 打印清理完成提示

# --- 示例用法 ---  # 仅当作为脚本直接运行时执行以下示例
if __name__ == "__main__":  # 判断当前模块是否为主程序入口
    # 请替换为你的视频公网 URL
    url1='xxx'
    url2='xxx'
    output_video_url = concatenate_videos_with_opencv(url1, url2, "my_combined_video_cv.mp4")  # 执行拼接并返回输出 URL
    
    if output_video_url:  # 若返回有效 URL
        print(f"成功创建拼接视频文件：{output_video_url}")  # 打印成功信息
    else:  # 否则视为失败
        print("视频拼接过程失败。")  # 打印失败信息
