import json
import random
import os
from dotenv import load_dotenv
from character import Character
from llm.llm import LLM
from llm.openaigpt import OpenAIGPT
from llm.claude import Claude
from llm.gemini import Gemini

def load_random_character(json_file: str) -> dict:
    with open(json_file, 'r', encoding='utf-8') as file:
        customers = json.load(file)
    return random.choice(customers)

def choose_llm(llm_name: str) -> LLM:
    if llm_name.lower() == "openai":
        return OpenAIGPT(os.getenv("OPENAI_API_KEY"))
    elif llm_name.lower() == "claude":
        return Claude(os.getenv("ANTHROPIC_API_KEY"))
    elif llm_name.lower() == "gemini":
        return Gemini(os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError(f"未知的 LLM: {llm_name}")



def main():
    character_data = load_random_character('persona.json')
    character_info_str = json.dumps(character_data, indent=2, ensure_ascii=False)
    llm_choice = input("請選擇 LLM (openai, claude, gemini): ").strip()
    llm = choose_llm(llm_choice)
    character = Character(character_info_str, llm)
    conversation = "你好，今天的天氣真不錯，你覺得呢？"
    inner_activity = character.generate_inner_activity(conversation)
    print("角色內心獨白：")
    print(inner_activity)
    response = character.generate_response(inner_activity)
    print("\n角色回應：")
    print(response)

if __name__ == "__main__":
    main()
