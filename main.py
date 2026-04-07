import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent import graph
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy — Trợ lý Du lịch Thông minh")
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
