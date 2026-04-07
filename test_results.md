# TravelBuddy — Kết Quả Kiểm Thử

**Ngày chạy:** 2026-04-07 16:38:57
**Tổng số test:** 10 (5 base + 5 implement) | **PASS:** 10 | **REVIEW:** 0

---

## Test 1 — Direct Answer (Không cần tool)

**Expectation:** Chào hỏi, hỏi thêm thông tin, không gọi tool.

**Tools used:** _(không gọi tool)_

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.

TravelBuddy đang suy nghĩ...
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Xin chào! Rất vui được hỗ trợ bạn trong việc lên kế hoạch du lịch. Bạn có thể cho tôi biết một số thông tin như điểm khởi hành, ngân sách, số đêm dự kiến và nếu bạn có ý tưởng về điểm đến nào không? Điều này sẽ giúp tôi tìm kiếm những lựa chọn phù hợp nhất cho bạn.
```

---

## Test 2 — Single Tool Call

**Expectation:** Gọi search_flights, liệt kê 4 chuyến bay.

**Tools used:** `search_flights`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Dưới đây là danh sách các chuyến bay từ Hà Nội đi Đà Nẵng:

1. **Vietnam Airlines**
   - Hạng vé: Phổ thông
   - Thời gian: 06:00 -> 07:20
   - Giá: 1,450,000₫

2. **Vietnam Airlines**
   - Hạng vé: Thương gia
   - Thời gian: 14:00 -> 15:20
   - Giá: 2,800,000₫

3. **VietJet Air**
   - Hạng vé: Phổ thông
   - Thời gian: 08:30 -> 09:50
   - Giá: 890,000₫

4. **Bamboo Airways**
   - Hạng vé: Phổ thông
   - Thời gian: 11:00 -> 12:20
   - Giá: 1,200,000₫

Nếu bạn cần thêm thông tin hoặc muốn đặt chuyến bay nào, hãy cho tôi biết!
```

---

## Test 3 — Multi-Step Tool Chaining

**Expectation:** Chuỗi: Flight -> Budget -> Hotel -> Tổng hợp.

**Tools used:** `search_flights`, `calculate_budget`, `search_hotels`, `calculate_budget`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc', 'travel_date': '', 'flight_class': ''})
[Agent] Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:1100000'})
[Agent] Gọi tool: search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 1950000})
[Agent] Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé_máy_bay:1100000,khách_sạn:1600000'})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Chào bạn! Dưới đây là kế hoạch du lịch của bạn từ Hà Nội đến Phú Quốc trong 2 đêm với ngân sách 5 triệu đồng:

### Chi tiết chuyến bay:
- **Hãng hàng không**: VietJet Air
- **Thời gian**: 16:00 -> 18:15
- **Giá vé**: 1,100,000₫

### Khách sạn gợi ý:
- **Tên**: Lahana Resort
- **Sao**: 3*
- **Khu vực**: Dương Đông
- **Đánh giá**: 4.0
- **Giá**: 800,000₫/đêm
- **Tổng chi phí cho 2 đêm**: 1,600,000₫

### Bảng chi phí chi tiết:
| Mục chi phí       | Số tiền (₫)   |
|-------------------|----------------|
| Vé máy bay        | 1,100,000      |
| Khách sạn         | 1,600,000      |
| **Tổng chi**      | **2,700,000**  |
| Ngân sách ban đầu | 5,000,000      |
| **Còn lại**       | **2,300,000**  |

### Một số gợi ý du lịch:
- Bạn có thể tham quan các bãi biển nổi tiếng như Bãi Sao, Bãi Trường.
- Đừng quên thưởng thức hải sản tươi ngon tại các nhà hàng địa phương.
- Nếu có thời gian, hãy thử tham gia các hoạt động thể thao dưới nước như lặn biển hay lướt ván.

