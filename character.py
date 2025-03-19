import os
import json
import asyncio
import aiofiles
from dotenv import load_dotenv
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

def load_stage_info(json_path: str) -> dict:
    """
    同步讀取 JSON 檔案並建立以階段為鍵的字典。
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    stage_dict = {item["階段"]: item for item in data}
    return stage_dict

async def async_load_stage_info(json_path: str) -> dict:
    """
    非同步讀取 JSON 檔案並建立以階段為鍵的字典。
    """
    async with aiofiles.open(json_path, mode="r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)
    stage_dict = {item["階段"]: item for item in data}
    return stage_dict

class Character:
    def __init__(self, character_info: str, llm: LLM, stage_info: dict):
        self.stage = 1
        self.character_info = character_info
        self.llm = llm
        self.stage_info = stage_info  # 包含各階段的資訊字典
        # 將 conversation_history 改為儲存每回合的字典，包含「問題」、「心理活動」與「回應」
        self.conversation_history = []

    def get_current_stage_description(self) -> str:
        """
        根據 self.stage 回傳對應階段的描述。
        """
        stage = self.stage_info.get(self.stage, {})
        return f"{stage}"

    def format_history(self) -> str:
        """
        將 conversation_history 格式化成文字，供 prompt 使用。
        """
        history_text = ""
        for idx, turn in enumerate(self.conversation_history, start=1):
            history_text += (
                f"回合 {idx}：\n"
                f"問題：{turn.get('question', '')}\n"
                f"心理活動：{turn.get('inner_activity', '')}\n"
                f"回應：{turn.get('response', '')}\n\n"
            )
        return history_text.strip()

    def _generate_inner_activity(self, question: str, history_text: str) -> str:
        """
        同步生成角色內心獨白。
        """
        current_stage_desc = self.get_current_stage_description()
        prompt = (
            f"請根據以下角色資料、客戶所處階段資訊以及完整對話歷史，生成角色的內心心理活動：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"客戶階段資訊：\n{current_stage_desc}\n\n"
            f"對話歷史：\n{history_text}\n\n"
            f"當前問題：{question}\n\n"
            f"請輸出角色內心的獨白。"
        )
        inner_activity = self.llm.generate(prompt)
        return inner_activity.strip()

    async def _async_generate_inner_activity(self, question: str, history_text: str) -> str:
        """
        非同步生成角色內心獨白。
        """
        current_stage_desc = self.get_current_stage_description()
        prompt = (
            f"請根據以下角色資料、客戶所處階段資訊以及完整對話歷史，生成角色的內心心理活動：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"客戶階段資訊：\n{current_stage_desc}\n\n"
            f"對話歷史：\n{history_text}\n\n"
            f"當前問題：{question}\n\n"
            f"請輸出角色內心的獨白。"
        )
        # 假設 llm 提供非同步生成方法 async_generate
        inner_activity = await self.llm.async_generate(prompt)
        return inner_activity.strip()

    # 同步生成回應
    def generate_response(self, question: str) -> tuple:
        """
        同步生成角色回應，同時記錄問題、心理活動與回應。
        """
        history_text = self.format_history()
        inner_activity = self._generate_inner_activity(question, history_text)
        history_text = self.format_history()  # 再次取得對話歷史（不含本回合）
        prompt = (
            f"根據下面的角色心理活動，請生成角色的回應：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"心理活動：{inner_activity}\n\n"
            f"完整對話歷史：\n{history_text}\n\n"
            f"當前問題：{question}\n"
            f"請提供一個符合角色性格的回應。"
            f"請不要給予角色說的話以外的任何內容。"
        )
        response = self.llm.generate(prompt).strip()
        self.conversation_history.append({
            "question": question,
            "inner_activity": inner_activity,
            "response": response
        })
        return response, inner_activity

    # 非同步生成回應
    async def async_generate_response(self, question: str) -> tuple:
        """
        非同步生成角色回應，同時記錄問題、心理活動與回應。
        """
        history_text = self.format_history()
        inner_activity = await self._async_generate_inner_activity(question, history_text)
        history_text = self.format_history()  
        prompt = (
            f"根據下面的角色心理活動，請生成角色的回應：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"心理活動：{inner_activity}\n\n"
            f"完整對話歷史：\n{history_text}\n\n"
            f"當前問題：{question}\n"
            f"請提供一個符合角色性格的回應。"
            f"請不要給予角色說的話以外的任何內容。"
        )
        response = (await self.llm.async_generate(prompt)).strip()
        self.conversation_history.append({
            "question": question,
            "inner_activity": inner_activity,
            "response": response
        })
        return response, inner_activity

def main_sync():
    """
    同步主程式
    """
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm_instance = choose_llm(llm_choice)
    stage_info = load_stage_info("stage_info.json")
    character_info = """
    {
      "客戶編號": 1,
      "年齡": 51,
      "性別": "男",
      "婚姻狀況": "已婚",
      "教育程度": "大學",
      "收入": "中等",
      "職業類型": "服務/小型企業",
      "有壽險": true,
      "保險興趣": [
        "退休金",
        "健康保險/重大疾病",
        "子女教育",
        "壽險/儲蓄"
      ],
      "家庭結構": {
        "家庭人數": 5
      },
      "風險態度": "風險規避",
      "偏好管道": "線下",
      "銷售接受度": "高度接受",
      "MBTI": "INTJ"
    }
    """
    question = "你好啊，我是保險業務員小陳，有什麼能幫忙的嗎?"
    character = Character(character_info, llm_instance, stage_info)
    response, inner_activity = character.generate_response_sync(question)
    print("\n同步角色回應：")
    print(response)

async def main_async():
    """
    非同步主程式
    """
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm_instance = choose_llm(llm_choice)
    stage_info = await async_load_stage_info("stage_info.json")
    character_info = """
    {
      "客戶編號": 1,
      "年齡": 51,
      "性別": "男",
      "婚姻狀況": "已婚",
      "教育程度": "大學",
      "收入": "中等",
      "職業類型": "服務/小型企業",
      "有壽險": true,
      "保險興趣": [
        "退休金",
        "健康保險/重大疾病",
        "子女教育",
        "壽險/儲蓄"
      ],
      "家庭結構": {
        "家庭人數": 5
      },
      "風險態度": "風險規避",
      "偏好管道": "線下",
      "銷售接受度": "高度接受",
      "MBTI": "INTJ"
    }
    """
    question = "你好啊，我是保險業務員小陳，有什麼能幫忙的嗎?"
    character = Character(character_info, llm_instance, stage_info)
    response, inner_activity = await character.async_generate_response(question)
    print("\n非同步角色回應：")
    print(response)

if __name__ == "__main__":
    mode = input("請選擇模式 (sync/async): ").strip().lower()
    if mode == "sync":
        main_sync()
    elif mode == "async":
        asyncio.run(main_async())
    else:
        print("未知模式")
