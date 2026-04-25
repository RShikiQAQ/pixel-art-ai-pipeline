import os
import json
import asyncio
import aiohttp
import traceback
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
from datetime import datetime

app = FastAPI(title="Pixel Art Character API with LoRA & ControlNet")

COMFYUI_URL = "http://127.0.0.1:8188"
WORKFLOW_FILE = "workflow.json"
task_status = {}

def load_workflow():
    with open(WORKFLOW_FILE, "r") as f:
        return json.load(f)

@app.post("/generate")
async def generate(
    prompt: str = Form("pixelgirl, pixel art, 1girl, standing"),
    seed: int = Form(12345),
    lora_strength: float = Form(1.0),
    pose_image: UploadFile = File(...)
):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"task_{timestamp}"
        
        # 保存姿势图
        pose_name = f"pose_{timestamp}.png"
        pose_path = f"../input/poses/{pose_name}"
        os.makedirs("../input/poses", exist_ok=True)
        
        with open(pose_path, "wb") as f:
            shutil.copyfileobj(pose_image.file, f)
        print(f"[DEBUG] Saved pose to {pose_path}")

        # 加载并修改 workflow
        workflow = load_workflow()
        
        for node_id, node in workflow.items():
            if not isinstance(node, dict):
                continue
                
            class_type = node.get("class_type", "")
            inputs = node.get("inputs", {})
            
            # 修改 LoadImage (姿势图路径)
            if class_type == "LoadImage" and "image" in inputs:
                inputs["image"] = f"poses/{pose_name}"
                print(f"[DEBUG] Set pose image: poses/{pose_name}")
            
            # 修改 LoRA 强度
            elif class_type == "LoraLoader":
                inputs["strength_model"] = lora_strength
                inputs["strength_clip"] = lora_strength
                print(f"[DEBUG] Set LoRA strength: {lora_strength}")
            
            # 修改正面提示词
            elif class_type == "CLIPTextEncode":
                text = inputs.get("text", "")
                if "pixelgirl" in text.lower() or "bad anatomy" not in text.lower():
                    if "bad anatomy" not in text.lower():  # 这是正面提示
                        inputs["text"] = prompt
                        print(f"[DEBUG] Set prompt: {prompt}")
            
            # 修改 seed
            elif class_type == "KSampler":
                inputs["seed"] = seed
                print(f"[DEBUG] Set seed: {seed}")

        # 发送到 ComfyUI
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{COMFYUI_URL}/prompt", 
                                   json={"prompt": workflow}) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"[ERROR] ComfyUI error: {text}")
                    raise HTTPException(500, f"ComfyUI error: {text}")
                result = await resp.json()
                comfy_id = result.get("prompt_id", task_id)
                print(f"[DEBUG] ComfyUI returned: {comfy_id}")

        task_status[task_id] = {
            "task_id": task_id,
            "comfyui_id": comfy_id,
            "status": "processing",
            "prompt": prompt,
            "lora_strength": lora_strength
        }
        
        return {
            "task_id": task_id,
            "comfyui_id": comfy_id,
            "status": "processing"
        }
        
    except Exception as e:
        print(f"[ERROR] {traceback.format_exc()}")
        raise HTTPException(500, str(e))

@app.get("/status/{task_id}")
async def status(task_id: str):
    if task_id not in task_status:
        raise HTTPException(404, "Task not found")
    return task_status[task_id]

@app.get("/")
async def root():
    return {
        "service": "Pixel Art Character API",
        "features": ["LoRA", "ControlNet OpenPose", "Dynamic Prompt"],
        "endpoints": {
            "POST /generate": "Upload pose image to generate pixel character",
            "GET /status/{task_id}": "Check generation status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Pixel Art API with LoRA + ControlNet support...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
