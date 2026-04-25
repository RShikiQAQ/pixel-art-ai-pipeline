# 🎮 Pixel Art AI Pipeline

基于 **Stable Diffusion + LoRA + ControlNet** 的像素风格游戏角色生成管线。

上传 OpenPose 骨骼图 → AI 自动生成对应姿势的像素角色，支持批量生成与参数调节。

---

## ✨ 核心功能

| 功能 | 技术实现 | 状态 |
|------|---------|------|
| 🎨 **像素风格生成** | Custom LoRA (`pixel_girl_v1`) | ✅ |
| 🦴 **姿势控制** | ControlNet OpenPose | ✅ |
| 🌐 **REST API** | FastAPI + ComfyUI Backend | ✅ |
| 💻 **Web 界面** | Gradio 前端 | ✅ |
| ⚡ **批量生成** | Python 自动化脚本 | ✅ |
| 🖥️ **GPU 加速** | RTX 4090 + CUDA 12.8 | ✅ |

---

## 🏗️ 系统架构

```
┌─────────────────┐     HTTP POST      ┌──────────────────┐
│   Gradio Web    │ ─────────────────→ │  FastAPI Server  │
│   (Frontend)    │                    │   (Port 8000)    │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                                ↓
                                       ┌──────────────────┐
                                       │   ComfyUI Core   │
                                       │   (Port 8188)    │
                                       └────────┬─────────┘
                                                │
                    ┌──────────────┬────────────┼────────────┬──────────────┐
                    ↓              ↓            ↓            ↓              ↓
              ┌─────────┐   ┌──────────┐ ┌──────────┐ ┌──────────┐   ┌─────────┐
              │ SD 1.5  │   │  LoRA    │ │ControlNet│ │  VAE     │   │ KSampler│
              │Checkpoint│   │pixelgirl │ │ OpenPose │ │ Decode   │   │         │
              └─────────┘   └──────────┘ └──────────┘ └──────────┘   └─────────┘
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/RShikiQAQ/pixel-art-ai-pipeline.git
cd pixel-art-ai-pipeline

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动后端 (ComfyUI + API)

```bash
# 启动 ComfyUI
cd /path/to/ComfyUI
export DISABLE_FLASH_ATTENTION=1
python main.py --listen 127.0.0.1 --port 8188

# 启动 API 服务
cd api
python api_server.py
# Uvicorn running on http://0.0.0.0:8000
```

### 3. 启动前端 (Gradio)

```bash
cd frontend
python gradio_app.py
# Running on local URL: http://localhost:7860
```

### 4. 批量生成

```bash
# 准备姿势图到 poses/ 文件夹
cd scripts
python batch_generate.py
# 生成完成后从服务器 output 目录下载
```

---

## 📡 API 接口

### POST `/generate`
生成像素角色

**参数：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `prompt` | string | 提示词（建议包含 `pixelgirl`）|
| `seed` | int | 随机种子 |
| `lora_strength` | float | LoRA 强度 (0.0-1.5) |
| `pose_image` | file | OpenPose 骨骼图 (PNG) |

**返回：**
```json
{
  "task_id": "task_20260424_003648",
  "comfyui_id": "xxx",
  "status": "processing"
}
```

### GET `/status/{task_id}`
查询生成状态

---

## 🛠️ 技术栈

- **后端**: Python, FastAPI, Uvicorn, aiohttp
- **AI 引擎**: ComfyUI, Stable Diffusion 1.5
- **模型**: Custom LoRA (pixelgirl), ControlNet OpenPose
- **前端**: Gradio
- **硬件**: NVIDIA RTX 4090, CUDA 12.8
- **部署**: Linux Server + SSH 隧道

---

## 📁 项目结构

```
pixel-art-ai-pipeline/
├── api/
│   └── api_server.py          # FastAPI 服务
├── frontend/
│   └── gradio_app.py          # Gradio 网页界面
├── scripts/
│   └── batch_generate.py      # 批量生成脚本
├── workflow/
│   └── workflow.json          # ComfyUI API 格式工作流
├── requirements.txt           # Python 依赖
└── README.md                  # 项目说明
```

---

## 🎯 应用场景

- 🎮 **2D 游戏开发**: 快速生成像素风格 NPC / 主角四方向行走图
- 🎨 **AIGC 创作**: 批量生成统一风格的像素角色素材
- 💼 **技术面试**: 展示 LLM/AIGC 工程化落地能力（模型微调 + 服务化 + 前端）

---

## 📌 注意事项

1. **姿势图格式**: 白色背景 + 黑色火柴人线条（OpenPose 骨骼图）
2. **LoRA 强度**: 1.0 为标准像素风格，0.5 偏写实，1.5 更夸张
3. **显存要求**: 推荐 24GB+（RTX 4090），512x512 分辨率
4. **首次生成慢**: 需要加载模型（约 20 秒），后续每张 1-2 秒

---

## 📄 License

MIT License

---

**Powered by ComfyUI + Stable Diffusion + LoRA + ControlNet**
