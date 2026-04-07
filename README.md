# TravelBuddy — Trợ Lý Du Lịch Thông Minh

> Lab 4 — AI Agent with LangGraph | Student ID: 2A202600039

TravelBuddy là một AI Agent tư vấn du lịch nội địa Việt Nam, được xây dựng trên nền tảng **LangGraph** (ReAct pattern) và **GPT-4o-mini**, có khả năng tìm kiếm vé máy bay, khách sạn và lập kế hoạch ngân sách theo yêu cầu người dùng.

---

## Kiến Trúc Graph

TravelBuddy sử dụng vòng lặp **ReAct (Reason + Act)** của LangGraph:

```
START
  │
  ▼
┌─────────────┐
│  agent_node │  ← LLM (GPT-4o-mini) + System Prompt
└──────┬──────┘
       │
       ▼ tools_condition
  ┌────┴────┐
  │         │
  │ tool?   │ no → END
  │ yes     │
  └────┬────┘
       │
       ▼
┌─────────────┐
│  ToolNode   │  ← search_flights / search_hotels / calculate_budget
└──────┬──────┘
       │
       └──────────────► (quay lại agent_node)
```

**Luồng xử lý:**
1. `START` → `agent_node`: LLM đọc System Prompt + tin nhắn người dùng, quyết định gọi tool hay trả lời thẳng.
2. `tools_condition`: nếu LLM phát sinh `tool_calls` → chuyển sang `ToolNode`; ngược lại → `END`.
3. `ToolNode` thực thi tool, kết quả được append vào `messages`.
4. Quay lại `agent_node` để LLM tổng hợp kết quả — lặp cho đến khi không còn tool call.

**State:**
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # tích lũy toàn bộ lịch sử hội thoại
```

---

## Công Cụ (Tools)

| Tool | Tham số | Chức năng |
|---|---|---|
| `search_flights` | `origin`, `destination`, `travel_date`, `flight_class` | Tìm vé giữa 2 thành phố. Hỗ trợ lọc theo hạng vé và phụ phí cuối tuần +20%. |
| `search_hotels` | `city`, `max_price_per_night` | Tìm khách sạn theo thành phố và giá tối đa mỗi đêm. |
| `calculate_budget` | `total_budget`, `expenses` | Tính ngân sách còn lại và xuất bảng chi phí chi tiết. |

---

## Tính Năng

### Tính năng gốc (Lab assignment)
| # | Tính năng | Mô tả |
|---|---|---|
| 1 | **Multi-step Tool Chaining** | Chuỗi 4 bước: `search_flights` → `calculate_budget` → `search_hotels` → `calculate_budget` |
| 2 | **Clarification** | Hỏi lại khi thiếu thông tin cần thiết (thành phố, ngân sách, số đêm) |
| 3 | **Guardrail** | Từ chối lịch sự các câu hỏi ngoài lĩnh vực du lịch |
| 4 | **Budget Calculation** | Bắt buộc dùng tool `calculate_budget`, không tự tính |

### Tính năng bổ sung
| # | Tính năng | Mô tả |
|---|---|---|
| 5 | **Weekend Pricing** | Giá vé tự động tăng 20% vào thứ 7, chủ nhật. Nhận diện từ từ khóa tự nhiên ("thứ 7", "cuối tuần") hoặc ngày ISO (2026-04-12). |
| 6 | **Time Preference** | Lọc chuyến bay theo buổi: sáng (trước 12:00), chiều (12:00–17:59), tối (sau 18:00). Hoạt động độc lập, không cần ngày đi. |
| 7 | **Flight Class Filter** | Tham số `flight_class` trong `search_flights` — lọc cứng economy/business tại tầng tool thay vì phụ thuộc LLM. |
| 8 | **Smart Flight Selection** | Chọn vé theo thứ tự ưu tiên: (1) lọc theo buổi, (2) rẻ nhất trong nhóm khả thi, (3) tiebreaker sau 07:00 nếu chênh < 200k. |
| 9 | **Feasibility Check** | Kiểm tra trước khi đặt vé: `total_budget - flight_price >= nights × 200,000`. Loại bỏ vé không khả thi. |
| 10 | **Dead-end Detection** | Nếu không có vé nào vượt feasibility check → thông báo ngân sách tối thiểu cần thiết và dừng, không tìm khách sạn. |

---

## Cấu Trúc Thư Mục

```
Lab4_Agent_2A202600039/
├── main.py                  # Entry point — chat loop tương tác
├── system_prompt.txt        # System prompt XML (persona, rules, format, constraints)
├── requirement.txt          # Danh sách dependencies
├── README.md
├── test_results.md          # Kết quả kiểm thử đầy đủ (tự sinh)
├── test_logs.json           # Kết quả kiểm thử dạng JSON (tự sinh)
├── src/
│   ├── agent.py             # LangGraph graph + agent_node + ToolNode
│   └── tools.py             # 3 tools: search_flights, search_hotels, calculate_budget
└── test/
    └── test_case.py         # Automated test runner → sinh test_results.md + test_logs.json
