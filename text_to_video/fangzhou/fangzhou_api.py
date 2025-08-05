import os
import time
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

class FangzhouSmartGenerator:
    """
    封装所有与方舟视频生成 API 交互的后端逻辑。
    能够根据用户选择的模型系列和输入的参数，智能决策使用哪个具体模型。
    """
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("环境变量 ARK_API_KEY 未设置。")
        self.client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=self.api_key)

    def _decide_model_and_validate(self, base_model, params):
        """核心决策逻辑：根据基础模型和参数，决定具体的模型 endpoint 并验证。"""
        has_prompt = bool(params.get("prompt"))
        has_first_frame = bool(params.get("first_frame_url"))
        has_last_frame = bool(params.get("last_frame_url"))

        if base_model == 'doubao-seedance-1.0-pro':
            if has_first_frame or has_last_frame:
                raise ValueError("豆包 Pro 系列只支持文生视频，不能输入图片。")
            return 'doubao-seedance-1-0-pro-250528'

        elif base_model == 'doubao-seedance-1.0-lite':
            if has_first_frame:
                return 'doubao-seedance-1-0-lite-i2v-250428' # 图生视频
            elif has_prompt:
                return 'doubao-seedance-1-0-lite-t2v-250428' # 文生视频
            else:
                raise ValueError("豆包 Lite 系列需要提供提示词或首帧图片。")

        elif base_model == 'wan2.1-14b':
            if has_first_frame and has_last_frame:
                return 'wan2-1-14b-flf2v-250417' # 首尾帧生视频
            elif has_first_frame:
                return 'wan2-1-14b-i2v-250225' # 图生视频
            elif has_prompt:
                return 'wan2-1-14b-t2v-250225' # 文生视频
            else:
                raise ValueError("wan2.1 系列需要提供提示词、首帧或首尾帧图片。")
        
        raise ValueError(f"未知的基础模型系列: {base_model}")

    def _build_request_payload(self, specific_model_id, params):
        """为已确定的具体模型构建 API 请求体。"""
        payload = {"model": specific_model_id, "content": [], "parameters": {}}
        
        # 根据具体模型填充 content 和 parameters
        if specific_model_id == 'doubao-seedance-1-0-pro-250528':
            payload['content'].append({"type": "text", "text": params.get("prompt")})
            payload['parameters'] = {"width": params.get("width", 1024), "height": params.get("height", 576), "duration": params.get("duration", 4), "fps": params.get("fps", 24), "seed": params.get("seed", 0)}
            if params.get("negative_prompt"): payload['parameters']["negative_prompt"] = params["negative_prompt"]
        
        elif specific_model_id == 'doubao-seedance-1-0-lite-t2v-250428':
            prompt_text = f"{params.get('prompt', '')} --ratio {params.get('ratio', '16:9')}"
            payload['content'].append({"type": "text", "text": prompt_text})

        elif specific_model_id == 'doubao-seedance-1-0-lite-i2v-250428':
            payload['content'].append({"type": "image", "url": params["first_frame_url"]})
            payload['parameters'] = {"motion_strength": params.get("motion_strength", 0.5), "seed": params.get("seed", 0)}

        elif specific_model_id == 'wan2-1-14b-flf2v-250417':
            payload['content'].append({"type": "image", "url": params["first_frame_url"]})
            payload['content'].append({"type": "image", "url": params["last_frame_url"]})
            payload['parameters'] = {"duration": params.get("duration", 4), "motion_strength": params.get("motion_strength", 0.5), "seed": params.get("seed", 0)}

        # ... 此处可补充其他 wan2.1 模型的分支 ...

        if not payload.get('parameters'): del payload['parameters']
        print(f"[Backend] 构建的最终载荷: {payload}")
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
