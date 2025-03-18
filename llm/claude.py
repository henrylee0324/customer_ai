import os
import base64
import asyncio
from dotenv import load_dotenv
import anthropic
from llm.llm import LLM

load_dotenv()

class Claude(LLM):      
    def generate(self, prompt="", image_path=None, model_name="claude-3-5-sonnet-20241022"):
        client = anthropic.Client(
            api_key=self.api_key,
        )

        messages = []

        if image_path:
            with open(image_path, "rb") as image_file:
                image = base64.b64encode(image_file.read()).decode("utf-8")
                messages.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image,
                    },
                })
        messages.append({
            "type": "text",
            "text": prompt
        })
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": messages,
                    }
                ]
            )
            extracted_text = "".join(block.text for block in response.content if hasattr(block, "text"))
            return extracted_text
        except Exception as e:
            print(f"Error: {e}")

    async def async_generate(self, prompt="", image_path=None, model_name="claude-3-5-sonnet-20241022"):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, image_path, model_name)

if __name__ == "__main__":
    claude = Claude(os.getenv("ANTHROPIC_API_KEY"))
    prompt = "Say hello"

    # 執行同步請求
    res = claude.generate(prompt=prompt)
    print(f"res: \n{res}")

    # 執行非同步請求
    async def main():
        async_res = await claude.async_generate(prompt=prompt)
        if async_res:
            print(f"async_res:\n {res}")

    asyncio.run(main())
