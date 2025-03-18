import PIL.Image
import time
import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from llm.llm import LLM

class Gemini(LLM):
    def __init__(self, api_key):
        super().__init__(api_key)
        genai.configure(api_key=self.api_key)
        self.last_execution_time = None  # 記錄上次執行時間

    def generate(self, prompt="", image_path=None, model_name="gemini-1.5-pro-002", needwaiting = False):
        current_time = time.time()

        if self.last_execution_time and (current_time - self.last_execution_time < 30) and needwaiting:
            wait_time = 30 - (current_time - self.last_execution_time)
            print(f"Waiting for {wait_time:.2f} seconds to comply with the 30-second rule.")
            time.sleep(wait_time)

        message = [prompt]
        if image_path:
            image = PIL.Image.open(image_path)
            message.append(image)
        else:
            image = None

        model = genai.GenerativeModel(model_name=model_name)
        try:
            response = model.generate_content(message)
            print(f"response: {response.text}")
            # 更新上次執行時間
            self.last_execution_time = time.time()
            return response.text
        except Exception as e:
            print(f"Error: {e}")
    async def async_generate(self, prompt="", image_path=None, model_name="gemini-1.5-pro-002", needwaiting = False):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, image_path, model_name, needwaiting)

    
if __name__ == "__main__":
    load_dotenv()
    gemini = Gemini(os.getenv("GEMINI_API_KEY"))
    prompt = "Say hello"
    res = gemini.generate(prompt=prompt)
    if res:
        print(f"res:\n {res}")
    else:
        print("Failed to generate")    
        # 執行同步請求

    # 執行非同步請求
    async def main():
        async_res = await gemini.async_generate(prompt=prompt, needwaiting = False)
        if async_res:
            print(f"async_res:\n {res}")

    asyncio.run(main())
 
    