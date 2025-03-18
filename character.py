from dotenv import load_dotenv
import os
from llm.llm import LLM
from llm.openaigpt import OpenAIGPT
from llm.claude import Claude
from llm.gemini import Gemini


load_dotenv()

def choose_llm(llm_name: str) -> LLM:
    """
    根據傳入的 llm_name 返回對應的 LLM 實例。
    """
    if llm_name.lower() == "openai":
        return OpenAIGPT(os.getenv("OPENAI_API_KEY"))
    elif llm_name.lower() == "claude":
        return Claude(os.getenv("ANTHROPIC_API_KEY"))
    elif llm_name.lower() == "gemini":
        return Gemini(os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError(f"未知的 LLM: {llm_name}")

class Character:
    def __init__(self, character_info: str, llm: LLM):
        self.character_info = character_info
        self.llm = llm

    def generate_inner_activity(self, conversation: str) -> str:
        """
        根據角色資料和對話內容生成心理活動（內心獨白）。
        """
        prompt = (
            f"請根據以下角色資料和對話內容，生成角色的內心心理活動：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"對話內容：{conversation}\n\n"
            f"請輸出角色內心的獨白。"
        )
        inner_activity = self.llm.generate(prompt)
        return inner_activity.strip()

    def generate_response(self, inner_activity: str) -> str:
        """
        根據心理活動生成角色最終回應。
        """
        prompt = (
            f"根據下面的角色心理活動，請生成角色的回應：\n\n"
            f"心理活動：{inner_activity}\n\n"
            f"請提供一個符合角色性格的回應。"
        )
        character_response = self.llm.generate(prompt)
        return character_response.strip()

# 測試範例
if __name__ == "__main__":
    # 取得使用者輸入，決定使用哪一個 LLM
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm_instance = choose_llm(llm_choice)

    character_info = "角色：劍士艾倫，性格剛毅、沉著；背景：曾是戰場上的英雄，現隱居山林，心中隱藏著深深的悲傷。"
    conversation = "玩家：艾倫，你最近看起來心事重重，是發生什麼事了？"
    
    character = Character(character_info, llm_instance)
    inner_activity = character.generate_inner_activity(conversation)
    print("心理活動：")
    print(inner_activity)
    
    # 根據心理活動生成角色回應
    response_text = character.generate_response(inner_activity)
    print("\n角色回應：")
    print(response_text)
