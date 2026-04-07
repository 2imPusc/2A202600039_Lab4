# TravelBuddy — Trợ Lý Du Lịch Thông Minh

> Lab 4 — AI Agent with LangGraph | Student ID: 2A202600039

TravelBuddy là một AI Agent tư vấn du lịch nội địa Việt Nam, được xây dựng trên nền tảng **LangGraph** (ReAct pattern) và **GPT-4o-mini**, có khả năng tìm kiếm vé máy bay, khách sạn và lập kế hoạch ngân sách theo yêu cầu người dùng.

---

## Mục Lục

- [Kiến Trúc Graph](#kiến-trúc-graph)
- [Công Cụ (Tools)](#công-cụ-tools)
- [Tính Năng](#tính-năng)
- [Thiết Kế System Prompt](#thiết-kế-system-prompt)
- [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
- [Test Cases](#test-cases)
- [Chạy Chương Trình](#chạy-chương-trình)
- [Ví Dụ Hội Thoại](#ví-dụ-hội-thoại)

---

## Kiến Trúc Graph

TravelBuddy sử dụng vòng lặp **ReAct (Reason + Act)** của LangGraph:

```
                        START
                          │
                          ▼
          ┌───────────────────────────────┐
    ┌────►│         agent_node            │  LLM (GPT-4o-mini) + System Prompt
    │     └───────────────┬───────────────┘
    │                     │
    │                     ▼ tools_condition
    │         ┌───────────┴───────────┐
    │  có tool_calls               không có tool_calls
    │         │                        │
    │         ▼                        ▼
    │ ┌───────────────┐             [END]
    │ │   ToolNode    │
    │ │────────────── │
    │ │ search_flights│
    │ │ search_hotels │
    │ │ calc_budget   │
    └─┤               │
      └───────────────┘
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

## Thiết Kế System Prompt

System prompt được viết theo cấu trúc XML với 5 khối độc lập, mỗi khối có vai trò riêng biệt:

```
┌──────────────────┬────────────────────────────────────────────────────────────┐
│ Khối             │ Vai trò                                                    │
├──────────────────┼────────────────────────────────────────────────────────────┤
│ <persona>        │ Định hình nhân cách: chuyên gia du lịch, lịch sự, trả lời │
│                  │ bằng tiếng Việt, tự nhiên — không máy móc.                │
├──────────────────┼────────────────────────────────────────────────────────────┤
│ <rules>          │ Logic nghiệp vụ cốt lõi (xem chi tiết bên dưới).          │
├──────────────────┼────────────────────────────────────────────────────────────┤
│ <tools_          │ Mô tả ngắn 3 tools để LLM biết khi nào nên dùng cái nào. │
│  instruction>    │ (Schema chi tiết do bind_tools() tự sinh — không cần lặp) │
├──────────────────┼────────────────────────────────────────────────────────────┤
│ <response_format>│ Quy định cấu trúc câu trả lời kế hoạch du lịch: 5 phần   │
│                  │ theo thứ tự (chào → vé → khách sạn → ngân sách → tips).  │
├──────────────────┼────────────────────────────────────────────────────────────┤
│ <constraints>    │ Guardrail off-topic, bảo mật prompt, xử lý edge case.     │
└──────────────────┴────────────────────────────────────────────────────────────┘
```

### Khối `<rules>` — Trung Tâm Điều Phối

Đây là phần phức tạp nhất, kiểm soát toàn bộ hành vi của agent:

**Rule 2 — WORKFLOW (4 bước bắt buộc cho full plan):**

```
Step 1: search_flights
    │
    ├─ (a) Class Filter     → economy mặc định; business nếu user yêu cầu
    │                          hoặc budget rộng & user thiên về tiện nghi
    ├─ (b) Feasibility Check (tính MENTALLY, không gọi tool)
    │       remaining = budget - flight_price
    │       viable nếu: remaining >= nights × 200,000
    │       → nếu TẤT CẢ vé đều fail → DEAD END, dừng ngay
    ├─ (c) Selection Priority
    │       1. Lọc theo buổi (sáng/chiều/tối) nếu user đề cập
    │       2. Chọn rẻ nhất trong nhóm viable
    │       3. Tiebreaker: chênh < 200k → ưu tiên chuyến sau 07:00
    └─ (e) Transparency    → luôn liệt kê các lựa chọn còn lại
         │
         ▼
Step 2: calculate_budget(budget, "vé_máy_bay:{giá}")
         │
         ▼
Step 3: search_hotels(city, max_price = remaining / nights)
         │
         ▼
Step 4: calculate_budget(budget, "vé_máy_bay:{x}, khách_sạn:{y}")
```

**Tại sao thiết kế như vậy?**

| Quyết định thiết kế | Lý do |
|---|---|
| Feasibility check ở Step 1, trước khi gọi tool tiếp theo | Tránh gọi `calculate_budget` → `search_hotels` rồi mới phát hiện ngân sách không đủ — lãng phí token và API call |
| Feasibility check làm MENTALLY (không dùng tool) | Rule 3 bắt buộc dùng `calculate_budget` để tính, nhưng nếu áp dụng ở dead-end sẽ tạo vòng lặp thừa. Ghi rõ exception để tránh xung đột rule |
| `search_hotels` nhận `max_price = remaining / nights` | Đảm bảo khách sạn trả về luôn nằm trong ngân sách còn lại, không cần lọc thêm sau |
| Tách Rule 5 CLARIFICATION thành 3 nhánh | Flight-only và hotel-only không cần đủ 4 tham số → tránh agent hỏi thừa khi user chỉ muốn xem giá vé |
| `flight_class` và `travel_date` là optional trong tìm vé đơn | Nếu không ghi rõ, LLM sẽ hỏi thêm ngày/hạng vé trước khi gọi tool, làm chậm trải nghiệm |

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
