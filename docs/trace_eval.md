# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Cần hiểu nhu cầu, phân tích ngân sách và vị trí gần trường, lọc danh sách, so sánh lựa chọn rồi đề xuất phòng trọ phù hợp. |
| 🛠️ **Tool Interaction** | `4/5` | Cần kết nối công cụ tìm kiếm tin đăng, bản đồ, dữ liệu giá và lịch của sinh viên/chủ trọ để đặt lịch xem. |
| 🔀 **Dynamic Decision** | `5/5` | Kết quả tìm kiếm và tình trạng phòng trọ quyết định bước tiếp theo hoặc phương án thay thế. |
| ⏳ **Long Horizon** | `4/5` | Quy trình kéo dài qua nhiều bước từ thu thập yêu cầu, tìm và xác minh phòng trọ đến thương lượng thời gian, xác nhận và nhắc lịch. |
| **TỔNG ĐIỂM FIT** | **18/20** | **KẾT LUẬN: BÀI TOÁN RẤT PHÙ HỢP ĐỂ TRIỂN KHAI BẰNG REACT AGENT!** |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Tôi là sinh viên, cần tìm phòng trọ khép kín ở Cầu Giấy, gần trường, giá dưới 5 triệu đồng/tháng và muốn đặt lịch xem vào chiều thứ Bảy tuần này."*

### 🤖 Chatbot Baseline:
* **Phản hồi**: Chào bạn! Rất vui được hỗ trợ một bạn sinh viên năng động. 

Lời đầu tiên, mình rất tiếc phải thông báo rằng mình là trợ lý tư vấn thông tin chung nên **không thể trực tiếp tra cứu các tin đăng thực tế, kiểm tra phòng trống hay đặt lịch hẹn xem nhà cho bạn vào chiều thứ Bảy này được**. 

Tuy nhiên, với tài chính **dưới 5 triệu đồng/tháng** để tìm phòng khép kín ở **Cầu Giấy**, mình khẳng định đây là một mức ngân sách **rất hợp lý và có nhiều lựa chọn tốt** (bạn hoàn toàn có thể thuê được một căn chung cư mini đẹp, có thang máy, đầy đủ điều hòa, nóng lạnh, giường tủ).

Để chuyến đi tìm và xem phòng của bạn vào cuối tuần này hiệu quả nhất, mình xin chia sẻ một số kinh nghiệm "bỏ túi" nhé"*

* **Nhận xét**: Chỉ đưa ra hướng dẫn chung, không tìm được tin đăng cụ thể, không kiểm tra tình trạng phòng trọ và cũng không hoàn tất việc đặt lịch.

### 🧠 ReAct Agent:
* **Thought 1**: Cần tìm phòng trọ tại Cầu Giấy có giá không quá 5 triệu đồng/tháng.
* **Action 1**: `search_rentals['Cầu Giấy', 5000000, 'phòng trọ']`
* **Observation 1**: ` Tìm thấy 1 kết quả phù hợp: Mã nhà: NT001 Tên: Phòng trọ khép kín Cầu Giấy Giá: 4.500.000 VNĐ/tháng Diện tích: 25 m²  `
* **Thought 2**: Đã tìm thấy mã NT001; cần xem chi tiết và các khung giờ xem phòng.
* **Action 2**: `get_rental_details['NT001']`
* **Observation 2**: `Thông tin chi tiết nhà NT001: Tên: Phòng trọ khép kín Cầu Giấy Khu vực: Cầu Giấy, Hà Nội Địa chỉ: Ngõ 165 Cầu Giấy, Hà Nội Loại hình: phòng trọ Giá thuê: 4.500.000 VNĐ/tháng Diện tích: 25 m²Tiện ích: Điều hòa, nóng lạnh, máy giặt chung Khung giờ xem nhà: 09:00, 14:00, 18:30`
* **Thought 3**: Đã có phòng phù hợp và các giờ khả dụng, nhưng còn thiếu ngày cụ thể, họ tên và số điện thoại nên chưa được gọi book_viewing.
* **Final Answer**: *"Tôi tìm thấy phòng trọ khép kín NT001 tại Cầu Giấy, giá 4.500.000 VNĐ/tháng. Các giờ xem khả dụng là 09:00, 14:00 và 18:30. Bạn vui lòng cung cấp ngày xem cụ thể, họ tên, số điện thoại và chọn một khung giờ để tôi đặt lịch."*

* **Nhận xét**: Agent chủ động tìm kiếm và kiểm tra khung giờ xem nhà; nhưng chưa có ngày cụ thể để biết ngày nào có thể xem, Agent  dừng đúng lúc để xin người dùng cung cấp thêm thông tin khi thực hiện hành động đặt lịch.
