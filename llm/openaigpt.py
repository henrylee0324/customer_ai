import openai
import asyncio
import os
from dotenv import load_dotenv
from llm.llm import LLM

load_dotenv()

class OpenAIGPT(LLM):
    def __init__(self, api_key):
        super().__init__(api_key)
        openai.api_key = api_key
        self.client = openai  # 直接使用 openai 模組

    def generate(self, prompt="", image_path=None, model_name="gpt-4o"):
        response = self.client.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content

    async def async_generate(self, prompt="", image_path=None, model_name="gpt-4o"):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, image_path, model_name)

if __name__ == "__main__":
    openaigpt = OpenAIGPT(os.getenv("OPENAI_API_KEY"))
    prompt = "Say hello"

    res = openaigpt.generate(prompt=prompt)
    print(f"res: \n{res}")

    async def main():
        async_res = await openaigpt.async_generate(prompt=prompt)
        if async_res:
            print(f"async_res:\n {async_res}")

    asyncio.run(main())
