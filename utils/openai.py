import os
import base64
from openai import OpenAI
from typing import Union, Sequence
from streamlit.runtime.uploaded_file_manager import UploadedFile

class CompletionUtils:
    @staticmethod
    def text_completion(client: OpenAI, prompt: str, messages: Sequence[dict]):
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        completion = client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=messages,
            # 设置输出数据的模态，当前支持["text"]
            modalities=["text"],
            # stream 必须设置为 True，否则会报错
            stream=True,
            stream_options={
                "include_usage": True
            }
        )
        response, usage = [], None
        for chunk in completion:
            if chunk.choices:
                if chunk.choices[0].delta.content is not None and chunk.choices[0].delta.content != "":
                    response.append(chunk.choices[0].delta.content)
            else:
                usage = chunk.usage
        reply = ''.join(response)
        messages.append({"role": "assistant", "content": reply})
        return reply, usage

    @staticmethod
    def mm_completion(client: OpenAI, prompt: str, image: Union[UploadedFile, str], messages: Sequence[dict]):
        image_type = None
        if isinstance(image, str):
            if os.path.exists(image):
                image_type = os.path.splitext(image)[1][-3:]
                with open(image, "rb") as f:
                    base64_image = base64.b64encode(f.read()).decode("utf-8")
        else:
            _, image_type = os.path.splitext(image.name)
            base64_image = base64.b64encode(image.read()).decode("utf-8")
        messages.append({"role": "user", "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_type};base64,{base64_image}"
                },
            },
            {"type": "text", "text": prompt},
        ]})
        completion = client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=messages,
            # 设置输出数据的模态，当前支持["text"]
            modalities=["text"],
            # stream 必须设置为 True，否则会报错
            stream=True,
            stream_options={
                "include_usage": True
            }
        )
        response, usage = [], None
        for chunk in completion:
            if chunk.choices:
                if chunk.choices[0].delta.content is not None and chunk.choices[0].delta.content != "":
                    response.append(chunk.choices[0].delta.content)
            else:
                usage = chunk.usage
        reply = ''.join(response)
        messages.append({"role": "assistant", "content": reply})
        return reply, usage