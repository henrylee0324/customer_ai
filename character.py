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
    # 將清單轉成以階段數字為鍵的字典，方便查找
    stage_dict = {item["階段"]: item for item in data}
    return stage_dict

class Character:
    def __init__(self, character_info: str, llm: LLM, stage_info: dict):
        self.stage = 1
        self.character_info = character_info
        self.llm = llm
        self.stage_info = stage_info  # 包含各階段的資訊字典

    def get_current_stage_description(self) -> str:
        """
        根據 self.stage 回傳對應階段的描述。
        """
        stage = self.stage_info.get(self.stage, {})
        # 取出「階段描述」和「當前客戶狀態描述」
        stage_desc = stage.get("階段描述", "未知階段")
        current_state = stage.get("當前客戶狀態描述", "")
        return f"階段描述：{stage_desc}\n當前狀態：{current_state}"

    def _generate_inner_activity(self, conversation: str) -> str:
        """
        根據角色資料、階段資訊與對話內容生成心理活動（內心獨白）。
        """
        current_stage_desc = self.get_current_stage_description()
        prompt = (
            f"請根據以下角色資料、客戶所處階段資訊以及對話內容，生成角色的內心心理活動：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"客戶階段資訊：\n{current_stage_desc}\n\n"
            f"對話內容：{conversation}\n\n"
            f"請輸出角色內心的獨白。"
        )
        inner_activity = self.llm.generate(prompt)
        print(f"inner_activity: {inner_activity}")
        return inner_activity.strip()

    def generate_response(self, conversation: str) -> str:
        """
        根據心理活動生成角色最終回應。
        """
        inner_activity = self._generate_inner_activity(conversation)
        prompt = (
            f"根據下面的角色心理活動，請生成角色的回應：\n\n"
            f"角色資料：{self.character_info}\n\n"
            f"心理活動：{inner_activity}\n\n"
            f"對話內容: {conversation}\n"
            f"請提供一個符合角色性格的回應。"
        )
        character_response = self.llm.generate(prompt)
        return character_response.strip()

# 測試範例
if __name__ == "__main__":
    # 取得使用者輸入，決定使用哪一個 LLM
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm_instance = choose_llm(llm_choice)

    # 讀取階段資訊 JSON 檔案 (請確保 json 檔案路徑正確)
    stage_info = load_stage_info("stage_info.json")

    # 這裡 character_info 代表角色背景，例如：劍士艾倫；你可以根據實際需求修改
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
    conversation = "你好啊，有什麼能幫忙的嗎?"
    
    character = Character(character_info, llm_instance, stage_info)   
    response_text = character.generate_response(conversation)
    print("\n角色回應：")
    print(response_text)
