import os
import time
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

class FangzhouVideoGenerator:
    """
    封装所有与方舟文生视频 API 交互的后端逻辑。
    """
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("环境变量 ARK_API_KEY 未设置。")
        
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.api_key,
        )
        self.model_id = "doubao-seedance-1-0-lite-t2v-250428"

    def _build_prompt(self, prompt, negative_prompt, ratio, duration, fps, seed):
        """内部方法，用于构建符合模型要求的最终提示词字符串。"""
        final_prompt = prompt
        if negative_prompt:
            # 负向提示词的拼接方式可能需要根据模型微调，但通常模型能理解
            final_prompt += f" --negative_prompt {negative_prompt}"
        
        final_prompt += f" --ratio {ratio}"
        final_prompt += f" --duration {duration}"
        final_prompt += f" --fps {fps}"
        if seed > 0:
            final_prompt += f" --seed {seed}"
        
        print(f"[Backend] 构建的最终提示词: {final_prompt}")
        return final_prompt

    def generate(self, prompt, negative_prompt, ratio, duration, fps, seed, status_callback=None):
        """
        公共方法，执行完整的视频生成流程。
        接收纯 Python 参数，返回最终的视频 URL 或抛出异常。
        """
        final_prompt_text = self._build_prompt(prompt, negative_prompt, ratio, duration, fps, seed)

        # 1. 提交任务
        try:
            if status_callback: status_callback("正在提交任务...")
            create_result = self.client.content_generation.tasks.create(
                model=self.model_id,
                content=[{"type": "text", "text": final_prompt_text}]
            )
            task_id = create_result.id
            print(f"[Backend] 任务提交成功, Task ID: {task_id}")
        except Exception as e:
            print(f"[Backend] 任务提交失败: {e}")
            raise RuntimeError(f"任务提交失败: {e}") from e

        # 2. 轮询结果
        if status_callback: status_callback(f"任务已提交 (ID: {task_id[:8]}...), 等待结果中...")
        start_time = time.time()
        while time.time() - start_time < 300:  # 5分钟超时
            try:
                get_result = self.client.content_generation.tasks.get(task_id=task_id)
                status = get_result.status

                if status == "succeeded":
                    print("[Backend] 任务成功。")
                    if status_callback: status_callback("任务成功！正在加载视频...")
                    video_url = get_result.content.video_url
                    print(f"[Backend] 成功提取视频 URL: {video_url}")
                    return video_url
                elif status == "failed":
                    error_info = get_result.error
                    print(f"[Backend] 任务失败: {error_info}")
                    raise RuntimeError(f"任务失败: {error_info}")
                else:
                    print(f"[Backend] 任务状态: {status}")
                    if status_callback: status_callback(f"任务状态: {status}, 持续查询中...")
                    time.sleep(5)
            except Exception as e:
                print(f"[Backend] 查询状态时出错: {e}")
                raise RuntimeError(f"查询状态时出错: {e}") from e

        raise TimeoutError("任务处理超时 (5分钟)。")
