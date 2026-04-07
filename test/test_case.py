import sys, os, io, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from agent import graph
from datetime import datetime
from langchain_core.messages import HumanMessage

# Danh sách Test Cases
test_cases = [
    {
        "id": "Test 1",
        "description": "Direct Answer (Không cần tool)",
        "input": "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.",
        "expectation": "Chào hỏi, hỏi thêm thông tin, không gọi tool."
    },
    {
        "id": "Test 2",
        "description": "Single Tool Call",
        "input": "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng",
        "expectation": "Gọi search_flights, liệt kê 4 chuyến bay."
    },
    {
        "id": "Test 3",
        "description": "Multi-Step Tool Chaining",
        "input": "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!",
        "expectation": "Chuỗi: Flight -> Budget -> Hotel -> Tổng hợp."
    },
    {
        "id": "Test 4",
        "description": "Clarification",
        "input": "Tôi muốn đặt khách sạn",
        "expectation": "Hỏi lại thông tin thiếu, chưa gọi tool ngay."
    },
    {
        "id": "Test 5",
        "description": "Guardrail / Refusal",
        "input": "Giải giúp tôi bài tập lập trình Python về linked list",
        "expectation": "Từ chối lịch sự, chỉ hỗ trợ du lịch."
    },
    # --- FEATURE TESTS (bổ sung) ---
    {
        "id": "Test 6",
        "description": "Weekend Pricing (+20%)",
        "input": "Tìm vé từ Hà Nội đi Đà Nẵng vào thứ 7",
        "expectation": "Gọi search_flights với travel_date='thứ 7', giá vé tăng 20% so với ngày thường (VD: VietJet 890k → 1,068,000₫)."
    },
    {
        "id": "Test 7",
        "description": "Time Preference (không cần ngày)",
        "input": "Tìm vé buổi sáng từ Hà Nội đi Đà Nẵng",
        "expectation": "Gọi search_flights, chỉ liệt kê/ưu tiên các chuyến trước 12:00 (06:00, 08:30, 11:00), chọn rẻ nhất là VietJet 08:30."
    },
    {
        "id": "Test 8",
        "description": "Business Class Filter",
        "input": "Tìm vé hạng thương gia từ Hà Nội đi Hồ Chí Minh",
        "expectation": "Gọi search_flights với flight_class='business', chỉ trả về đúng 1 chuyến Vietnam Airlines 18:00 giá 3,200,000₫."
    },
    {
        "id": "Test 9",
        "description": "Dead-end Detection (budget quá thấp)",
        "input": "Tôi ở Hà Nội muốn đi Phú Quốc 3 đêm, budget 1.5 triệu. Tư vấn giúp!",
        "expectation": "Gọi search_flights, phát hiện không có vé khả thi (rẻ nhất 1.1M + 3×200k = 1.7M > 1.5M), thông báo ngân sách tối thiểu cần thiết và DỪNG, không gọi search_hotels."
    },
    {
        "id": "Test 10",
        "description": "Full Plan + Time Preference kết hợp",
        "input": "Tôi ở Hà Nội muốn đi Đà Nẵng 2 đêm, budget 4 triệu, muốn đi chuyến buổi sáng",
        "expectation": "Chuỗi đầy đủ: search_flights (lọc sáng, chọn VietJet 08:30 890k) -> calculate_budget -> search_hotels -> calculate_budget tổng hợp."
    }
]


def determine_status(test_id, tools_called):
    no_tool_tests = ["Test 1", "Test 4", "Test 5"]
    if test_id in no_tool_tests:
        return "PASS" if len(tools_called) == 0 else "REVIEW"
    elif test_id == "Test 9":
        return "PASS" if "search_flights" in tools_called and "search_hotels" not in tools_called else "REVIEW"
    else:
        return "PASS" if len(tools_called) > 0 else "REVIEW"


def run_automated_tests():
    all_results = []
    md_sections = []

    print("=" * 60)
    print("BẮT ĐẦU CHẠY KIỂM THỬ TỰ ĐỘNG")

    for test in test_cases:
        print(f"\n⚡ Đang chạy {test['id']}...")

        # Capture stdout ([Agent] print lines) trong lúc invoke
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        start_time = datetime.now()
        result = graph.invoke({"messages": [HumanMessage(content=test['input'])]})

        sys.stdout = old_stdout
        agent_log_lines = captured.getvalue().strip().splitlines()

        # In lại ra console để theo dõi
        for line in agent_log_lines:
            print(line)

        tools_called = [
            m.tool_calls[0]['name']
            for m in result['messages']
            if hasattr(m, 'tool_calls') and m.tool_calls
        ]
        final_answer = result["messages"][-1].content
        status = determine_status(test["id"], tools_called)
        status_icon = "✅ PASS" if status == "PASS" else "⚠️ REVIEW"

        # --- Ghi kết quả JSON ---
        all_results.append({
            "id": test["id"],
            "input": test["input"],
            "expectation": test["expectation"],
            "agent_response": final_answer,
            "tools_used": tools_called,
            "status": status,
            "timestamp": start_time.isoformat()
        })

        # --- Xây dựng phần Markdown cho test này ---
        tools_display = ", ".join(f"`{t}`" for t in tools_called) if tools_called else "_(không gọi tool)_"

        # Dựng console log block: ghép input + agent lines + response
        console_log = f"Bạn: {test['input']}\n\nTravelBuddy đang suy nghĩ...\n"
        console_log += "\n".join(agent_log_lines)
        console_log += f"\n\nTravelBuddy: {final_answer}"

        md_sections.append(f"""## {test['id']} — {test['description']}

**Expectation:** {test['expectation']}

**Tools used:** {tools_display}

**Status:** {status_icon}

**Console Log:**

```
{console_log}
```

---
""")

    # --- Ghi JSON ---
    with open("test_logs.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    # --- Ghi Markdown ---
    pass_count = sum(1 for r in all_results if r["status"] == "PASS")
    total = len(all_results)
    md_header = f"""# TravelBuddy — Kết Quả Kiểm Thử

**Ngày chạy:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tổng số test:** {total} | **PASS:** {pass_count} | **REVIEW:** {total - pass_count}

---

"""
    md_path = os.path.join(os.path.dirname(__file__), '..', 'test_results.md')
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_header + "\n".join(md_sections))

    print("\n" + "=" * 60)
    print(f"✅ Đã hoàn thành {total} Test Cases. PASS: {pass_count}/{total}")
    print(f"📂 JSON: test_logs.json")
    print(f"📄 Markdown: test_results.md")
    print("=" * 60)


if __name__ == "__main__":
    run_automated_tests()
