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

## 💬 2. LOG CHATBOT BASELINE — 5 TEST CASES (Mốc 2)

Chạy thật với `LLM_PROVIDER=gemini`, không có tool. Phân loại: ✅ Correct / 🟡 Safe Fallback / 🔴 Hallucinated.

| # | Câu hỏi | Tóm tắt phản hồi Chatbot Baseline | Phân loại |
| :-: | :--- | :--- | :-: |
| 1 | Sinh viên cần lưu ý gì khi ký hợp đồng thuê phòng trọ? | Liệt kê đầy đủ, đúng kiến thức chung (xác minh chủ nhà, tiền cọc, chi phí điện nước, thời hạn hợp đồng...). | ✅ Correct |
| 2 | Nêu 3 tiêu chí quan trọng khi chọn phòng trọ cho sinh viên. | Trả lời đúng 3 tiêu chí (vị trí, chi phí, an ninh) + **tự giác nói rõ "không thể tra cứu tin đăng phòng trống thực tế"**. | ✅ Correct |
| 3 | Tìm phòng khép kín Cầu Giấy, dưới 5tr, xem chiều thứ Bảy. | Từ chối tra cứu/đặt lịch thật, chỉ đưa mẹo tìm phòng chung chung (kênh Facebook, khu vực gợi ý...). **Không bịa ra tin đăng cụ thể nào.** | 🟡 Safe Fallback |
| 4 | Tìm phòng Cầu Giấy dưới 5tr, xem chi tiết, đặt lịch 14:00 ngày 2026-08-01 cho Nguyễn An. | Từ chối đặt lịch thật, chỉ tư vấn mặt bằng giá + kinh nghiệm chung. **Không tự bịa mã phòng, không xác nhận đã đặt lịch.** | 🟡 Safe Fallback |
| 5 | Ngân sách -1 triệu, đặt lịch mã phòng KHONGTONTAI. | Tự nhận ra ngân sách âm là "nhầm lẫn vui", từ chối xử lý mã phòng không có thật, chỉ đưa mặt bằng giá tham khảo. | 🟡 Safe Fallback |

