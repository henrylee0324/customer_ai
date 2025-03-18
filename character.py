from dotenv import load_dotenv
import os
import json
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
    讀取 JSON 檔案並建立以階段為鍵的字典。
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
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
            history_text += f"回合 {idx}：\n問題：{turn.get('question', '')}\n心理活動：{turn.get('inner_activity', '')}\n回應：{turn.get('response', '')}\n\n"
        return history_text.strip()

    def _generate_inner_activity(self, question: str, history_text: str) -> str:
        """
        根據角色資料、階段資訊、對話歷史與當前問題生成心理活動（內心獨白）。
        """
        current_stage_desc = self.get_current_stage_description()
        #nils
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

    def generate_response(self, question: str) -> str:
        """
        根據當前問題生成角色的回應，同時將問題、心理活動與回應存入 conversation_history 中。
        """
        # 先取得目前的對話歷史文字
        history_text = self.format_history()
        # 生成心理活動
        inner_activity = self._generate_inner_activity(question, history_text)
        # 再次取得格式化後的對話歷史（此時不包含本回合的內容）
        history_text = self.format_history()
        #nils
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
        # 將本回合的資料存入 conversation_history
        self.conversation_history.append({
            "question": question,
            "inner_activity": inner_activity,
            "response": response
        })
        return response, inner_activity

if __name__ == "__main__":
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
    # 範例對話回合
    question = "你好啊，我是保險業務員小陳，有什麼能幫忙的嗎?"
    character = Character(character_info, llm_instance, stage_info)   
    response_text = character.generate_response(question)
    print("\n角色回應：")
    print(response_text)
