from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncIterator, Dict, Any, List, TypedDict
import asyncio
import json
import time
import uvicorn
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import END, StateGraph, START
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
import app.adaptive_rag as AR


load_dotenv()
# 定义状态类型
class State(TypedDict):
    messages: List[HumanMessage | AIMessage]

# 初始化聊天模型
try:
    # 使用OpenAI模型
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        streaming=True
    )
except Exception as e:
    print(f"初始化OpenAI模型失败: {e}")
    # 使用简单的模拟模型作为回退
    class SimpleLLM:
        async def astream(self, messages):
            responses = [
                "让我思考一下您的问题...",
                "这是一个很好的问题。",
                "根据我的分析，我认为...",
                "首先，我们需要考虑几个方面。",
                "其次，还有一些因素也很重要。",
                "最后，我的建议是保持耐心并继续探索。",
                "希望这个回答对您有帮助！"
            ]
            
            for part in responses:
                await asyncio.sleep(0.3)
                yield AIMessage(content=part)
    
    llm = SimpleLLM()

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的AI助手。请用友好、专业的语气回答用户的问题。"),
    MessagesPlaceholder(variable_name="messages"),
])

# 定义聊天节点
async def chat_node(state: State, config: RunnableConfig) -> State:
    # 格式化消息
    formatted_messages = prompt.format_messages(messages=state["messages"])
    
    # 获取AI响应
    ai_response = ""
    async for chunk in llm.astream(formatted_messages):
        if hasattr(chunk, 'content'):
            ai_response += chunk.content
    
    # 返回更新后的状态
    return {"messages": state["messages"] + [AIMessage(content=ai_response)]}

# 构建图
workflow = StateGraph(state_schema=State)

# 添加节点
workflow.add_node("chat", chat_node)

# 设置入口点和边
workflow.add_edge(START, "chat")
workflow.add_edge("chat", END)

# 编译图
app_graph = workflow.compile()

app = FastAPI(title="Chatbox API with LangGraph")

# 添加CORS中间件以允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

async def generate_stream_response(message: str, conversation_id: str = None):
    """生成流式响应"""
    try:
        # 创建初始状态
        human_message = HumanMessage(content=message)
        initial_state = {"messages": [human_message]}
        
        # 使用流式方式执行图
        async for event in app_graph.astream_events(
            initial_state, 
            version="v1",
            stream_mode="values"
        ):
            # 只处理聊天节点的事件
            if event["event"] == "on_chat_model_stream" and "chunk" in event["data"]:
                content = event["data"]["chunk"].content
                if content:
                    data = json.dumps({"content": content})
                    yield f"data: {data}\n\n"
                    await asyncio.sleep(0.05)  # 控制流式输出速度
            
            # 当聊天节点完成时
            elif event["event"] == "on_chain_end" and event["name"] == "chat":
                # 发送结束信号
                yield "data: [DONE]\n\n"
                break
                
    except Exception as e:
        error_data = json.dumps({"error": str(e)})
        yield f"data: {error_data}\n\n"
        yield "data: [DONE]\n\n"

async def generate_stream_response2(message: str, conversation_id: str = None):
    """生成流式响应"""
    try:
        print("-----generate streaming-------", message)
        async for chunk, meta in AR.app.astream({"question": message}, stream_mode="messages"):
            if("tags" in meta and "content" in meta["tags"]):
                data = json.dumps({"content": chunk.content})
                print(chunk.content, end="", flush=True) # chunk 包含了根据 stream_mode 确定的流式输出数据
                yield f"data: {data}\n\n"
            else:
                continue
                
    except Exception as e:
        error_data = json.dumps({"error": str(e)})
        yield f"data: {error_data}\n\n"
        yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天端点"""
    return StreamingResponse(
        generate_stream_response2(request.message, request.conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)