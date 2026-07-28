"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

Đề tài 10:
Trợ lý tìm nhà trọ/căn hộ và đặt lịch xem nhà.
"""


# Dữ liệu nhà trọ/căn hộ giả lập để các tool tra cứu
RENTAL_DATA = {
    "NT001": {
        "title": "Phòng trọ khép kín Cầu Giấy",
        "location": "Cầu Giấy, Hà Nội",
        "property_type": "phòng trọ",
        "price": 4500000,
        "area": 25,
        "address": "Ngõ 165 Cầu Giấy, Hà Nội",
        "amenities": "Điều hòa, nóng lạnh, máy giặt chung",
        "viewing_times": ["09:00", "14:00", "18:30"],
    },
    "NT002": {
        "title": "Phòng studio Nam Từ Liêm",
        "location": "Nam Từ Liêm, Hà Nội",
        "property_type": "studio",
        "price": 5800000,
        "area": 30,
        "address": "Đường Phạm Văn Đồng, Nam Từ Liêm, Hà Nội",
        "amenities": "Nội thất cơ bản, thang máy, chỗ để xe",
        "viewing_times": ["10:00", "15:30", "19:00"],
    },
    "CH001": {
        "title": "Căn hộ 2 phòng ngủ Thanh Xuân",
        "location": "Thanh Xuân, Hà Nội",
        "property_type": "căn hộ",
        "price": 9500000,
        "area": 65,
        "address": "Đường Nguyễn Trãi, Thanh Xuân, Hà Nội",
        "amenities": "Đầy đủ nội thất, ban công, bảo vệ 24/7",
        "viewing_times": ["08:30", "13:30", "17:30"],
    },
}


def search_rentals(
    location: str,
    max_price: int,
    property_type: str = "tất cả"
) -> str:
    """
    Tìm nhà trọ hoặc căn hộ phù hợp với nhu cầu của người dùng.

    Args:
        location (str):
            Khu vực người dùng muốn thuê nhà.
            Ví dụ: 'Cầu Giấy', 'Thanh Xuân', 'Hà Nội'.

        max_price (int):
            Mức giá thuê tối đa mỗi tháng, tính bằng VNĐ.
            Ví dụ: 5000000.

        property_type (str):
            Loại hình nhà ở.
            Ví dụ: 'phòng trọ', 'studio', 'căn hộ'.
            Mặc định là 'tất cả'.

    Returns:
        str:
            Danh sách các nhà trọ hoặc căn hộ phù hợp.
    """
    if not location:
        return "LỖI: Khu vực tìm kiếm không được để trống."

    try:
        max_price = int(max_price)
    except (TypeError, ValueError):
        return "LỖI: Giá tối đa phải là một số nguyên."

    if max_price <= 0:
        return "LỖI: Giá tối đa phải lớn hơn 0."

    location_lower = location.lower()
    property_type_lower = property_type.lower()

    results = []

    for listing_id, listing in RENTAL_DATA.items():
        location_match = (
            location_lower in listing["location"].lower()
        )

        price_match = listing["price"] <= max_price

        type_match = (
            property_type_lower == "tất cả"
            or property_type_lower in listing["property_type"].lower()
        )

        if location_match and price_match and type_match:
            formatted_price = (
                f"{listing['price']:,}".replace(",", ".")
            )

            results.append(
                f"- Mã nhà: {listing_id}\n"
                f"  Tên: {listing['title']}\n"
                f"  Giá: {formatted_price} VNĐ/tháng\n"
                f"  Diện tích: {listing['area']} m²"
            )

    if not results:
        return (
            "KHÔNG TÌM THẤY: Chưa có nhà trọ hoặc căn hộ "
            "phù hợp với yêu cầu của bạn."
        )

    return (
        f"Tìm thấy {len(results)} kết quả phù hợp:\n\n"
        + "\n\n".join(results)
    )


def get_rental_details(listing_id: str) -> str:
    """
    Tra cứu thông tin chi tiết của một nhà trọ hoặc căn hộ.

    Args:
        listing_id (str):
            Mã nhà nhận được từ kết quả của tool search_rentals.
            Ví dụ: 'NT001', 'NT002', 'CH001'.

    Returns:
        str:
            Thông tin chi tiết của nhà trọ hoặc căn hộ,
            bao gồm địa chỉ, giá thuê, diện tích, tiện ích
            và các khung giờ có thể đến xem nhà.
    """
    if not listing_id:
        return "LỖI: Mã nhà không được để trống."

    listing_id = listing_id.upper().strip()

    if listing_id not in RENTAL_DATA:
        return (
            f"LỖI: Không tìm thấy nhà có mã '{listing_id}'."
        )

    listing = RENTAL_DATA[listing_id]

    formatted_price = (
        f"{listing['price']:,}".replace(",", ".")
    )

    return (
        f"Thông tin chi tiết nhà {listing_id}:\n"
        f"- Tên: {listing['title']}\n"
        f"- Khu vực: {listing['location']}\n"
        f"- Địa chỉ: {listing['address']}\n"
        f"- Loại hình: {listing['property_type']}\n"
        f"- Giá thuê: {formatted_price} VNĐ/tháng\n"
        f"- Diện tích: {listing['area']} m²\n"
        f"- Tiện ích: {listing['amenities']}\n"
        f"- Khung giờ xem nhà: "
        f"{', '.join(listing['viewing_times'])}"
    )


def book_viewing(
    listing_id: str,
    viewing_date: str,
    viewing_time: str,
    customer_name: str,
    phone: str
) -> str:
    """
    Đặt lịch xem một nhà trọ hoặc căn hộ.

    Args:
        listing_id (str):
            Mã nhà người dùng muốn xem.
            Ví dụ: 'NT001'.

        viewing_date (str):
            Ngày người dùng muốn xem nhà.
            Định dạng: YYYY-MM-DD.
            Ví dụ: '2026-08-01'.

        viewing_time (str):
            Khung giờ người dùng muốn xem nhà.
            Ví dụ: '09:00'.

        customer_name (str):
            Họ tên của người đăng ký xem nhà.

        phone (str):
            Số điện thoại liên hệ của người đăng ký.

    Returns:
        str:
            Thông tin xác nhận đặt lịch xem nhà.
    """
    if not listing_id:
        return "LỖI: Mã nhà không được để trống."

    listing_id = listing_id.upper().strip()

    if listing_id not in RENTAL_DATA:
        return (
            f"LỖI: Không tìm thấy nhà có mã '{listing_id}'."
        )

    if not viewing_date:
        return "LỖI: Ngày xem nhà không được để trống."

    if not viewing_time:
        return "LỖI: Giờ xem nhà không được để trống."

    if not customer_name:
        return "LỖI: Họ tên khách hàng không được để trống."

    if not phone:
        return "LỖI: Số điện thoại không được để trống."

    listing = RENTAL_DATA[listing_id]

    if viewing_time not in listing["viewing_times"]:
        return (
            f"LỖI: Khung giờ {viewing_time} không khả dụng.\n"
            f"Các khung giờ có thể chọn: "
            f"{', '.join(listing['viewing_times'])}."
        )

    booking_code = (
        f"VIEW-{listing_id}-"
        f"{viewing_date.replace('-', '')}-"
        f"{viewing_time.replace(':', '')}"
    )

    return (
        "ĐẶT LỊCH XEM NHÀ THÀNH CÔNG\n"
        f"- Mã đặt lịch: {booking_code}\n"
        f"- Nhà: {listing['title']} ({listing_id})\n"
        f"- Địa chỉ: {listing['address']}\n"
        f"- Ngày xem: {viewing_date}\n"
        f"- Giờ xem: {viewing_time}\n"
        f"- Khách hàng: {customer_name}\n"
        f"- Số điện thoại: {phone}"
    )


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "search_rentals": search_rentals,
    "get_rental_details": get_rental_details,
    "book_viewing": book_viewing,
}