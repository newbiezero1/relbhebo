from openai import OpenAI

import config


class ChatGPT:
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = "gpt-4-vision-preview"
        self.promt = 'Look to image and find stop loss he is red. Let response in format SL: (stop loss)'

    def get_sl_from_img(self, url: str) -> str:
        """ask to gpt for help find sl in picture"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.promt},
                        {
                            "type": "image_url",
                            "image_url": url,
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        text = response.choices[0].message.content.split('SL: ')
        if text[1]:
            return text[1].strip()
        return ''
