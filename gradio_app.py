import gradio as gr
import sys
import os
import base64
import io
from PIL import Image
from pathlib import Path

# --- 项目设置 ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from text_to_video.fangzhou.fangzhou_api import UnifiedGenerator
from text_to_video.fangzhou.image_api import generate_image_url

# --- 后端实例化 ---
try:
    generator = UnifiedGenerator()
except (ValueError, ImportError) as e:
    print(f"[Frontend] 初始化失败: {e}")
    generator = None

# --- UI 定义 ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 方舟-视频生成")

    with gr.Row():
        with gr.Column(scale=3):
            model_selector = gr.Dropdown(
                choices=["doubao-seedance-1.0-pro", "doubao-seedance-1.0-lite"],
                label="选择模型系列",
                value="doubao-seedance-1.0-lite"
            )

            prompt_input = gr.Textbox(label="提示词 (无图片时必填)", lines=4, placeholder="一只可爱的猫在阳光下玩耍...")
            
            with gr.Row():
                first_frame_input = gr.Image(label="首帧图片 (可选)", type="pil", height=200)
                last_frame_input = gr.Image(label="尾帧图片 (仅 Lite 模型支持)", type="pil", height=200, interactive=True)

            with gr.Accordion("通用参数设置", open=False):
                resolution_input = gr.Dropdown(["1080p", "720p"], label="分辨率 (rs)", value="1080p")
                ratio_input = gr.Radio(["16:9", "9:16", "1:1", "4:3", "3:4"], label="宽高比", value="16:9")
                duration_input = gr.Slider(label="时长 (秒)", minimum=1, maximum=15, value=4, step=1)
                fps_input = gr.Slider(label="帧率 (fps)", minimum=8, maximum=30, value=24, step=1)
                seed_input = gr.Number(label="随机种子", value=0, precision=0)
                with gr.Row():
                    watermark_input = gr.Checkbox(label="添加水印", value=False)
                    camerafixed_input = gr.Checkbox(label="固定相机", value=False)

            submit_button = gr.Button("生成视频", variant="primary")

        with gr.Column(scale=2):
            video_output = gr.Video(label="生成结果", interactive=False)

    # --- 图片生成 UI ---
    gr.Markdown("## 方舟图片生成")
    with gr.Row():
        with gr.Column(scale=3):
            image_prompt_input = gr.Textbox(label="提示词", lines=4, placeholder="鱼眼镜头，一只猫咪的头部……")
            
            # image_upload_input = gr.Image(label="上传图片 (图生图，可选)", type="pil", height=300)
            
            image_submit_button = gr.Button("生成图片", variant="primary")
        with gr.Column(scale=2):
            image_output = gr.Gallery(label="生成结果", columns=2, height="auto", interactive=False)

    # --- 前端逻辑 ---
    def pil_to_data_uri(img):
        """将 PIL Image 对象转换为 Base64 编码的 Data URI"""
        if img is None:
            return None

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        encoded_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded_string}"

    def handle_model_change(model_base):
        """当模型变化时，控制尾帧输入框的状态。"""
        if model_base == "doubao-seedance-1.0-pro":
            # Pro 模型不支持尾帧，禁用并清空
            return gr.update(interactive=False, value=None)
        else: # Lite 模型
            return gr.update(interactive=True)

    def handle_generate_video(model_base, prompt, first_frame_pil, last_frame_pil, resolution, ratio, duration, fps, watermark, camerafixed, seed, progress=gr.Progress(track_tqdm=True)):
        if not generator: raise gr.Error("后端服务未初始化。")
        
        try:
            # 将 PIL Image 转换为 Base64 Data URI
            first_frame_url = pil_to_data_uri(first_frame_pil)
            last_frame_url = pil_to_data_uri(last_frame_pil)

            params = {
                "prompt": prompt, "first_frame_url": first_frame_url, "last_frame_url": last_frame_url,
                "resolution": resolution, "ratio": ratio, "duration": duration, 
                "framespersecond": fps, "watermark": watermark, "camerafixed": camerafixed, "seed": seed
            }

            video_url = generator.generate(model_base, params, status_callback=lambda s: progress(0, s))
            return gr.update(value=video_url, visible=True)
        except (RuntimeError, TimeoutError, ValueError) as e:
            raise gr.Error(str(e))

    def handle_generate_image(prompt, progress=gr.Progress(track_tqdm=True)):
        if not prompt or not str(prompt).strip():
            raise gr.Error("提示词不能为空。")
        
        # 为图生图功能保留的警告
        # if image_pil:
        #     # 转换图片，但暂不使用，因为后端功能未实现
        #     image_data_uri = pil_to_data_uri(image_pil)
        #     gr.Warning("图生图功能暂未实现，将仅根据提示词生成图片。")

        try:
            image_urls = []
            num_images = 4
            # 使用 tqdm 创建进度条
            for i in progress.tqdm(range(num_images), desc="正在生成图片..."):
                # 为确保每次生成结果不同，可以考虑在 prompt 或 seed 中加入变量
                # 此处后端 API 未体现 seed，暂时调用多次相同 prompt
                url = generate_image_url(prompt)
                image_urls.append(url)
            
            return image_urls # 直接返回 URL 列表
        except (RuntimeError, ValueError) as e:
            raise gr.Error(str(e))

    # --- 事件绑定 ---
    model_selector.change(fn=handle_model_change, inputs=model_selector, outputs=last_frame_input)

    all_inputs = [
        model_selector, prompt_input, first_frame_input, last_frame_input, 
        resolution_input, ratio_input, duration_input, fps_input, 
        watermark_input, camerafixed_input, seed_input
    ]
    submit_button.click(fn=handle_generate_video, inputs=all_inputs, outputs=video_output)

    image_submit_button.click(fn=handle_generate_image, inputs=[image_prompt_input], outputs=image_output)

# --- 启动应用 ---
if __name__ == "__main__":
    demo.launch(
        max_file_size="10mb" # 设置最大文件上传大小为10MB
    )
