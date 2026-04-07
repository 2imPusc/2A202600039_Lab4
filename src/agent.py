import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from tools import search_flights, search_hotels, calculate_budget

load_dotenv()

# 1. Định nghĩa trạng thái của Agent (State)
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # Temperature=0 để Agent hoạt động chính xác, ít sáng tạo linh tinh
llm_with_tools = llm.bind_tools(tools_list)

# 3. Đọc System Prompt
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "system_prompt.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 4. Định nghĩa Agent Node (Nút xử lý chính)
def agent_node(state: AgentState):
    messages = state["messages"]
    
    # Nếu là tin nhắn đầu tiên, chèn System Prompt vào đầu danh sách
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    
    #=== LOGGING ===
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"[Agent] Gọi tool: {tc['name']}({tc['args']})")
    else:
        print("[Agent] Trả lời trực tiếp cho khách hàng.")
        
    return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)

# Thêm các nút vào đồ thị
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools_list))

# Thiết lập các luồng di chuyển (Edges)
builder.add_edge(START, "agent")

# Kiểm tra điều kiện sau khi Agent xử lý
# Nếu Agent gọi tool -> chuyển sang nút "tools"
# Nếu Agent trả lời xong -> kết thúc (END)
builder.add_conditional_edges("agent", tools_condition)

# Sau khi dùng Tool xong, phải quay lại nút Agent để "não bộ" xử lý kết quả từ tool
builder.add_edge("tools", "agent")

# Biên dịch đồ thị thành ứng dụng hoàn chỉnh
graph = builder.compile()

# 6. Chat Loop
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy: Trợ lý Du lịch Thông minh sẵn sàng!")
    print("Gõ 'quit', 'exit' hoặc 'q' để thoát.")
    print("=" * 60)
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
            
        print("\nTravelBuddy đang suy nghĩ...")
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        final_message = result["messages"][-1]
        print(f"\nTravelBuddy: {final_message.content}")