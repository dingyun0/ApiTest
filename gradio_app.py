import gradio as gr
import sys
import os

# --- 项目设置 ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from text_to_video.fangzhou.fangzhou_api import FangzhouSmartGenerator

# --- 后端实例化 ---
try:
    smart_generator = FangzhouSmartGenerator()
except (ValueError, ImportError) as e:
    print(f"[Frontend] 后端模块初始化失败: {e}")
    smart_generator = None

# --- UI 定义 ---
# 定义所有可能的 UI 组件
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 方舟智能视频生成器")
    gr.Markdown("请选择一个模型系列，并提供相应的参数。系统将根据您的输入自动选择最合适的具体模型进行调用。")

    with gr.Row():
        with gr.Column(scale=3):
            model_base_selector = gr.Dropdown(
                choices=["doubao-seedance-1.0-pro", "doubao-seedance-1.0-lite", "wan2.1-14b"],
                label="选择模型系列",
                value="doubao-seedance-1.0-lite"
            )

            # --- 定义所有可能的输入控件 ---
            with gr.Group(visible=True) as text_inputs:
                prompt_input = gr.Textbox(label="提示词 (文生视频必需)", lines=3)
                negative_prompt_input = gr.Textbox(label="负向提示词 (可选)", lines=2)

            with gr.Group(visible=True) as image_inputs:
                first_frame_input = gr.Textbox(label="首帧图片 URL (图生视频/首尾帧必需)", placeholder="http://...")
                last_frame_input = gr.Textbox(label="尾帧图片 URL (首尾帧必需)", placeholder="http://...")

            with gr.Accordion("高级参数设置", open=False):
                with gr.Group(visible=True) as pro_params:
                    width_input = gr.Slider(label="宽度 (Pro/wan2.1)", minimum=256, maximum=1024, value=1024, step=64)
                    height_input = gr.Slider(label="高度 (Pro/wan2.1)", minimum=256, maximum=1024, value=576, step=64)
                
                with gr.Group(visible=True) as lite_params:
                    ratio_input = gr.Radio(["16:9", "9:16", "1:1"], label="宽高比 (Lite)", value="16:9")

                with gr.Group(visible=True) as common_params:
                    duration_input = gr.Slider(label="时长 (秒)", minimum=1, maximum=15, value=4, step=1)
                    motion_strength_input = gr.Slider(label="运动强度 (图/首尾帧)", minimum=0, maximum=1, value=0.5, step=0.05)
                    seed_input = gr.Number(label="随机种子", value=0, precision=0)

            submit_button = gr.Button("生成视频", variant="primary")

        with gr.Column(scale=2):
            video_output = gr.Video(label="生成结果", interactive=False)

    # --- 前端逻辑 ---
    def handle_model_change(model_base):
        """根据选择的模型系列，动态显示/隐藏相关参数组。"""
        if model_base == "doubao-seedance-1.0-pro":
            return {
                text_inputs: gr.update(visible=True),
                image_inputs: gr.update(visible=False),
                pro_params: gr.update(visible=True),
                lite_params: gr.update(visible=False),
                common_params: gr.update(visible=True)
            }
        elif model_base == "doubao-seedance-1.0-lite":
            return {
                text_inputs: gr.update(visible=True),
                image_inputs: gr.update(visible=True),
                pro_params: gr.update(visible=False),
                lite_params: gr.update(visible=True),
                common_params: gr.update(visible=True)
            }
        elif model_base == "wan2.1-14b":
            return {
                text_inputs: gr.update(visible=True),
                image_inputs: gr.update(visible=True),
                pro_params: gr.update(visible=True),
                lite_params: gr.update(visible=False),
                common_params: gr.update(visible=True)
            }
        return {}

    def handle_generate_video(model_base, prompt, neg_prompt, first_frame, last_frame, width, height, ratio, duration, motion, seed, progress=gr.Progress(track_tqdm=True)):
        if not smart_generator: raise gr.Error("后端服务未初始化。")
        
        # 将所有输入打包成一个字典
        params = {
            "prompt": prompt, "negative_prompt": neg_prompt,
            "first_frame_url": first_frame, "last_frame_url": last_frame,
            "width": width, "height": height, "ratio": ratio,
            "duration": duration, "motion_strength": motion, "seed": seed
        }

        try:
            video_url = smart_generator.generate(model_base, params, status_callback=lambda s: progress(0, s))
            return gr.update(value=video_url, visible=True)
        except (RuntimeError, TimeoutError, ValueError) as e:
            raise gr.Error(str(e))

    # --- 事件绑定 ---
    model_base_selector.change(
        fn=handle_model_change,
        inputs=model_base_selector,
        outputs=[text_inputs, image_inputs, pro_params, lite_params, common_params]
    )

    all_inputs = [model_base_selector, prompt_input, negative_prompt_input, first_frame_input, last_frame_input, width_input, height_input, ratio_input, duration_input, motion_strength_input, seed_input]
    submit_button.click(
        fn=handle_generate_video,
        inputs=all_inputs,
        outputs=video_output
    )
    
    demo.load(fn=handle_model_change, inputs=model_base_selector, outputs=[text_inputs, image_inputs, pro_params, lite_params, common_params])

# --- 启动应用 ---
if __name__ == "__main__":
    demo.launch()