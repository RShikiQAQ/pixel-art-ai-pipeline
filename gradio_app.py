import gradio as gr
import requests
import time
import glob
import os
from PIL import Image

API_URL = "http://localhost:8000"
OUTPUT_DIR = "/root/ComfyUI/output"

def generate_character(pose_image_path, prompt, seed, lora_strength):
    """调用后端 API 生成像素角色"""
    if not pose_image_path:
        return "❌ 请先上传姿势图", None
    
    try:
        # 1. 提交任务
        with open(pose_image_path, 'rb') as f:
            files = {'pose_image': ('pose.png', f, 'image/png')}
            data = {
                'prompt': prompt,
                'seed': int(seed),
                'lora_strength': float(lora_strength)
            }
            resp = requests.post(f"{API_URL}/generate", files=files, data=data, timeout=30)
        
        if resp.status_code != 200:
            return f"❌ 生成失败: {resp.text}", None
        
        result = resp.json()
        task_id = result.get("task_id")
        
        # 2. 轮询等待（最多等 2 分钟）
        status = "processing"
        for _ in range(60):
            time.sleep(2)
            s = requests.get(f"{API_URL}/status/{task_id}", timeout=10)
            if s.status_code == 200:
                status_data = s.json()
                status = status_data.get("status", "processing")
                if status == "completed":
                    break
        
        # 3. 读取最新生成的图片
        files = glob.glob(os.path.join(OUTPUT_DIR, "ComfyUI_pixel_*.png"))
        if not files:
            files = glob.glob(os.path.join(OUTPUT_DIR, "ComfyUI_*.png"))
        
        if files:
            latest = max(files, key=os.path.getctime)
            img = Image.open(latest)
            return f"✅ 完成！Task: {task_id}\n📁 {latest}", img
        else:
            return f"⏳ 处理中... Task: {task_id}\n💡 请稍后刷新或去服务器 output 目录查看", None
            
    except Exception as e:
        return f"❌ 错误: {str(e)}", None

# ============ 界面 ============
with gr.Blocks(title="🎮 Pixel Art 角色生成器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎮 Pixel Art 角色生成器
    上传 **OpenPose 骨骼图**（火柴人姿势），AI 自动生成像素风格角色！
    """)
    
    with gr.Row():
        # 左侧：输入区
        with gr.Column(scale=1):
            gr.Markdown("### 🎨 输入参数")
            
            pose_input = gr.Image(
                label="1. 上传姿势图（OpenPose 骨骼图）",
                type="filepath",
                height=300
            )
            
            prompt_input = gr.Textbox(
                label="2. 提示词 Prompt",
                value="pixelgirl, pixel art, 1girl, standing, white background, simple",
                lines=2
            )
            
            with gr.Row():
                seed_input = gr.Number(label="随机种子 Seed", value=12345, precision=0)
                lora_slider = gr.Slider(
                    label="LoRA 强度（像素风格强度）", 
                    minimum=0.0, maximum=1.5, 
                    value=1.0, step=0.1
                )
            
            generate_btn = gr.Button("🚀 生成角色", variant="primary", size="lg")
            
            gr.Markdown("""
            **💡 使用说明：**
            - 姿势图：白色背景 + 黑色火柴人线条（OpenPose 格式）
            - LoRA 强度：1.0 为标准像素风格，0.5 偏写实，1.5 更夸张
            - 生成时间：约 10-30 秒
            """)
        
        # 右侧：结果区
        with gr.Column(scale=1):
            gr.Markdown("### 🖼️ 生成结果")
            status_text = gr.Textbox(label="状态", interactive=False, lines=3)
            result_image = gr.Image(label="生成的像素角色", height=512)
    
    # 绑定按钮
    generate_btn.click(
        fn=generate_character,
        inputs=[pose_input, prompt_input, seed_input, lora_slider],
        outputs=[status_text, result_image]
    )
    
    gr.Markdown("---")
    gr.Markdown("Powered by **ComfyUI + Stable Diffusion + LoRA + ControlNet** | API Server: `localhost:8000`")

if __name__ == "__main__":
    print("🎮 Pixel Art 前端启动中...")
    print("请通过 SSH 隧道访问: http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)