from llm.llm import LLM

class Judge:
    """
    Judge 角色會根據對話內容以及階段資訊來判斷是否完成該階段，
    並決定是否可以進入下一個階段。
    """
    def __init__(self, llm: LLM):
        self.llm = llm

    def evaluate_stage(self, conversation: str, inner_activity: str, stage_description: str) -> bool:
        """
        同步方式利用 LLM 來評估是否完成階段。
        傳入參數：
          - conversation: 一組對話內容
          - inner_activity: 內部活動或系統紀錄的訊息
          - stage_description: 當前階段的描述文字
        回傳值：
          - True 表示該階段已完成，可進入下一階段；False 表示仍需進行。
        """
        prompt = (
            "請根據以下資訊判斷目前階段是否已完成：\n"
            f"【對話】：\n{conversation}\n\n"
            f"【角色心理活動】：\n{inner_activity}\n\n"
            f"【階段描述】：\n{stage_description}\n\n"
            "請回答「是」或「否」，其中「是」代表階段已完成；「否」代表階段尚未完成。"
        )
        result = self.llm.generate(prompt)
        if "是" in result or "完成" in result:
            return True
        return False

    async def async_evaluate_stage(self, conversation: str, inner_activity: str, stage_description: str) -> bool:
        """
        非同步方式利用 LLM 來評估是否完成階段。
        傳入參數：
          - conversation: 一組對話內容
          - inner_activity: 內部活動或系統紀錄的訊息
          - stage_description: 當前階段的描述文字
        回傳值：
          - True 表示該階段已完成，可進入下一階段；False 表示仍需進行。
        """
        prompt = (
            "請根據以下資訊判斷目前階段是否已完成：\n\n"
            f"【對話】：\n{conversation}\n"
            f"【角色心理活動】：\n{inner_activity}\n\n"
            f"【階段描述】：\n{stage_description}\n\n"
            "請回答「是」或「否」，其中「是」代表階段已完成；「否」代表階段尚未完成。"
        )
        result = await self.llm.async_generate(prompt)
        if "是" in result or "完成" in result:
            return True
        return False
