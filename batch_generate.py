import requests
import time
import os
import glob
from pathlib import Path

# ============ 配置 ============
API_URL = "http://localhost:8000"
POSE_DIR = r"D:\\vscode\\study\\pose"          # 姿势图文件夹（放你的 OpenPose 骨骼图）
OUTPUT_DIR = r"D:\\vscode\\study\\pixel_outputs" # 输出文件夹
PROMPT = "pixelgirl, pixel art, 1girl, white background, simple"
LORA_STRENGTH = 1.0
SEEDS = [12345, 12346, 12347]  # 每个姿势生成 3 个版本（不同种子）
POLL_INTERVAL = 3              # 每 3 秒查一次状态
MAX_WAIT = 120                 # 最多等 2 分钟

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_one(pose_path, seed, idx):
    filename = Path(pose_path).stem
    print(f"\n🚀 [{idx}] 正在生成: {filename} | seed={seed}")
    
    with open(pose_path, 'rb') as f:
        files = {'pose_image': (f'{filename}.png', f, 'image/png')}
        data = {'prompt': PROMPT, 'seed': seed, 'lora_strength': LORA_STRENGTH}
        resp = requests.post(f"{API_URL}/generate", files=files, data=data, timeout=30)
    
    if resp.status_code != 200:
        print(f"❌ 提交失败: {resp.text[:100]}")
        return False
    
    task_id = resp.json().get("task_id")
    print(f"⏳ Task: {task_id}")
    
    # 第一张等 25 秒（加载模型慢），之后等 5 秒
    wait = 25 if idx.endswith("1/4") else 5
    print(f"   ... 等待 {wait} 秒")
    time.sleep(wait)
    print(f"✅ [{idx}] 完成")
    return True

def main():
    poses = glob.glob(os.path.join(POSE_DIR, "*.png")) + \
            glob.glob(os.path.join(POSE_DIR, "*.jpg"))
    
    if not poses:
        print(f"❌ {POSE_DIR} 里没有姿势图！先放几张 OpenPose 骨骼图进去")
        return
    
    print(f"📁 找到 {len(poses)} 张姿势图，每张生成 {len(SEEDS)} 个版本")
    print(f"💡 提示：生成完成后，去服务器 ~/ComfyUI/output/ 用 SCP 下载")
    print("-" * 50)
    
    total = 0
    for i, pose in enumerate(poses, 1):
        for seed in SEEDS:
            if generate_one(pose, seed, f"{i}/{len(poses)}"):
                total += 1
                print(f"✅ 完成第 {total} 张")
    
    print(f"\n🎉 全部提交完成！共 {total} 张")
    print(f"📥 下载命令（本地 PowerShell 执行）：")
    print(f"   scp -P [端口] root@[IP]:~/ComfyUI/output/ComfyUI_pixel_*.png {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()