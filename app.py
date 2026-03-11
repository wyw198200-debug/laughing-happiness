import os
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

import gradio as gr
import torch
from diffusers import StableDiffusionPipeline

MODEL_ID = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TextToImageApp:
    def __init__(self, model_id: str = MODEL_ID, device: str = DEVICE) -> None:
        self.model_id = model_id
        self.device = device
        self.pipe: Optional[StableDiffusionPipeline] = None

    def load_model(self) -> None:
        if self.pipe is not None:
            return

        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            safety_checker=None,
        )
        self.pipe = self.pipe.to(self.device)

        if self.device == "cuda":
            self.pipe.enable_attention_slicing()

    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        steps: int,
        guidance_scale: float,
        width: int,
        height: int,
        seed: int,
    ):
        if not prompt.strip():
            raise gr.Error("请输入有效的提示词")

        self.load_model()

        if seed < 0:
            seed = random.randint(0, 2**31 - 1)

        generator = torch.Generator(device=self.device).manual_seed(seed)

        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            generator=generator,
        ).images[0]

        filename = OUTPUT_DIR / f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{seed}.png"
        image.save(filename)

        meta = (
            f"生成完成\n"
            f"- seed: {seed}\n"
            f"- 模型: {self.model_id}\n"
            f"- 图片尺寸: {width}x{height}\n"
            f"- 结果文件: {filename}"
        )
        return image, meta


def create_ui(app: TextToImageApp) -> gr.Blocks:
    with gr.Blocks(title="Mini Stable Diffusion") as demo:
        gr.Markdown("# 🖼️ Mini Stable Diffusion\n输入文字，生成图片。")

        with gr.Row():
            with gr.Column(scale=2):
                prompt = gr.Textbox(label="提示词", lines=3, placeholder="例如：赛博朋克风格的未来城市，4k")
                negative_prompt = gr.Textbox(
                    label="反向提示词（可选）",
                    lines=2,
                    placeholder="例如：low quality, blurry",
                )

                with gr.Row():
                    steps = gr.Slider(10, 80, value=30, step=1, label="采样步数")
                    guidance = gr.Slider(1.0, 20.0, value=7.5, step=0.5, label="CFG Guidance")

                with gr.Row():
                    width = gr.Dropdown([512, 640, 768], value=512, label="宽度")
                    height = gr.Dropdown([512, 640, 768], value=512, label="高度")
                    seed = gr.Number(value=-1, precision=0, label="Seed（-1 为随机）")

                run_btn = gr.Button("生成图片", variant="primary")

            with gr.Column(scale=3):
                image_out = gr.Image(label="生成结果", type="pil")
                status = gr.Markdown()

        run_btn.click(
            fn=app.generate,
            inputs=[prompt, negative_prompt, steps, guidance, width, height, seed],
            outputs=[image_out, status],
        )

    return demo


def main() -> None:
    app = TextToImageApp()
    demo = create_ui(app)
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
