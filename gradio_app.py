import gradio as gr
import sys
import os

# --- 项目设置 ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from text_to_video.fangzhou.fangzhou_api import UnifiedGenerator
from text_to_video.fangzhou.image_api import generate_image_url

# --- 后端实例化 ---
try:
    generator = UnifiedGenerator()
except (ValueError, ImportError) as e:
    print(f"[Frontend] 后端模块初始化失败: {e}")
    generator = None

# --- UI 定义 ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 方舟统一视频生成器")
    gr.Markdown("请选择模型系列并提供参数。系统将根据您的输入自动调用合适的模型。")

    with gr.Row():
        with gr.Column(scale=3):
            model_selector = gr.Dropdown(
                choices=["doubao-seedance-1.0-pro", "doubao-seedance-1.0-lite"],
                label="选择模型系列",
                value="doubao-seedance-1.0-lite"
            )

            prompt_input = gr.Textbox(label="提示词 (无图片时必填)", lines=4, placeholder="一只可爱的猫在阳光下玩耍...")
            first_frame_input = gr.Textbox(label="首帧图片 URL (可选)", placeholder="http://...")
            last_frame_input = gr.Textbox(label="尾帧图片 URL (仅 Lite 模型支持)", placeholder="http://...", interactive=True)

            with gr.Accordion("通用参数设置", open=False):
                resolution_input = gr.Dropdown(["1080p", "720p"], label="分辨率 (rs)", value="1080p")
                ratio_input = gr.Radio(["16:9", "9:16", "1:1", "4:3", "3:4"], label="宽高比", value="16:9")
                duration_input = gr.Slider(label="时长 (秒)", minimum=1, maximum=15, value=4, step=1)
                fps_input = gr.Slider(label="帧率 (fps)", minimum=8, maximum=30, value=24, step=1)
                seed_input = gr.Number(label="随机种子", value=0, precision=0)
                with gr.Row():
                    watermark_input = gr.Checkbox(label="添加水印", value=True)
                    camerafixed_input = gr.Checkbox(label="固定相机", value=False)

            submit_button = gr.Button("生成视频", variant="primary")

        with gr.Column(scale=2):
            video_output = gr.Video(label="生成结果", interactive=False)

    # --- 图片生成 UI ---
    gr.Markdown("## 方舟图片生成器")
    with gr.Row():
        with gr.Column(scale=3):
            image_prompt_input = gr.Textbox(label="提示词", lines=4, placeholder="鱼眼镜头，一只猫咪的头部……")
            image_submit_button = gr.Button("生成图片", variant="primary")
        with gr.Column(scale=2):
            image_output = gr.Image(label="生成结果", interactive=False)

    # --- 前端逻辑 ---
    def handle_model_change(model_base):
        """当模型变化时，控制尾帧输入框的状态。"""
        if model_base == "doubao-seedance-1.0-pro":
            return gr.update(interactive=False, value="", placeholder="Pro 模型不支持尾帧")
        else: # Lite 模型
            return gr.update(interactive=True, placeholder="http://...")

    def handle_generate_video(model_base, prompt, first_frame, last_frame, resolution, ratio, duration, fps, watermark, camerafixed, seed, progress=gr.Progress(track_tqdm=True)):
        if not generator: raise gr.Error("后端服务未初始化。")
        
        params = {
            "prompt": prompt, "first_frame_url": first_frame, "last_frame_url": last_frame,
            "resolution": resolution, "ratio": ratio, "duration": duration, 
            "framespersecond": fps, "watermark": watermark, "camerafixed": camerafixed, "seed": seed
        }

        try:
            video_url = generator.generate(model_base, params, status_callback=lambda s: progress(0, s))
            return gr.update(value=video_url, visible=True)
        except (RuntimeError, TimeoutError, ValueError) as e:
            raise gr.Error(str(e))

    def handle_generate_image(prompt, progress=gr.Progress(track_tqdm=False)):
        if not prompt or not str(prompt).strip():
            raise gr.Error("提示词不能为空。")
        try:
            url = generate_image_url(prompt)
            return gr.update(value=url, visible=True)
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

    image_submit_button.click(fn=handle_generate_image, inputs=image_prompt_input, outputs=image_output)

# --- 启动应用 ---
if __name__ == "__main__":
    demo.launch()
