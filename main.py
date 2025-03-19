import json
import random
import os
import asyncio
from dotenv import load_dotenv
from character import Character
from llm.llm import LLM
from llm.openaigpt import OpenAIGPT
from llm.claude import Claude
from llm.gemini import Gemini
from judge import Judge
from colorama import init, Fore, Style
import aiofiles

# 初始化 colorama (在 Windows 上會有更好的相容性)
init(autoreset=True)

def load_random_character(json_file: str) -> dict:
    """
    同步讀取 JSON 檔案並隨機選取一位角色資料
    """
    with open(json_file, 'r', encoding='utf-8') as file:
        customers = json.load(file)
    return random.choice(customers)

async def load_random_character_async(json_file: str) -> dict:
    """
    非同步讀取 JSON 檔案並隨機選取一位角色資料
    """
    async with aiofiles.open(json_file, mode='r', encoding='utf-8') as file:
        content = await file.read()
        customers = json.loads(content)
    return random.choice(customers)

def load_stage_info(json_path: str) -> dict:
    """
    同步讀取 JSON 檔案並建立以階段為鍵的字典
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    stage_dict = {item["階段"]: item for item in data}
    return stage_dict

async def load_stage_info_async(json_path: str) -> dict:
    """
    非同步讀取 JSON 檔案並建立以階段為鍵的字典
    """
    async with aiofiles.open(json_path, mode="r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)
    stage_dict = {item["階段"]: item for item in data}
    return stage_dict

def choose_llm(llm_name: str) -> LLM:
    """
    根據傳入的 llm_name 返回對應的 LLM 實例
    """
    if llm_name.lower() == "openai":
        return OpenAIGPT(os.getenv("OPENAI_API_KEY"))
    elif llm_name.lower() == "claude":
        return Claude(os.getenv("ANTHROPIC_API_KEY"))
    elif llm_name.lower() == "gemini":
        return Gemini(os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError(f"未知的 LLM: {llm_name}")

def main_sync():
    """
    同步主程式
    """
    # 載入環境變數（如果需要）
    load_dotenv()
    
    # 載入角色與階段資訊
    character_data = load_random_character('persona.json')
    character_info_str = json.dumps(character_data, indent=2, ensure_ascii=False)
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm = choose_llm(llm_choice)
    stage_info = load_stage_info("stage_info.json")
    character = Character(character_info_str, llm, stage_info)
    judge = Judge(llm)
    
    print(f"{Fore.GREEN}客戶資訊: \n{character_info_str}")
    print(f"{Fore.YELLOW}開始對話 (輸入 'quit', 'exit' 或 'q' 可結束對話)：")
    
    conversation = ""  # 儲存累積對話內容
    while True:
        user_input = input(f"\n{Fore.BLUE}使用者: {Style.RESET_ALL}")
        if user_input.lower() in ("quit", "exit", "q"):
            print(f"{Fore.RED}對話結束。{Style.RESET_ALL}")
            break

        # 將使用者輸入加入對話內容中
        conversation += f"\n使用者: {user_input}"
        
        # 生成角色回應（同步版）
        response_text, inner_activity = character.generate_response(conversation)
        print(f"{Fore.RED}inner_activity: \n{inner_activity}\n{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}角色回應： \n{response_text}\n{Style.RESET_ALL}")
        
        # 取得當前階段描述並評估是否通過
        stage_description = character.get_current_stage_description()
        print(f"stage: {stage_description}")
        ispass = judge.evaluate_stage(user_input, response_text, inner_activity, stage_description)
        print(f"{Fore.YELLOW}ispass: {ispass}{Style.RESET_ALL}")
        if ispass:
            character.stage += 1
        if character.stage > len(stage_info):
            print(f"{Fore.MAGENTA}恭喜通關!對話結束。{Style.RESET_ALL}")
            break

async def main_async():
    """
    非同步主程式
    """
    load_dotenv()
    
    # 載入角色與階段資訊 (非同步版)
    character_data = await load_random_character_async('persona.json')
    character_info_str = json.dumps(character_data, indent=2, ensure_ascii=False)
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm = choose_llm(llm_choice)
    stage_info = await load_stage_info_async("stage_info.json")
    # 假設 Character 與 Judge 分別有非同步版本的方法，如 generate_response_async 與 evaluate_stage_async
    character = Character(character_info_str, llm, stage_info)
    judge = Judge(llm)
    
    print(f"{Fore.GREEN}客戶資訊: \n{character_info_str}")
    print(f"{Fore.YELLOW}開始對話 (輸入 'quit', 'exit' 或 'q' 可結束對話)：")
    
    conversation = ""  # 儲存累積對話內容
    while True:
        user_input = input(f"\n{Fore.BLUE}使用者: {Style.RESET_ALL}")
        if user_input.lower() in ("quit", "exit", "q"):
            print(f"{Fore.RED}對話結束。{Style.RESET_ALL}")
            break

        conversation += f"\n使用者: {user_input}"
        
        # 生成角色回應 (非同步版)
        response_text, inner_activity = await character.async_generate_response(conversation)
        print(f"{Fore.RED}inner_activity: \n{inner_activity}\n{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}角色回應： \n{response_text}\n{Style.RESET_ALL}")
        
        stage_description = character.get_current_stage_description()
        print(f"stage: {stage_description}")
        ispass = await judge.async_evaluate_stage(user_input, response_text, inner_activity, stage_description)
        print(f"{Fore.YELLOW}ispass: {ispass}{Style.RESET_ALL}")
        if ispass:
            character.stage += 1
        if character.stage > len(stage_info):
            print(f"{Fore.MAGENTA}恭喜通關!對話結束。{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    mode = input("請選擇模式 (sync/async): ").strip().lower()
    if mode == "sync":
        main_sync()
    elif mode == "async":
        asyncio.run(main_async())
    else:
        print("未知模式")
