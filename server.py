import json
import random
import os
import uuid
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles
import uvicorn
from collections import deque

# 匯入你原本的模組
from character import Character
from llm.llm import LLM
from llm.openaigpt import OpenAIGPT
from llm.claude import Claude
from llm.gemini import Gemini
from judge import Judge

# 讀取環境變數
load_dotenv()

app = FastAPI(title="Character Chat API")

# 用來儲存會話資料（僅供示範，非生產環境用）
sessions = {}

origins = [
    "http://localhost:9000",
    # 如有需要，也可以加入其他來源
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 輔助函式：非同步載入隨機角色資料
async def load_random_character_async(json_file: str) -> dict:
    async with aiofiles.open(json_file, mode='r', encoding='utf-8') as file:
        content = await file.read()
        customers = json.loads(content)
    return random.choice(customers)

# 輔助函式：非同步載入階段資訊並建立以階段為鍵的字典
async def load_stage_info_async(json_path: str) -> dict:
    async with aiofiles.open(json_path, mode="r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)
    stage_dict = {item["階段"]: item for item in data}
    return stage_dict

# 根據 llm_choice 建立 LLM 實例
def choose_llm(llm_name: str) -> LLM:
    if llm_name.lower() == "openai":
        return OpenAIGPT(os.getenv("OPENAI_API_KEY"))
    elif llm_name.lower() == "claude":
        return Claude(os.getenv("ANTHROPIC_API_KEY"))
    elif llm_name.lower() == "gemini":
        return Gemini(os.getenv("GEMINI_API_KEY"))
    else:
        raise ValueError(f"未知的 LLM: {llm_name}")

# Pydantic 模型定義
class StartSessionRequest(BaseModel):
    llm_choice: str

class StartSessionResponse(BaseModel):
    session_id: str
    character_info: dict
    current_stage: int
    stage_description: str

class ChatRequest(BaseModel):
    session_id: str
    user_input: str

class ChatResponse(BaseModel):
    response_text: str
    inner_activity: str
    conversation: str
    current_stage: int
    stage_description: str
    is_pass: bool
    finished: bool

class EndSessionRequest(BaseModel):
    session_id: str

# 建立 /start 端點，用於初始化會話
@app.post("/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    try:
        # 非同步載入角色資料與階段資訊
        character_data = await load_random_character_async('persona.json')
        # 將角色資料格式化成字串（依原程式）
        character_info_str = json.dumps(character_data, indent=2, ensure_ascii=False)
        stage_info = await load_stage_info_async("stage_info.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案載入錯誤: {str(e)}")

    try:
        llm = choose_llm(request.llm_choice)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    # 建立 Character 與 Judge 物件（假設這些類別皆有非同步方法）
    character = Character(character_info_str, llm, stage_info)
    judge = Judge(llm)
    
    # 初始對話歷史使用 deque（保留最近 3 則訊息），初始階段為 1
    conversation_history = deque(maxlen=3)
    stage = 1
    # 儲存會話資料到 sessions 字典
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "character": character,
        "judge": judge,
        "conversation_history": conversation_history,
        "stage": stage,
        "stage_info": stage_info,
    }
    
    # 取得初始階段描述
    stage_description = character.get_current_stage_description() if hasattr(character, "get_current_stage_description") else ""
    
    return StartSessionResponse(
        session_id=session_id,
        character_info=character_data,
        current_stage=stage,
        stage_description=stage_description
    )

# 建立 /chat 端點，用於持續對話
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    character: Character = session["character"]
    judge: Judge = session["judge"]
    conversation_history: deque = session["conversation_history"]
    stage: int = session["stage"]
    stage_info = session["stage_info"]
    
    # 將使用者訊息加入對話歷史
    conversation_history.append(f"使用者: {request.user_input}")
    
    # 將對話歷史合併為單一字串，用於生成回應
    conversation = "\n".join(conversation_history)
    
    # 產生角色回應（呼叫非同步方法）
    try:
        response_text, inner_activity = await character.async_generate_response(conversation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成回應時發生錯誤: {str(e)}")
    
    # 將角色回應加入對話歷史
    conversation_history.append(f"角色: {response_text}")
    
    # 取得目前階段描述（同步呼叫）
    stage_description = character.get_current_stage_description() if hasattr(character, "get_current_stage_description") else ""
    
    # 評估是否通過當前階段，傳入對話歷史（以字串形式）
    try:
        is_pass = await judge.async_evaluate_stage("\n".join(conversation_history), inner_activity, stage_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"階段評估時發生錯誤: {str(e)}")
    
    # 如果通過則進入下一階段
    if is_pass:
        stage += 1
        character.stage = stage  # 假設 Character 物件有 stage 屬性
    
    # 更新 session 中的對話歷史與階段
    session["stage"] = stage
    
    finished = False
    # 若階段超過階段資訊數量則對話結束
    if stage > len(stage_info):
        finished = True
    
    return ChatResponse(
        response_text=response_text,
        inner_activity=inner_activity,
        conversation="\n".join(conversation_history),
        current_stage=stage,
        stage_description=stage_description,
        is_pass=is_pass,
        finished=finished
    )

@app.post("/end")
async def end_session(request: EndSessionRequest):
    if request.session_id in sessions:
        del sessions[request.session_id]
        return {"detail": "Session ended successfully."}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    uvicorn.run("server:app", reload=True, host="localhost", port=8000)