**Nhận xét Mốc 2**: Baseline **không hề hallucinate** trong 5 lần chạy thật (khác lo ngại ban đầu) — mô hình Gemini tự nhận thức giới hạn khá tốt. Điểm yếu thực sự của Baseline không phải là bịa đặt, mà là **không có khả năng hành động**: không tìm được tin đăng thật, không xác nhận đặt lịch thật, dù người dùng cung cấp đủ thông tin (Test #4). Đây chính là bằng chứng "Agentic Fit" — bài toán cần Agent có Tool thật, không chỉ cần Chatbot trả lời hay hơn.

---

## 🧠 3. TRACE REACT AGENT — 5 TEST CASES (Mốc 3)

Chạy thật, Agent tự gọi LLM sinh `Thought → Action`, hệ thống thực thi tool thật trong `tools.py` và chèn `Observation` thật (không phải do LLM tự bịa).

### Test #1 — Đơn giản
```
Thought: Đây là câu hỏi tư vấn chung, không cần tool.
Final Answer: [liệt kê đầy đủ lưu ý hợp đồng thuê trọ]
```
→ Agent tự nhận biết **không cần gọi tool** cho câu hỏi lý thuyết, trả lời ngay ở Step 1/N — đúng tinh thần "đừng vội dùng Agent cho việc không cần Agent".

### Test #2 — Đơn giản
```
Thought: Câu hỏi tư vấn chung, không cần tool.
Final Answer: [3 tiêu chí: vị trí, chi phí, an ninh]
```
→ Tương tự Test #1, dừng đúng ở Step 1.

### Test #3 — Multi-step (cần Tool)
```
Thought: Cần tìm phòng trọ khép kín Cầu Giấy giá dưới 5tr, dùng search_rentals.
Action: search_rentals[Cầu Giấy, 5000000, phòng trọ khép kín]
Observation: KHÔNG TÌM THẤY: Chưa có nhà trọ hoặc căn hộ phù hợp với yêu cầu của bạn.

Thought: "phòng trọ khép kín" quá hẹp so với property_type dữ liệu, thử lại với "phòng trọ".
Action: search_rentals[Cầu Giấy, 5000000, phòng trọ]
Observation: Tìm thấy 1 kết quả phù hợp: Mã nhà NT001, giá 4.500.000 VNĐ/tháng, 25m²

Thought: Đã có mã NT001, cần xem chi tiết + khung giờ xem.
Action: get_rental_details[NT001]
Observation: [chi tiết đầy đủ] Khung giờ xem nhà: 09:00, 14:00, 18:30
```
→ **Agent tự phục hồi lỗi** (search quá hẹp → tự nới rộng tham số ở lượt sau) mà không cần con người can thiệp — đúng hành vi mong đợi của guardrail "thử lại tham số hợp lý" đã viết trong `REACT_SYSTEM_PROMPT`.

### Test #4 — Multi-step (2 Tools + hành động thật)
```
Thought: Cần tìm phòng Cầu Giấy dưới 5tr trước.
Action: search_rentals[Cầu Giấy, 5000000, phòng trọ]
Observation: Tìm thấy 1 kết quả phù hợp: Mã nhà NT001, giá 4.500.000 VNĐ/tháng

Thought: Đã có mã NT001, xem chi tiết + khung giờ.
Action: get_rental_details[NT001]
Observation: [chi tiết đầy đủ] Khung giờ xem nhà: 09:00, 14:00, 18:30

Thought: 14:00 hợp lệ, đủ thông tin khách hàng, tiến hành đặt lịch.
Action: book_viewing[NT001, 2026-08-01, 14:00, Nguyễn An, 0912345678]
Observation: ĐẶT LỊCH XEM NHÀ THÀNH CÔNG
- Mã đặt lịch: VIEW-NT001-20260801-1400
```
→ Agent gọi **đúng cả 3 tool theo đúng thứ tự**, đặt lịch **thành công thật** trong hệ thống. Đây là bằng chứng rõ nhất cho thấy ReAct Agent có khả năng **hành động** mà Chatbot Baseline (Test #4 ở mục 2) hoàn toàn không làm được.

### Test #5 — Edge Case (Bẫy Guardrail)
```
Thought: Ngân sách -1 triệu đồng không hợp lệ (phải lớn hơn 0). Cần hỏi lại người dùng.
Final Answer: Ngân sách bạn đưa ra là -1 triệu đồng, đây là mức ngân sách không hợp lệ...
```
→ Agent **không hề gọi tool với tham số bẩn**, tự nhận diện input vô lý ngay ở Thought và dừng an toàn trong 1 bước — Guardrail hoạt động đúng như thiết kế, không cần chạm tới `MAX_ITERATIONS`.

---

## 🔧 4. FAILED TRACE → AGENT V2 (Root Cause Analysis)

### 🔴 Lỗi phát hiện được (Before)
Ở lần chạy đầu tiên với `MAX_ITERATIONS = 3`, **Test #4 thực thi hoàn toàn đúng và đặt lịch thành công** (xem trace ở mục 3), nhưng vì mỗi lần gọi tool tốn đúng 1 lượt, Agent dùng hết cả 3 lượt cho 3 Action (`search_rentals` → `get_rental_details` → `book_viewing`) mà **không còn lượt nào để phát biểu `Final Answer`**. Hệ quả: code cũ in ra:

```
🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa 3 bước. Ngắt lặp an toàn!
🏁 Final Answer (fallback): Xin lỗi, tôi chưa thể hoàn tất yêu cầu này...
```

**Mâu thuẫn nghiêm trọng**: hệ thống vừa in "ĐẶT LỊCH XEM NHÀ THÀNH CÔNG — Mã đặt lịch: VIEW-NT001-..." ở Observation ngay phía trên, nhưng dòng cuối lại nói "xin lỗi, chưa hoàn tất" — gây hiểu lầm cho người dùng thật.

**Root Cause**: `MAX_ITERATIONS = 3` chỉ đủ cho 3 lượt suy luận, nhưng một luồng hợp lệ cần tối thiểu **N Action + 1 Final Answer**. Với bài toán cần chuỗi 3 tool (search → details → book), 3 lượt là không đủ — đây là lỗi cấu hình Guardrail quá chặt, không phải lỗi suy luận của Agent.

### ✅ Bản vá Agent V2 (After)
1. **`MAX_ITERATIONS`: 3 → 5** (`src/prompts.py`) — đủ chỗ cho chuỗi 3 tool + 1 lần tự phục hồi (như Test #3) + 1 Final Answer, vẫn chặn được lặp vô tận.
2. **`REACT_SYSTEM_PROMPT`** bổ sung quy tắc: dùng `property_type` tổng quát khi gọi `search_rentals` (tránh lặp lại nguyên văn mô tả dài của người dùng như "khép kín" khiến tìm kiếm quá hẹp — chính là nguyên nhân lượt 1 của Test #3 bị `KHÔNG TÌM THẤY` oan).
3. **`src/app.py`** — khi Guardrail chạm giới hạn, không còn in cứng một câu "xin lỗi" vô điều kiện. Hệ thống kiểm tra `Observation` cuối cùng: nếu là kết quả thành công (không bắt đầu bằng `LỖI:`/`KHÔNG TÌM THẤY:`), Final Answer fallback sẽ **dùng chính Observation đó** thay vì phủ nhận nó.

### ⚠️ Giới hạn khi kiểm chứng (điều cần biết trước ngày demo)
Khi chạy lại để xác nhận bản vá, gói **Gemini API Free Tier bị chặn giữa chừng do chạm quota `20 request/ngày`** cho model (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`) — đây là giới hạn từ phía Google, không phải lỗi code. Bằng chứng đã xác nhận được sau bản vá trước khi hết quota:
- Test #1 chạy sạch hoàn toàn với `MAX_ITERATIONS=5`, hành vi không đổi so với trước (không cần tool vẫn dừng đúng ở Step 1).
- Test #3: khi bị rate-limit làm hao lượt, Agent vẫn kịp lấy được `get_rental_details` thật, và **Final Answer fallback mới đã in đúng dữ liệu thật thu được** thay vì một câu xin lỗi vô căn cứ — xác nhận bản vá #3 ở trên hoạt động đúng như thiết kế.
- Chưa kịp xác nhận lại toàn bộ Test #4 tới bước `book_viewing` thành công dưới `MAX_ITERATIONS=5` bằng Gemini thật do hết quota giữa chừng.
- **Đã xác nhận bù bằng `LLM_PROVIDER=mock`** (chạy offline, không tốn quota): Test #4 hoàn tất **trọn vẹn** cả chuỗi `search_rentals → get_rental_details → book_viewing` (đặt lịch thành công, mã `VIEW-NT001-20260801-1400`) **và** phát biểu đúng `Final Answer` ở Step 4/5 — không còn bị Guardrail cắt ngang oan như bản trước vá. Vẫn nên chạy lại 1 lần bằng Gemini thật khi quota reset để có bằng chứng bằng LLM thật, nhưng logic đã được xác nhận đúng.

🚨 **Rủi ro quan trọng cho Mốc 4 (Cross-Audit)**: quota 20 request/ngày rất dễ cạn chỉ sau vài lượt demo + bị nhóm khác "tấn công". Khuyến nghị: tạo sẵn 1 API key/project Gemini riêng, chưa dùng để test, dành riêng cho ngày trình bày; hoặc dùng `LLM_PROVIDER=mock` khi tập dượt để không tốn quota thật.