Nếu bạn cần thêm thông tin hoặc muốn thay đổi kế hoạch, hãy cho tôi biết nhé!
```

---

## Test 4 — Clarification

**Expectation:** Hỏi lại thông tin thiếu, chưa gọi tool ngay.

**Tools used:** _(không gọi tool)_

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tôi muốn đặt khách sạn

TravelBuddy đang suy nghĩ...
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Xin vui lòng cho tôi biết tên thành phố mà bạn muốn đặt khách sạn, và nếu có, bạn có thể cung cấp mức giá tối đa mỗi đêm mà bạn dự định chi tiêu không?
```

---

## Test 5 — Guardrail / Refusal

**Expectation:** Từ chối lịch sự, chỉ hỗ trợ du lịch.

**Tools used:** _(không gọi tool)_

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Giải giúp tôi bài tập lập trình Python về linked list

TravelBuddy đang suy nghĩ...
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Xin lỗi, nhưng tôi không thể giúp bạn với bài tập lập trình. Tuy nhiên, nếu bạn cần thông tin về du lịch hoặc lên kế hoạch cho chuyến đi, tôi rất sẵn lòng hỗ trợ!
```

---

## Test 6 — Weekend Pricing (+20%)

**Expectation:** Gọi search_flights với travel_date='thứ 7', giá vé tăng 20% so với ngày thường (VD: VietJet 890k → 1,068,000₫).

**Tools used:** `search_flights`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tìm vé từ Hà Nội đi Đà Nẵng vào thứ 7

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng', 'travel_date': 'thứ 7'})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Dưới đây là danh sách các chuyến bay từ Hà Nội đi Đà Nẵng vào thứ 7:

1. **Vietnam Airlines (phổ thông)**:
   - Thời gian: 06:00 -> 07:20
   - Giá: 1,740,000₫

2. **Vietnam Airlines (thương gia)**:
   - Thời gian: 14:00 -> 15:20
   - Giá: 3,360,000₫

3. **VietJet Air (phổ thông)**:
   - Thời gian: 08:30 -> 09:50
   - Giá: 1,068,000₫

4. **Bamboo Airways (phổ thông)**:
   - Thời gian: 11:00 -> 12:20
   - Giá: 1,440,000₫

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho tôi biết!
```

---

## Test 7 — Time Preference (không cần ngày)

**Expectation:** Gọi search_flights, chỉ liệt kê/ưu tiên các chuyến trước 12:00 (06:00, 08:30, 11:00), chọn rẻ nhất là VietJet 08:30.

**Tools used:** `search_flights`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tìm vé buổi sáng từ Hà Nội đi Đà Nẵng

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng', 'travel_date': '', 'flight_class': ''})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Dưới đây là danh sách các chuyến bay buổi sáng từ Hà Nội đi Đà Nẵng:

1. **Vietnam Airlines**
   - Thời gian: 06:00 -> 07:20
   - Giá: 1,450,000₫

2. **VietJet Air**
   - Thời gian: 08:30 -> 09:50
   - Giá: 890,000₫

3. **Bamboo Airways**
   - Thời gian: 11:00 -> 12:20
   - Giá: 1,200,000₫

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho tôi biết!
```

---

## Test 8 — Business Class Filter

**Expectation:** Gọi search_flights với flight_class='business', chỉ trả về đúng 1 chuyến Vietnam Airlines 18:00 giá 3,200,000₫.

**Tools used:** `search_flights`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tìm vé hạng thương gia từ Hà Nội đi Hồ Chí Minh

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Hồ Chí Minh', 'flight_class': 'business'})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Tôi đã tìm thấy chuyến bay hạng thương gia từ Hà Nội đi Hồ Chí Minh như sau:

- **Hãng hàng không**: Vietnam Airlines
- **Thời gian**: 18:00 -> 20:10
- **Giá**: 3,200,000₫

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho tôi biết nhé!
```

---

## Test 9 — Dead-end Detection (budget quá thấp)

**Expectation:** Gọi search_flights, phát hiện không có vé khả thi (rẻ nhất 1.1M + 3×200k = 1.7M > 1.5M), thông báo ngân sách tối thiểu cần thiết và DỪNG, không gọi search_hotels.

