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
* **Phản hồi**: *"Bạn có thể tìm phòng trọ tại Cầu Giấy trên các trang đăng tin, lọc mức giá dưới 5 triệu đồng rồi liên hệ chủ trọ để đặt lịch xem."*
* **Nhận xét**: Chỉ đưa ra hướng dẫn chung, không tìm được tin đăng cụ thể, không kiểm tra tình trạng phòng trọ và cũng không hoàn tất việc đặt lịch.

### 🧠 ReAct Agent:
* **Thought 1**: Cần chuẩn hóa các tiêu chí gồm phòng trọ khép kín tại Cầu Giấy, gần trường, giá tối đa 5 triệu đồng/tháng và thời gian xem vào chiều thứ Bảy.
* **Action 1**: `search_rooms(location='Cầu Giấy', room_type='khép kín', near_school=true, max_price=5000000)`
* **Observation 1**: `Tìm thấy 3 phòng phù hợp; phòng PT-CG-102 cách trường 700 m, giá 3,9 triệu đồng/tháng, hiện còn trống và đáp ứng đầy đủ tiêu chí.`
* **Thought 2**: Cần kiểm tra khung giờ xem phòng PT-CG-102 vào chiều thứ Bảy trước khi đặt lịch.
* **Action 2**: `check_viewing_slots(listing_id='PT-CG-102', date='thứ Bảy tuần này', period='buổi chiều')`
* **Observation 2**: `Còn hai khung giờ: 14:00 và 16:30.`
* **Thought 3**: Chưa có lựa chọn giờ cụ thể của người dùng nên cần đề xuất các khung giờ còn trống, không tự ý đặt lịch.
* **Final Answer**: *"Tôi tìm thấy phòng trọ khép kín PT-CG-102 tại Cầu Giấy, cách trường khoảng 700 m, giá 3,9 triệu đồng/tháng và hiện còn trống. Chủ trọ có thể tiếp bạn lúc 14:00 hoặc 16:30 vào thứ Bảy tuần này. Bạn muốn chọn khung giờ nào để tôi xác nhận lịch xem?"*
* **Nhận xét**: Agent chủ động tìm kiếm và kiểm tra lịch bằng công cụ, đồng thời dừng đúng lúc để xin người dùng chọn giờ trước khi thực hiện hành động đặt lịch.
