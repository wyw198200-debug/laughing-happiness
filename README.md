# Mini Stable Diffusion（文本生成图片）

这是一个轻量版“类似 Stable Diffusion”的文本生成图片应用。你可以输入中文或英文提示词，生成对应图像。

## 功能

- 文本生成图片（Text-to-Image）
- 支持反向提示词（negative prompt）
- 可调采样步数、CFG Guidance、图片分辨率
- 支持固定 seed（便于复现）
- 自动保存生成结果到 `outputs/`

## 环境要求

- Python 3.10+
- 建议有 NVIDIA GPU（CPU 也可运行，但速度较慢）

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 启动

```bash
python app.py
```

启动后访问：`http://127.0.0.1:7860`

## 模型说明

默认模型是：

- `runwayml/stable-diffusion-v1-5`

你也可以通过环境变量切换模型：

```bash
export SD_MODEL_ID="stabilityai/stable-diffusion-2-1"
python app.py
```

## 注意事项

- 首次运行会从 Hugging Face 下载模型，耗时较长。
- 需要能访问 Hugging Face 模型仓库。
- 若在 GPU 上运行，请确保 CUDA 与 PyTorch 版本匹配。