**Tools used:** `search_flights`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tôi ở Hà Nội muốn đi Phú Quốc 3 đêm, budget 1.5 triệu. Tư vấn giúp!

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc', 'travel_date': '', 'flight_class': ''})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Chào bạn! Dưới đây là thông tin chuyến bay từ Hà Nội đến Phú Quốc cho kế hoạch của bạn:

### Chi tiết chuyến bay:
1. **Hãng hàng không**: VietJet Air
   - **Thời gian**: 16:00 -> 18:15
   - **Giá**: 1,100,000₫

### Tính toán ngân sách:
- **Tổng ngân sách**: 1,500,000₫
- **Giá vé máy bay**: 1,100,000₫
- **Ngân sách còn lại cho khách sạn**: 1,500,000₫ - 1,100,000₫ = 400,000₫
- **Chi phí tối thiểu cho khách sạn (3 đêm)**: 3 × 200,000₫ = 600,000₫

Với ngân sách hiện tại, bạn sẽ cần ít nhất 1,700,000₫ (1,100,000₫ + 600,000₫) để có thể thực hiện chuyến đi này. Do đó, kế hoạch này không khả thi với ngân sách 1,500,000₫.

Nếu bạn muốn, tôi có thể giúp bạn tìm kiếm các chuyến bay khác hoặc điều chỉnh kế hoạch để phù hợp hơn với ngân sách của bạn. Bạn có muốn thử không?
```

---

## Test 10 — Full Plan + Time Preference kết hợp

**Expectation:** Chuỗi đầy đủ: search_flights (lọc sáng, chọn VietJet 08:30 890k) -> calculate_budget -> search_hotels -> calculate_budget tổng hợp.

**Tools used:** `search_flights`, `calculate_budget`, `search_hotels`, `calculate_budget`

**Status:** ✅ PASS

**Console Log:**

```
Bạn: Tôi ở Hà Nội muốn đi Đà Nẵng 2 đêm, budget 4 triệu, muốn đi chuyến buổi sáng

TravelBuddy đang suy nghĩ...
[Agent] Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng', 'travel_date': '', 'flight_class': ''})
[Agent] Gọi tool: calculate_budget({'total_budget': 4000000, 'expenses': 'vé_máy_bay:890000₫'})
[Agent] Gọi tool: calculate_budget({'total_budget': 4000000, 'expenses': 'vé_máy_bay:1450000₫'})
[Agent] Gọi tool: search_hotels({'city': 'Đà Nẵng', 'max_price_per_night': 1555000})
[Agent] Gọi tool: calculate_budget({'total_budget': 4000000, 'expenses': 'vé_máy_bay:890000₫,khách_sạn:500000₫'})
[Agent] Trả lời trực tiếp cho khách hàng.

TravelBuddy: Chào bạn! Dưới đây là kế hoạch chuyến đi của bạn từ Hà Nội đến Đà Nẵng trong 2 đêm với ngân sách 4 triệu đồng:

### Chi tiết chuyến bay:
- **Hãng hàng không**: VietJet Air
- **Thời gian**: 08:30 -> 09:50
- **Giá vé**: 890,000₫

### Khách sạn gợi ý:
- **Tên**: Memory Hostel
- **Sao**: 2*
- **Khu vực**: Hải Châu
- **Đánh giá**: 4.6
- **Giá**: 250,000₫/đêm

### Bảng chi phí chi tiết:
| Mục chi phí       | Số tiền      |
|-------------------|--------------|
| Vé máy bay        | 890,000₫    |
| Khách sạn (2 đêm) | 500,000₫    |
| **Tổng chi**      | **1,390,000₫** |
| **Ngân sách ban đầu** | **4,000,000₫** |
| **Còn lại**       | **2,610,000₫** |

### Một số gợi ý du lịch:
- Đà Nẵng nổi tiếng với bãi biển Mỹ Khê, bạn có thể dành thời gian thư giãn tại đây.
- Tham quan cầu Rồng và thưởng thức ẩm thực địa phương tại các quán ăn ven biển.

Nếu bạn cần thêm thông tin hoặc muốn thay đổi kế hoạch, hãy cho tôi biết nhé!
```

---
