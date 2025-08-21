import os
import time
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

class UnifiedGenerator:
    """
    后端统一生成器。
    严格按照官方文档示例构建 API 请求。
    """
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("环境变量 ARK_API_KEY 未设置。")
        self.client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=self.api_key)

    def _decide_model_and_validate(self, base_model, params):
        """核心决策与验证逻辑。"""
        has_prompt = bool(params.get("prompt"))
        has_first_frame = bool(params.get("first_frame_url"))
        has_last_frame = bool(params.get("last_frame_url"))

        if not has_prompt and not has_first_frame:
            raise ValueError("请求失败：必须提供提示词或首帧图片。")

        if base_model == 'doubao-seedance-1.0-pro':
            if has_last_frame:
                raise ValueError("模型不匹配：Pro 模型不支持尾帧输入。")
            return 'doubao-seedance-1-0-pro-250528'

        elif base_model == 'doubao-seedance-1.0-lite':
            if has_first_frame or has_last_frame:
                return 'doubao-seedance-1-0-lite-i2v-250428'
            else:
                return 'doubao-seedance-1-0-lite-t2v-250428'
        
        raise ValueError(f"未知的基础模型系列: {base_model}")

    def _build_request_payload(self, specific_model_id, params):
        """为所有模型统一构建请求体，严格遵循文档格式。"""
        payload = {"model": specific_model_id, "content": []}
        
        # 1. 构建基础提示词文本，并将所有通用参数统一拼接到文本中
        prompt_text = params.get("prompt", "")
        # 使用文档规定的正确缩写
        # prompt_text += f" --rs {params.get('resolution', '1080p')}" # 暂时注释，因为输入格式需要调整
        prompt_text += f" --ratio {params.get('ratio', '16:9')}"
        prompt_text += f" --dur {params.get('duration', 4)}"
        prompt_text += f" --fps {params.get('framespersecond', 24)}"
        if params.get('watermark', True):
            prompt_text += " --wm true"
        else:
            prompt_text += " --wm false"
        if params.get('seed', 0) > 0:
            prompt_text += f" --seed {params['seed']}"
        if params.get('camerafixed', False):
            prompt_text += " --camera_fixed true"

        # 2. 添加文本对象到 content 列表
        # 即使提示词为空（在图生视频中可选），也需要添加这个 text 对象
        payload["content"].append({"type": "text", "text": prompt_text.strip()})

        # 3. 根据文档，正确地添加图片对象
        first_frame_url = params.get("first_frame_url")
        last_frame_url = params.get("last_frame_url")

        if first_frame_url:
            image_obj = {
                "type": "image_url",
                "image_url": {"url": first_frame_url}
            }
            # 如果是首尾帧模式，为首帧添加 role
            if last_frame_url:
                image_obj["role"] = "first_frame"
            payload["content"].append(image_obj)

        if last_frame_url:
            payload["content"].append({
                "type": "image_url",
                "image_url": {"url": last_frame_url},
                "role": "last_frame"
            })

        # print(f"[Backend] 构建的最终载荷: {payload}")
        return payload

    def generate(self, base_model, params, status_callback=None):
        """公共方法，执行完整的视频生成流程。"""
        try:
            specific_model_id = self._decide_model_and_validate(base_model, params)
            payload = self._build_request_payload(specific_model_id, params)
            if status_callback: status_callback("正在提交任务...")
            create_result = self.client.content_generation.tasks.create(**payload)
            task_id = create_result.id
        except (ValueError, Exception) as e:
            raise RuntimeError(f"任务提交失败: {e}") from e

        # 轮询逻辑 (不变)
        if status_callback: status_callback(f"任务已提交 (ID: {task_id[:8]}...), 等待结果中...")
        start_time = time.time()
        while time.time() - start_time < 600:
            try:
                get_result = self.client.content_generation.tasks.get(task_id=task_id)
                if get_result.status == "succeeded":
                    if status_callback: status_callback("任务成功！")
                    return get_result.content.video_url
                elif get_result.status == "failed":
                    raise RuntimeError(f"任务失败: {get_result.error}")
                else:
                    if status_callback: status_callback(f"任务状态: {get_result.status}, 查询中...")
                    time.sleep(8)
            except Exception as e:
                raise RuntimeError(f"查询状态时出错: {e}") from e
        raise TimeoutError("任务处理超时。")