```

---

## Test Cases

### Test Cases Gốc (Lab Assignment)

| ID | Mô tả | Input | Điều kiện PASS |
|---|---|---|---|
| Test 1 | Direct Answer | "Xin chào! Tôi đang muốn đi du lịch..." | Không gọi tool, hỏi thêm thông tin |
| Test 2 | Single Tool Call | "Tìm vé từ Hà Nội đi Đà Nẵng" | Gọi `search_flights`, trả về danh sách bay |
| Test 3 | Multi-step Chaining | "HN → Phú Quốc, 2 đêm, 5 triệu" | Chuỗi 4 tools đúng thứ tự |
| Test 4 | Clarification | "Tôi muốn đặt khách sạn" | Hỏi lại city, chưa gọi tool |
| Test 5 | Guardrail | "Giải bài tập Python linked list" | Từ chối lịch sự |

### Test Cases Bổ Sung (Feature Tests)

| ID | Feature | Input | Điều kiện PASS |
|---|---|---|---|
| Test 6 | Weekend Pricing | "Tìm vé HN → Đà Nẵng vào thứ 7" | Giá tăng 20% (VietJet 890k → 1,068,000₫) |
| Test 7 | Time Preference | "Tìm vé buổi sáng HN → Đà Nẵng" | Chỉ hiển thị/ưu tiên chuyến trước 12:00 |
| Test 8 | Business Class | "Vé thương gia HN → HCM" | `flight_class='business'`, chỉ 1 kết quả |
| Test 9 | Dead-end | "HN → Phú Quốc, 3 đêm, 1.5 triệu" | Gọi `search_flights`, DỪNG — không gọi `search_hotels` |
| Test 10 | Full Plan + Buổi | "HN → Đà Nẵng, 2 đêm, 4 triệu, buổi sáng" | Chuỗi 4 tools, chọn đúng VietJet 08:30 |

> Kết quả chi tiết từng test (console log đầy đủ) xem tại [test_results.md](test_results.md).

---

## Chạy Chương Trình

**Cài dependencies:**
```bash
pip install -r requirement.txt
```

**Chat tương tác:**
```bash
python main.py
```

**Chạy toàn bộ test cases:**
```bash
python test/test_case.py
```
Kết quả được ghi tự động vào `test_results.md` và `test_logs.json`.

---

## Ví Dụ Hội Thoại

```
Bạn: Tôi ở Hà Nội muốn đi Đà Nẵng 2 đêm, budget 4 triệu, muốn đi chuyến buổi sáng

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng', ...})
[Agent] Gọi tool: calculate_budget({'total_budget': 4000000, 'expenses': 'vé_máy_bay:890000'})
[Agent] Gọi tool: search_hotels({'city': 'Đà Nẵng', 'max_price_per_night': 1555000})
[Agent] Gọi tool: calculate_budget({..., 'expenses': 'vé_máy_bay:890000,khách_sạn:2400000'})

TravelBuddy: ✈️ VietJet Air | 08:30 → 09:50 | 890,000₫
             🏨 Sala Danang Beach (4★) | Mỹ Khê | 1,200,000₫/đêm
             💰 Tổng: 3,290,000₫ | Còn lại: 710,000₫
```
