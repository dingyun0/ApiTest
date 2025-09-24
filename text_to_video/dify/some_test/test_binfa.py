import threading
import requests
import time
import logging

# 1. 配置日志记录器
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO，会记录INFO, WARNING, ERROR, CRITICAL级别的日志
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s', # 定义日志输出格式
    datefmt='%Y-%m-%d %H:%M:%S' # 定义时间格式
)

# --- 配置参数 ---
API_URL = "http://113.45.180.205/v1/workflows/run"
TOTAL_REQUESTS = 1000
CONCURRENT_THREADS = 100

# --- 统计结果 ---
success_count = 0
failure_count = 0
results_lock = threading.Lock()

def make_request():
    """
    发送单个API POST请求并记录结果
    """
    global success_count, failure_count
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer app-8qKLZzUr1EFF7NoEkIKvhiM4" 
        # "Authorization": "Bearer app-sxA7G5J8hqcnVHDKF0rSw0Vk" 
    }
    
    payload = {
        "inputs": {
            "product_description": "豆沙色口红",
            "other_expressive_style": "",
            "other_camera_movement": "",
            "display_method": "",
            "ratio": "9:16",
            "duration": 5,
            "type": ""
        },
        "response_mode": "blocking",
        "user": "abc"
    }

    # payload={
    #     "inputs": {
    #         "test":"1111"
    #     },
    #     "response_mode": "blocking",
    #     "user": "abc"
    # }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=1000)

        if 200 <= response.status_code < 300:
            with results_lock:
                success_count += 1
            # 打印成功的请求结果
            logging.info(f"请求成功: Status Code {response.status_code}, Response: {response.text}")
        else:
            with results_lock:
                failure_count += 1
            # 打印失败的请求结果
            error_details = response.text[:200] if response.text else "No response body"
            logging.error(f"请求失败: Status Code {response.status_code}, Response: {error_details}")

    except requests.exceptions.Timeout:
        # 记录请求超时异常
        with results_lock:
            failure_count += 1
        logging.error("请求异常: Connection timed out")
        
    except requests.exceptions.RequestException as e:
        # 记录其他所有请求相关的异常 (如连接错误)
        with results_lock:
            failure_count += 1
        logging.error(f"请求异常: {e}")


def run_test():
    """
    主测试函数
    """
    logging.info(f"开始并发POST测试...")
    logging.info(f"URL: {API_URL}")
    logging.info(f"总请求数: {TOTAL_REQUESTS}")
    logging.info(f"并发数: {CONCURRENT_THREADS}")
    
    start_time = time.time()
    
    threads = []
    
    requests_per_thread = TOTAL_REQUESTS // CONCURRENT_THREADS
    
    for i in range(CONCURRENT_THREADS):
        # 给每个线程命名，方便在日志中区分
        thread = threading.Thread(
            target=lambda: [make_request() for _ in range(requests_per_thread)],
            name=f"Worker-{i+1}"
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
        
    end_time = time.time()
    duration = end_time - start_time
    
    # --- 打印测试报告 ---
    print("\n--- 测试结果 ---")
    print(f"测试总耗时: {duration:.2f} 秒")
    print(f"成功请求数: {success_count}")
    print(f"失败请求数: {failure_count}")
    if duration > 0:
        rps = TOTAL_REQUESTS / duration
        print(f"吞吐量 (RPS - Requests Per Second): {rps:.2f}")
    print("----------------")
    logging.info("测试完成。")

if __name__ == "__main__":
    run_test()
