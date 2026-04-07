from langchain_core.tools import tool

# --- MOCK DATA: Dữ liệu giả lập hệ thống du lịch ---
# Lưu ý kỹ thuật: 
# 1. Giá vé máy bay có sự khác biệt giữa các hãng và hạng ghế.
# 2. Khách sạn được phân loại theo số sao và khu vực để Agent dễ tư vấn.

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1450000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2800000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1200000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1350000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1100000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1600000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1300000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3200000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1300000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1800000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1200000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3500000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1500000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2800000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1400000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180000, "area": "Quận 1", "rating": 4.6},
    ],
}

def _is_weekend(travel_date: str) -> bool:
    """Kiểm tra travel_date có phải cuối tuần không (thứ 7, chủ nhật)."""
    from datetime import datetime
    text = travel_date.lower()

    # Từ khóa tự nhiên
    weekend_keywords = ["cuối tuần", "thứ 7", "thứ bảy", "chủ nhật", "saturday", "sunday", "weekend"]
    if any(kw in text for kw in weekend_keywords):
        return True

    # Thử parse định dạng ngày ISO (YYYY-MM-DD) hoặc DD/MM/YYYY
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(travel_date.strip(), fmt).weekday() >= 5
        except ValueError:
            continue

    return False


@tool
def search_flights(origin: str, destination: str, travel_date: str = "", flight_class: str = "") -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: Thành phố khởi hành (VD: 'Hà Nội')
    - destination: Thành phố đến (VD: 'Đà Nẵng')
    - travel_date: Ngày đi (VD: '2026-04-12', 'cuối tuần', 'thứ 7'). Để trống nếu không rõ.
    - flight_class: Hạng vé ('economy' hoặc 'business'). Để trống để xem tất cả hạng.
    Lưu ý: Giá vé cuối tuần (thứ 7, chủ nhật) tăng 20% so với ngày thường.
    """
    try:
        # Thử tra cứu theo chiều thuận
        flights = FLIGHTS_DB.get((origin, destination))

        # Nếu không thấy, thử tra cứu theo chiều ngược
        is_reversed = False
        if not flights:
            flights = FLIGHTS_DB.get((destination, origin))
            is_reversed = True

        if not flights:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."

        # Lọc theo hạng vé nếu được chỉ định
        if flight_class:
            flights = [f for f in flights if f['class'] == flight_class.lower()]
            if not flights:
                return f"Không có chuyến bay hạng '{flight_class}' từ {origin} đến {destination}."

        # Áp dụng phụ phí cuối tuần +20%
        weekend = _is_weekend(travel_date) if travel_date else False
        surcharge_note = " [Giá cuối tuần, đã tăng 20%]" if weekend else ""
        class_note = f" [Hạng {flight_class.upper()}]" if flight_class else ""

        res = [f"Danh sách chuyến bay {'(chiều ngược lại)' if is_reversed else ''}{class_note}{surcharge_note}:"]
        for f in flights:
            price = int(f['price'] * 1.2) if weekend else f['price']
            res.append(
                f"- {f['airline']} ({f['class']}): {f['departure']} -> {f['arrival']} | Giá: {price:,}₫"
            )

        return "\n".join(res)
    except Exception as e:
        return f"Lỗi khi tìm chuyến bay từ {origin} đến {destination}: {str(e)}"


@tool
def search_hotels(city: str, max_price_per_night: int = 999_999_999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: Tên thành phố (VD: 'Phú Quốc')
    - max_price_per_night: Giá tối đa (VNĐ)
    """
    try:
        hotels = HOTELS_DB.get(city, [])

        # Lọc theo giá và sắp xếp theo rating giảm dần
        filtered_hotels = [h for h in hotels if h['price_per_night'] <= max_price_per_night]
        sorted_hotels = sorted(filtered_hotels, key=lambda x: x['rating'], reverse=True)

        if not sorted_hotels:
            return f"Không tìm thấy khách sạn tại {city} với giá dưới {max_price_per_night:,}₫/đêm."

        res = [f"Khách sạn phù hợp tại {city} (Ưu tiên đánh giá cao):"]
        for h in sorted_hotels:
            res.append(f"- {h['name']} ({h['stars']}*): {h['price_per_night']:,}₫/đêm | Khu vực: {h['area']} | Rating: {h['rating']}")

        return "\n".join(res)
    except Exception as e:
        return f"Lỗi khi tìm khách sạn tại {city}: {str(e)}"


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại.
    Tham số:
    - total_budget: Tổng ngân sách ban đầu (VNĐ)
    - expenses: Chuỗi định dạng 'tên: số tiền, tên: số tiền'
    """
    try:
        # Parse chuỗi expenses thành dictionary
        expense_items = {}
        parts = expenses.split(',')
        for part in parts:
            if ':' in part:
                name, amount = part.split(':')
                clean = ''.join(c for c in amount if c.isdigit())
                expense_items[name.strip()] = int(clean)

        total_spent = sum(expense_items.values())
        remaining = total_budget - total_spent
        
        # Tạo bảng chi tiết
        report = ["--- BẢNG CHI PHÍ CHI TIẾT ---"]
        for name, amount in expense_items.items():
            report.append(f"- {name.capitalize()}: {amount:,}₫")
        
        report.append(f"Tổng chi: {total_spent:,}₫")
        report.append(f"Ngân sách ban đầu: {total_budget:,}₫")
        report.append(f"CÒN LẠI: {remaining:,}₫")

        if remaining < 0:
            report.append(f"⚠️ CẢNH BÁO: Vượt ngân sách {abs(remaining):,}₫! Cần điều chỉnh.")
        
        return "\n".join(report)
    except Exception as e:
        return f"Lỗi định dạng expenses: {str(e)}. Vui lòng nhập theo dạng 'mục_chi: số_tiền'."